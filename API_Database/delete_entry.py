import sys
sys.path.append("../")
from psql import db_connector
import psycopg2
from typing import Dict
from API_Database import update_memo_entry, retrieve_memo_entry

def delete_entry(data: Dict, table: str):
    id = data["id"]
    db, cursor = db_connector.cursor()

    if table == "memo_entry":
        all_ids = retrieve_memo_entry.get_memo_bills_by_id(id)

        for ids in all_ids:
            update_memo_entry.delete_memo_bill(ids["id"])
        
        update_memo_entry.delete_memo_payments(id)

    if table == "memo_bills":
        update_memo_entry.delete_memo_bill(id)
    else:
        sql = f"DELETE from {table} where id={id}"

        try:
            cursor.execute(sql)
        except psycopg2.errors.ForeignKeyViolation:
            return {"status": "error", "message": f"The {table} can't be deleted as it is referenced in another table"}
    db.commit()
    db.close()
    return {"status": "okay"}