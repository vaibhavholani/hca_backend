import sys
sys.path.append("../")
from psql import db_connector
import psycopg2
from typing import Dict


def edit_individual(data: Dict, table: str):

    db, cursor = db_connector.cursor()

    name = data["name"]
    address = data["address"]
    id = data["id"]

    query = f"UPDATE {table} set name= '{name}', address= '{address}' where id={id}"

    try: 
        cursor.execute(query)
    except: 
        return {"status": "error", "message": f"Could not update {table} Please contact Vaibhav"}
    
    db.commit()
    db.close()

    return {"status": "okay"}