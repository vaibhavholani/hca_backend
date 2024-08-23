from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import ast
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager


from API_Database import retrieve_indivijual, retrieve_credit, retrieve_register_entry
from API_Database import insert_individual, retrieve_all, retrieve_from_id
from API_Database import edit_individual, delete_entry, retrieve_memo_entry
from API_Database import update_register_entry, update_memo_entry


from backup import backup
from Entities import RegisterEntry, MemoEntry, OrderForm, Item, ItemEntry
from Individual import Supplier, Party, Bank, Transporter
from Reports import report_select, CustomEncoder
from Legacy_Data import add_party, add_suppliers
from Exceptions import DataError
from utils import table_class_mapper

# load env file
load_dotenv()

# Crate flask app
app = Flask(__name__)
CORS(app)
# stop flask from sorting keys
app.config['JSON_SORT_KEYS'] = False
# Change this!
app.config["JWT_SECRET_KEY"] = "NHYd198vQNOBa9HrIAGEGNYrKHBegc9Z"
jwt = JWTManager(app)

BASE = ""

# Authentication Request


@app.route(BASE + '/token', methods=["POST"])
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Check if the username and password is valid
    if username != "admin" or password != "admin5555":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Error Handler
@app.errorhandler(DataError)
def handle_data_error(e):
    error = e.dict()
    if error["status"] == "error" and "input_errors" not in error:
        error["input_errors"] = {}
    print("returning error")
    print(error)
    return jsonify(error), 500


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
    data = retrieve_register_entry.get_pending_bills(
        supplier_id, party_id)
    json_data = json.dumps(data)
    return json_data


@app.route(BASE + '/create_report', methods=['POST'])
def create_report():
    if request.method == "POST":
        data = request.json
        report_data = report_select.make_report(data)
        return jsonify(report_data)
    return {"status": "okay"}


@app.route(BASE + '/add/individual', methods=['POST'])
def add_individual():
    data = request.json

    entity_mapping = {
        "supplier": Supplier,
        "party": Party,
        "bank": Bank,
        "transport": Transporter}

    return entity_mapping[data["entity"]].insert(data)


@app.route(BASE + '/add/entry', methods=['POST'])
def add_entry():
    data = request.json

    entity_mapping = {
        "register_entry": RegisterEntry,
        "memo_entry": MemoEntry,
        "order_form": OrderForm,
        "item": Item,
        "item_entry": ItemEntry
    }

    return entity_mapping[data["entity"]].insert(data)


@app.route(BASE + '/add/register_entry', methods=['POST'])
def add_register_entry():
    data = request.json
    response = RegisterEntry.insert(data)
    return jsonify(response)


@app.route(BASE + '/add/memo_entry', methods=['POST'])
def add_memo_entry():
    data = request.json
    response = MemoEntry.insert(data)
    return jsonify(response)


@app.route(BASE + '/add/order_form', methods=['POST'])
def add_order_form_entry():
    data = request.json
    response = OrderForm.insert(data)
    return jsonify(response)


@app.route(BASE + '/add_legacy')
def add_legacy():
    add_suppliers.add()
    add_party.add()

    return {"status": "okay"}


@app.route(BASE + '/get_all', methods=['POST'])
def get_all():
    if request.method == 'POST':
        data = request.json

        return json.dumps(retrieve_all.get_all(**data), cls=CustomEncoder)


@app.route(BASE + '/get_by_id/<string:table_name>/<int:id>')
def get_id(table_name: str, id: int):
    data = retrieve_from_id.get_from_id(table_name, id)
    return json.dumps(data)


@app.route(BASE + '/update/<string:table_name>', methods=['POST'])
def update_id(table_name: str):
    if request.method == 'POST':
        data = request.json
        cls = table_class_mapper(table_name)
        instance = cls.from_dict(data)
        r_val = instance.update()
        return jsonify(r_val)


@app.route(BASE + '/delete/<string:table_name>', methods=['POST'])
def delete(table_name: str):
    if request.method == 'POST':
        data = request.json
        cls = table_class_mapper(table_name)
        instance = cls.from_dict(data, parse_memo_bills=True)
        r_val = instance.delete()
        return jsonify(r_val)

    raise DataError("Only POST requests are allowed on this /delete")


@app.route(BASE + '/get_memo_bills/<int:id>')
def get_memo_bills(id: int):
    data = retrieve_memo_entry.get_memo_bills_by_id(id)
    return json.dumps(data)


@app.route(BASE + '/backup', methods=['GET'])
def backup_data():

    # Get the current date
    current_date = datetime.now()
    # Format the date as "01_Jan_2023"
    formatted_date = current_date.strftime("%d_%b_%Y")

    # Usage example
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    os.makedirs("./backups", exist_ok=True)
    backup_file_path = f'./backups/backup_{formatted_date}.sql'

    return backup.backup_postgresql_database(user, dbname, password, backup_file_path)


@app.route(BASE + '/fix_problems')
def fix():
    update_register_entry.fix_problems()
    return {"status": "okay"}


if __name__ == '__main__':
    app.run(debug=True)
