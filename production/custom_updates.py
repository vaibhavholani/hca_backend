import os
import sys
sys.path.append("../")
from psql import execute_query

def execute_sql_file(filename):
    with open(filename, 'r') as f:
        sql_commands = f.read().split(';')
    
    for command in sql_commands:
        # Check if the command is empty or just whitespace
        command = command.strip()
        if command == '':
            continue
        print(f"Executing Query: {command}")
        status = execute_query(command, exec_remote=False)
        print(f"Query Execution Status: {status} for Query: {command}")

if __name__ == "__main__":

    try: 
        execute_sql_file("custom_updates.sql")
    except Exception as e: 
        print("Error Occured: Please contact Vaibhav")
        print(e)
