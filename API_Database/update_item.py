from __future__ import annotations
from typing import Dict
from psql import execute_query
from pypika import Query, Table
from Exceptions import DataError

def update_item(item) -> Dict:
    """
    Update an item in the database based on the provided Item object.
    """
    item_table = Table('item')
    
    # Constructing the update query
    update_query = (Query.update(item_table)
                    .set(item_table.supplier_id, item.supplier_id)
                    .set(item_table.name, item.name)
                    .set(item_table.color, item.color)
                    .where(item_table.id == item.get_id())
                   )
    sql = update_query.get_sql()
    ret = execute_query(sql)
    
    return ret
