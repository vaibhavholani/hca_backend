import os
import sys
sys.path.append("../")
from psql import execute_query
from Exceptions import DataError
from Entities import MemoEntry

def repair_data():
    memo_entry_del_data = [
    {"supplier_id": 2623, "party_id": 387, "memo_number": 884},
    {"supplier_id": 2394, "party_id": 530, "memo_number": 2991},
    {"supplier_id": 1685, "party_id": 621, "memo_number": 3147},
    {"supplier_id": 2419, "party_id": 426, "memo_number": 3039},
    {"supplier_id": 2623, "party_id": 387, "memo_number": 2964}]

    # Assuming MemoEntry class has a retrieve method
    for entry_data in memo_entry_del_data:
        try:
            supplier_id = entry_data["supplier_id"]
            party_id = entry_data["party_id"]
            memo_number = entry_data["memo_number"]
            print(f"Processing supplier_id: {supplier_id}, party_id: {party_id} and memo_number: {memo_number}")
            memo_entry = MemoEntry.retrieve(
                supplier_id=supplier_id,
                party_id=party_id,
                memo_number=memo_number
            )
        
            if memo_entry:
                # Assuming there's a delete method in MemoEntry class
                memo_entry.delete()
        except DataError as e:
            print(e.error_dict)



    

def execute_sql_file(filename):
    with open(filename, 'r') as f:
        sql_commands = f.read().split(';')
    
    for command in sql_commands:
        # Check if the command is empty or just whitespace
        command = command.strip()
        if command == '':
            continue

        status = execute_query(command)
        print(f"Query Execution Status: {status} for Query: {command}")

if __name__ == "__main__":

    # try: 
    #     execute_sql_file("custom_updates.sql")
    # except Exception as e: 
    #     print("Error Occured: Please contact Vaibhav")
    #     print(e)
    repair_data()