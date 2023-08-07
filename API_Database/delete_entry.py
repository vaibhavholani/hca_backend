from typing import Dict
from psql import execute_query

# def delete_entry(data: Dict, table: str):
#     id = data["id"]
#     db, cursor = db_connector.cursor()

#     if table == "memo_entry":
#         all_ids = retrieve_memo_entry.get_memo_bills_by_id(id)

#         for ids in all_ids:
#             update_memo_entry.delete_memo_bill(ids["id"])
        
#         update_memo_entry.delete_memo_payments(id)

#     if table == "memo_bills":
#         update_memo_entry.delete_memo_bill(id)
#     else:
#         return delete_by_id(id, table)

def delete_by_id(id: int, table_name: str) -> Dict: 
    sql = f"DELETE from {table_name} where id={id}"
    return execute_query(sql)

def delete_memo_payments(memo_id: int) -> Dict:
    query = f"delete from memo_payments where memo_id = {memo_id}"
    return execute_query(query)