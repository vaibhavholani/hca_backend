from typing import Dict
from psql import execute_query

    

def delete_by_id(id: int, table_name: str) -> Dict: 
    sql = f"DELETE from {table_name} where id={id}"
    return execute_query(sql)

def delete_memo_payments(memo_id: int) -> Dict:
    query = f"delete from memo_payments where memo_id = {memo_id}"
    return execute_query(query)