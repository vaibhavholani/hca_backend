from flask import Flask, request
import json
import sys
sys.path.append("../")
from API_Database import retrieve_indivijual, retrieve_credit, retrieve_register_entry
from API_Database import insert_individual
from Entities import RegisterEntry, MemoEntry
from Reports import report_select
from Legacy_Data import add_party, add_suppliers

app = Flask(__name__)

@app.route('/supplier_names_and_ids', methods=['GET'])
def get_all_supplier_names():
    data = retrieve_indivijual.get_all_names_ids('supplier')
    json_data = json.dumps(data)
    return json_data

@app.route('/party_names_and_ids', methods=['GET'])
def get_all_party_names():
    data = retrieve_indivijual.get_all_names_ids('party')
    json_data = json.dumps(data)
    return json_data

@app.route('/bank_names_and_ids', methods=['GET'])
def get_all_bank_names():
    data = retrieve_indivijual.get_all_names_ids('bank')
    json_data = json.dumps(data)
    return json_data

@app.route('/credit/<int:supplier_id>/<int:party_id>', methods=['GET'])
def get_credit(supplier_id: int, party_id: int):
    data = retrieve_credit.get_credit(supplier_id, party_id)
    json_data = json.dumps(data)
    return json_data

@app.route('/pending_bills/<int:supplier_id>/<int:party_id>', methods=['GET'])
def get_pending_bills(supplier_id: int, party_id: int):
    data = retrieve_register_entry.get_pending_bill_numbers(supplier_id, party_id)
    json_data = json.dumps(data)
    return json_data

@app.route('/add/register_entry/<int:bill>/<int:amount>/<string:supplier>/<string:party>/<string:date>', methods=['GET'])
def add_register_entry(bill: int, amount: int, supplier: str, party: str,  date: str):
    return RegisterEntry.create(bill, amount, json.loads(supplier), json.loads(party), date)

@app.route('/create_report', methods=['POST'])
def create_report():
    if request.method == "POST":
        data = request.json
        supplier_id = [element["id"] for element in json.loads(data["suppliers"])]
        party_id = [element["id"] for element in json.loads(data["parties"])]
        report = data['report']
        start = data['from']
        end = data['to']
        report_select.make_report(report, supplier_id, party_id, start, end)
    return {"status":"okay"}

@app.route('/add/individual/<string:type>/<string:name>/<string:phone>/<string:address>')
def add_individual(type: str, name: str, phone:str, address:str):
    insert_individual.add_individual(type, name, address)
    return {"status":"okay"}

@app.route('/add/memo_entry/<string:object>')
def add_memo_entry(object: str):
    object = json.loads(object)
    print(object)
    return MemoEntry.call(object)

@app.route('/add_legacy')
def add_legacy():
    add_suppliers.add()
    add_party.add()
    
    return {"status": "okay"}
    



if __name__ == '__main__':
    app.run(debug=True)
