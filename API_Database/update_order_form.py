from __future__ import annotations
from psql import execute_query


def update_order_form_data(entry) -> None:
    """
    Update changes made to the order form.
    """
   
    entry_id = entry.get_id()

    return update_order_form_by_id(entry, entry_id)

def update_order_form_by_id(entry, entry_id: int):

    query = "UPDATE order_form SET supplier_id= {}, party_id= {}, order_form_number = {}, " \
            "register_date = '{}', status = '{}' WHERE id = {}"\
        .format(entry.supplier_id, entry.party_id, entry.order_form_number, 
                str(entry.register_date), entry.status, entry_id)

    return execute_query(query)