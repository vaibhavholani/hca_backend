from __future__ import annotations
from typing import List, Dict, Union
from psql import execute_query
from Exceptions import DataError
from pypika import Query, Table


def get_all_item_entries(register_entry_id: int = None, item_id: int = None) -> List[Dict]:
    """
    Retrieve item entries from the database based on the provided criteria.
    If no criteria is provided, all item entries will be returned.
    """
    item_entry_table = Table('item_entry')

    # Constructing the select query
    select_query = Query.from_(item_entry_table).select('*')

    if register_entry_id:
        select_query = select_query.where(
            item_entry_table.register_entry_id == register_entry_id)
    if item_id:
        select_query = select_query.where(item_entry_table.item_id == item_id)

    sql = select_query.get_sql()
    return execute_query(sql)["result"]


def retrieve_item_entry(register_entry_id: int, item_id: int) -> Union[List[Dict], Dict]:
    # todo: CHANGE THIS SUCH THAT IT CAN RETURN A LIST
    result = get_all_item_entries(register_entry_id, item_id)

    # if len(result) == 0:
    #     raise DataError(
    #         f"No Item Entry found with given criteria: Register Entry id: {register_entry_id}, Item id: {item_id}")

    if register_entry_id and item_id:
        if len(result) != 1:
            raise DataError(
                f"Multiple Item Entries found with given criteria: Register Entry id: {register_entry_id}, Item id: {item_id}")
        else:
            return result[0]

    return result


def get_item_entry_id(register_entry_id: int, item_id: int) -> int:
    """
    Get the ID of the item entry based on the provided criteria.
    """
    item_entry_table = Table('item_entry')

    # Constructing the select query
    select_query = Query.from_(item_entry_table).select(item_entry_table.id)
    select_query = select_query.where(
        item_entry_table.register_entry_id == register_entry_id)
    select_query = select_query.where(item_entry_table.item_id == item_id)

    sql = select_query.get_sql()
    result = execute_query(sql)["result"]

    if len(result) == 0:
        raise DataError(
            f"No Item Entry found with given criteria: Register Entry id: {register_entry_id}, Item id: {item_id}")

    return int(result[0]["id"])
