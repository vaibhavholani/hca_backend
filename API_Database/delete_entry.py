from typing import Dict
from psql import execute_query

def delete_by_id(id: int, table_name: str) -> Dict:
    """Deletes a record from the specified table by its ID and returns the result."""
    sql = f'DELETE from {table_name} where id={id}'
    return execute_query(sql)

def delete_memo_payments(memo_id: int) -> Dict:
    """Deletes memo payments for a given memo ID and returns the execution result."""
    query = f'delete from memo_payments where memo_id = {memo_id}'
    return execute_query(query)