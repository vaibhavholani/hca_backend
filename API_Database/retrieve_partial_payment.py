from __future__ import annotations
from typing import Dict
from psql import db_connector, execute_query
from Exceptions import DataError

def get_partial_payment(supplier_id: int, party_id: int) -> int:
    """
    Returns the partial payment without bill between the party and supplier.
    """
    # Open a new connection
    db, cursor = db_connector.cursor(True)

    query = "select memo_id, used from part_payments where supplier_id = '{}' AND party_id = '{}'".format(
        supplier_id, party_id)
    cursor.execute(query)
    data = cursor.fetchall()
    # find the memo_billss for memo_id 
    part_list = []
    for parts in data:
        if parts["used"] == False:
            query="select memo_entry.memo_number as memo_no, to_char(register_date, 'DD/MM/YYYY') as memo_date, memo_entry.amount as chk_amt, memo_bills.amount as memo_amt, memo_bills.type as memo_type from memo_entry join memo_bills on memo_entry.id = memo_bills.memo_id where memo_entry.id = '{}' and memo_bills.type = 'PR'".format(parts["memo_id"])
            cursor.execute(query)
            memo_bills_data = cursor.fetchall()
            part_list.extend(memo_bills_data)
    
    db.close()
    return part_list

def get_partial_payment_by_memo_id(memo_id: int) -> Dict: 
    query = "select id, memo_id, used from part_payments where memo_id = '{}'".format(memo_id)
    response = execute_query(query)

    if len(response["result"]) > 1 or len(response["result"]) == 0:
        raise DataError(f"More than one party payment added with memo_id: {memo_id}")
    
    return response["result"][0]
