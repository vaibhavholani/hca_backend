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

from rapidfuzz import process, distance



data = retrieve_indivijual.get_all_names_ids('supplier', dict_cursor=False)
supplier_names = names = [y[1].lower() for y in data]

# String to query against
query = "V. Sons Emporio Private Limited"
# Convert the query to lowercase
query = query.lower()

# Perform fuzzy matching using RapidFuzz
# process.extract returns a list of tuples with the matched name and the similarity score
matches = process.extract(query, names, scorer=distance.JaroWinkler.distance, limit=10)  # Change limit to control the number of results


# Display the best matches
print("Best matches:")
for match in matches:
    print(f"Name: {match[0]}, Similarity Score: {match[1]:.2f}")
