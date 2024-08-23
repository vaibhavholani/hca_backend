from __future__ import annotations
from typing import Dict
from psql import execute_query
from Exceptions import DataError
from pypika import Query, Table

def check_new_item_entry(item_entry) -> bool:
    """
    Check if the item_entry already exists in the database based on register_entry_id and item_id.
    """
    query = "select id from item_entry where register_entry_id = '{}' AND item_id = '{}'".format(
        item_entry.register_entry_id, item_entry.item_id)
    response = execute_query(query)
    if len(response["result"]) == 0:
        return True
    return False

def insert_item_entry(item_entry) -> Dict:
    """
    Insert an item_entry into the database.
    """
    if check_new_item_entry(item_entry):
        item_entry_table = Table('item_entry')
        insert_query = Query.into(item_entry_table).columns(
            'register_entry_id',
            'item_id',
            'quantity',
            'rate'
        ).insert(
            item_entry.register_entry_id,
            item_entry.item_id,
            item_entry.quantity,
            item_entry.rate
        )
        sql = insert_query.get_sql()
        ret = execute_query(sql)
        
        return ret
    else:
        raise DataError({"status": "error",
                         "message": "Duplicate Item Entry",
                         "input_errors": {"register_entry_id": {"status": "error", "message": "Item Entry already exists for the given register_entry_id and item_id"}}})
