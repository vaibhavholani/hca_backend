from __future__ import annotations
from typing import Dict
from psql import execute_query
from pypika import Query, Table
from Exceptions import DataError

def update_item_entry(item_entry) -> Dict:
    """
    Update an item entry in the database based on the provided ItemEntry object.
    """
    item_entry_table = Table('item_entry')
    
    # Constructing the update query
    update_query = (Query.update(item_entry_table)
                    .set(item_entry_table.register_entry_id, item_entry.register_entry_id)
                    .set(item_entry_table.item_id, item_entry.item_id)
                    .set(item_entry_table.quantity, item_entry.quantity)
                    .set(item_entry_table.rate, item_entry.rate)
                    .where(item_entry_table.id == item_entry.get_id())
                   )
    sql = update_query.get_sql()
    ret = execute_query(sql)
    
    return ret
