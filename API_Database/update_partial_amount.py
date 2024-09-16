from __future__ import annotations
from psql import execute_query
from pypika import Query, Table

def update_part_payment(supplier_id: int, 
                        party_id: int, 
                        memo_id: int, 
                        use_memo_id: int = None, 
                        used: bool = True) -> None:
    """
    Use partial amount between a supplier and party
    """

    part_payments = Table('part_payments')

    update_query = (
        Query.update(part_payments)
        .set(part_payments.used, used)
        .set(part_payments.use_memo_id, None if use_memo_id is None else use_memo_id)
        .where(part_payments.supplier_id == supplier_id)
        .where(part_payments.party_id == party_id)
        .where(part_payments.memo_id == memo_id)
    )

    return execute_query(update_query.get_sql())





