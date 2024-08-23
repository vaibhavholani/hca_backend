from __future__ import annotations
from psql import execute_query
from pypika import Query, Table, functions as fn


def update_order_form_data(entry) -> None:
    """
    Update changes made to the order form.
    """
   
    entry_id = entry.get_id()

    return update_order_form_by_id(entry, entry_id)

def update_order_form_by_id(entry, entry_id: int):

    query = "UPDATE order_form SET supplier_id= {}, party_id= {}, order_form_number = {}, " \
            "register_date = '{}', status = '{}', delivered= {} WHERE id = {}"\
        .format(entry.supplier_id, entry.party_id, entry.order_form_number, 
                str(entry.register_date), entry.status, entry.delivered, entry_id)

    return execute_query(query)



def mark_order_forms_as_registered(supplier_id: int = None, party_id: int = None):
    order_form = Table('order_form')
    register_entry = Table('register_entry')

    sub_query = (Query
                 .from_(order_form)
                 .join(register_entry)
                 .on((order_form.supplier_id == register_entry.supplier_id) &
                     (order_form.party_id == register_entry.party_id))
                 .where((order_form.delivered == False) & 
                        (register_entry.register_date > order_form.register_date))
                 .select(order_form.id)
                 )

    # If supplier_id and party_id are provided, then add them to the WHERE clause
    if supplier_id and party_id:
        sub_query = sub_query.where((order_form.supplier_id == supplier_id) & 
                                    (order_form.party_id == party_id))

    sql = (order_form
                    .update()
                    .set(order_form.delivered, True)
                    .where(order_form.id.isin(sub_query))
                    )
    
    return execute_query(sql.get_sql())