from __future__ import annotations
from API_Database import retrieve_partial_payment
from psql import execute_query

def update_part_payment(supplier_id: int, party_id: int, memo_id:int, use_memo_id:int) -> None:
    """
    Use partial amount between a supplier and party
    """

    query = "UPDATE part_payments SET used = {}, use_memo_id = {} WHERE supplier_id = {} AND party_id = {} AND memo_id = {}" \
        .format(True, use_memo_id, supplier_id, party_id, memo_id)

    return execute_query(query)