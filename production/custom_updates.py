import os
import sys
sys.path.append("../")
from psql import db_connector

def execute_query(query: str) -> None:
    db, cursor = db_connector.cursor()
    cursor.execute(query)
    db.commit()
    db.close()


if __name__ == "__main__":
    try: 
        query = "ALTER table memo_entry drop column gr_amount"
        execute_query(query)
    except Exception as e: 
        print("Error Occured: Please contact Vaibhav")
        print(e)

