from __future__ import annotations
from Entities import RegisterEntry
from API_Database import retrieve_register_entry
from psql import execute_query


def update_register_entry_data(entry: RegisterEntry) -> None:
    """
    Update changes made to the register entry by a memo_entry
    """
   
    entry_id = entry.get_id()

    return update_register_entry_by_id(entry, entry_id)

def update_register_entry_by_id(entry: RegisterEntry, entry_id: int):

    query = "UPDATE register_entry SET supplier_id= {}, party_id= {}, register_date = '{}', " \
            "amount = {}, partial_amount = '{}', status = '{}', " \
            "deduction = '{}', gr_amount = '{}', bill_number = {} WHERE id = {}"\
        .format(entry.supplier_id, entry.party_id, str(entry.register_date), entry.amount, 
                entry.partial_amount, entry.status, entry.deduction, entry.gr_amount, 
                entry.bill_number, entry_id)

    return execute_query(query)