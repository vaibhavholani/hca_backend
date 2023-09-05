from __future__ import annotations
from typing import Dict
from Exceptions import DataError
from psql import execute_query
from pypika import Query, Table

def check_new_item(item) -> bool:
    """
    Check if the item already exists in the database based on name and color.
    """
    query = "select id from item where name = '{}' AND color = '{}' AND supplier_id = '{}'".format(
        item.name, item.color, item.supplier_id)
    response = execute_query(query)
    if len(response["result"]) == 0:
        return True
    return False

def insert_item(item) -> Dict:
    """
    Insert an item into the database.
    """
    if check_new_item(item):
        item_table = Table('item')
        insert_query = Query.into(item_table).columns(
            'supplier_id',
            'name',
            'color'
        ).insert(
            item.supplier_id,
            item.name,
            item.color
        )
        sql = insert_query.get_sql()
        ret = execute_query(sql)
        
        return ret
    else:
        raise DataError({"status": "error",
                         "message": "Duplicate Item",
                         "input_errors": {"name": {"status": "error", "message": "Item name and color already exists"}}})
