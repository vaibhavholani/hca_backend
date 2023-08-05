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
        query = "ALTER TABLE memo_entry ADD COLUMN gr_amount INT DEFAULT 0, ADD COLUMN deduction INT DEFAULT 0;"
        execute_query(query)
    except Exception as e: 
        print("Error Occured: Please contact Vaibhav")
        print(e)

