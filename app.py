from flask import Flask, request, send_file, make_response, jsonify
from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

import json
import sys
sys.path.append("../")
from API_Database import retrieve_indivijual, retrieve_credit, retrieve_register_entry
from API_Database import insert_individual, retrieve_all, retrieve_from_id
from API_Database import edit_individual, delete_entry, retrieve_memo_entry
from API_Database import update_register_entry, update_memo_entry
from Entities import RegisterEntry, MemoEntry
from Reports import report_select
from Legacy_Data import add_party, add_suppliers

# Crate flask app
app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "NHYd198vQNOBa9HrIAGEGNYrKHBegc9Z"  # Change this!
jwt = JWTManager(app)

BASE = ""

## Authentication Request
@app.route(BASE + '/token', methods=["POST"])
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    ## Check if the username and password is valid
    if username != "admin" or password != "admin5555":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route(BASE + '/supplier_names_and_ids', methods=['GET'])
def get_all_supplier_names():
    data = retrieve_indivijual.get_all_names_ids('supplier')
    json_data = json.dumps(data)
    return json_data

@app.route(BASE + '/party_names_and_ids', methods=['GET'])
def get_all_party_names():
    data = retrieve_indivijual.get_all_names_ids('party')
    json_data = json.dumps(data)
    return json_data

@app.route(BASE + '/bank_names_and_ids', methods=['GET'])
def get_all_bank_names():
    data = retrieve_indivijual.get_all_names_ids('bank')
    json_data = json.dumps(data)
    return json_data

@app.route(BASE + '/credit/<int:supplier_id>/<int:party_id>', methods=['GET'])
def get_credit(supplier_id: int, party_id: int):
    data = retrieve_credit.get_pending_part(supplier_id, party_id)
    json_data = json.dumps(data)
    return json_data

@app.route(BASE + '/pending_bills/<int:supplier_id>/<int:party_id>', methods=['GET'])
def get_pending_bills(supplier_id: int, party_id: int):
    data = retrieve_register_entry.get_pending_bill_numbers(supplier_id, party_id)
    json_data = json.dumps(data)
    return json_data

@app.route(BASE + '/add/register_entry/<int:bill>/<int:amount>/<string:supplier>/<string:party>/<string:date>', methods=['GET'])
def add_register_entry(bill: int, amount: int, supplier: str, party: str,  date: str):
    return RegisterEntry.create(bill, amount, json.loads(supplier), json.loads(party), date)

@app.route(BASE + '/create_report', methods=['POST'])
def create_report():
    if request.method == "POST":
        data = request.json
        supplier_id = [element["id"] for element in json.loads(data["suppliers"])]
        party_id = [element["id"] for element in json.loads(data["parties"])]
        report = data['report']
        start = data['from']
        end = data['to']
        report_select.make_report(report, supplier_id, party_id, start, end)
        pdealer_df, name= report_select.make_report(report, supplier_id, party_id, start, end)
        response = make_response(pdealer_df.getvalue())
        response.headers['Content-Disposition'] = "attachment; filename='sakulaci.pdealer_df"
        response.mimetype = 'application/pdealer_df'
        return response
    return {"status":"okay"}

@app.route(BASE + '/add/individual/<string:type>/<string:name>/<string:phone>/<string:address>')
def add_individual(type: str, name: str, phone:str, address:str):
    insert_individual.add_individual(type, name, address)
    return {"status":"okay"}

@app.route(BASE + '/add/memo_entry/<string:obj>')
def add_memo_entry(obj: str):
    obj = json.loads(obj)
    # check if obj contains the key "memo_gr_amount"
    if "memo_gr_amount" in obj:
        # create a new version of obj (keep all old properties) but "amount" is replaced by memo_gr_amount and "memo_type" is set to "gr"
        gr_obj = {**obj, "amount": obj["memo_gr_amount"], "memo_type": "Goods Return"}
        # allowing duplicate memo_number for the second iteration of memo_entry
        obj = {**obj, "allow_duplicate_memo_number": True}
        gr_return = MemoEntry.call(gr_obj)
        if gr_return["status"] == "error":
            return gr_return
    return MemoEntry.call(obj)

@app.route(BASE + '/add_legacy')
def add_legacy():
    add_suppliers.add()
    add_party.add()
    
    return {"status": "okay"}
    
@app.route(BASE + '/get_all/<string:table_name>')
def all(table_name: str):
    data = retrieve_all.get_all(table_name)
    return json.dumps(data)

@app.route(BASE + '/get_by_id/<string:table_name>/<int:id>')
def get_id(table_name: str, id: int):
    data = retrieve_from_id.get_from_id(table_name, id)
    return json.dumps(data)

@app.route(BASE + '/update/<string:table_name>', methods=['POST'])
def update_id(table_name: str):
    if request.method == 'POST':
        data = request.json
        if table_name == "register_entry":
            re = RegisterEntry.create_instance(data)
            return update_register_entry.update_register_entry_by_id(re, int(data["id"]))
        elif table_name == "memo_entry":
            return update_memo_entry.update_memo_entry_from_obj(data)
        else:
            return edit_individual.edit_individual(data, table_name)

@app.route(BASE + '/delete/<string:table_name>', methods=['POST'])
def delete_id(table_name: str):
    if request.method == 'POST':
        data = request.json
        return delete_entry.delete_entry(data, table_name)
    
    return {"status": "okay"}

@app.route(BASE + '/get_memo_bills/<int:id>')
def get_memo_bills(id: int):
    data = retrieve_memo_entry.get_memo_bills_by_id(id)
    return json.dumps(data)


@app.route(BASE + '/fix_problems')
def fix():
    update_register_entry.fix_problems()
    return {"status" : "okay"}

if __name__ == '__main__':
    app.run(debug=True)
