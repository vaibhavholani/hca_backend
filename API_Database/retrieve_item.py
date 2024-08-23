from __future__ import annotations
from typing import List, Dict
from psql import execute_query
from Exceptions import DataError
from pypika import Query, Table

def get_all_items(supplier_id: int = None, name: str = None, color: str = None) -> List[Dict]:
    """
    Retrieve items from the database based on the provided criteria.
    If no criteria is provided, all items will be returned.
    """
    item_table = Table('item')
    
    # Constructing the select query
    select_query = Query.from_(item_table).select('*')
    
    if supplier_id:
        select_query = select_query.where(item_table.supplier_id == supplier_id)
    if name:
        select_query = select_query.where(item_table.name == name)
    if color:
        select_query = select_query.where(item_table.color == color)
    
    
    sql = select_query.get_sql()
    return execute_query(sql)["result"]

def retrieve_item(supplier_id: int, name: str, color: str) -> Dict:
    result = get_all_items(supplier_id, name, color)

    if len(result) == 0:
        raise DataError(f"No Item found with given criteria: Supplier id: {supplier_id}, {name}, {color}")

    if len(result) != 1:
        raise DataError(f"Multiple Items found with given criteria: Supplier id: {supplier_id}, {name}, {color}")
    
    return result[0]

def get_item_id(supplier_id: int, name: str, color: str) -> int:
    """
    Get the ID of the item based on the provided criteria.
    """
    item_table = Table('item')
    
    # Constructing the select query
    select_query = Query.from_(item_table).select(item_table.id)
    select_query = select_query.where(item_table.supplier_id == supplier_id)
    select_query = select_query.where(item_table.name == name)
    select_query = select_query.where(item_table.color == color)
    
    sql = select_query.get_sql()
    result = execute_query(sql)["result"]
    
    if len(result) == 0:
        raise DataError(f"No Item found with given criteria: Supplier id: {supplier_id}, {name}, {color}")
    
    return int(result[0]["id"])
    
