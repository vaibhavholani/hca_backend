from __future__ import annotations
from typing import Dict
from psql import execute_query
from pypika import Query, Table


def check_new_order_form(entry) -> bool:
    """
    Check if the order_form already exists.
    """

    query = "select id from order_form where order_form_number = '{}' AND supplier_id = '{}' AND party_id = '{}'".format(
        entry.order_form_number, entry.supplier_id, entry.party_id)
    response = execute_query(query)
    if len(response["result"]) == 0:
        return True
    return False

def insert_order_form(entry) -> Dict:
    """
    Insert an order_form into the database.
    """
    
    # Define the table
    order_form_table = Table('order_form')

    # Build the INSERT query using Pypika
    insert_query = Query.into(order_form_table).columns(
        'supplier_id',
        'party_id',
        'order_form_number',
        'register_date',
        'status'
    ).insert(
        entry.supplier_id,
        entry.party_id,
        entry.order_form_number,
        entry.register_date,
        entry.status
    )

    # Get the raw SQL query and parameters from the Pypika query
    sql = insert_query.get_sql()
    # Execute the query
    return execute_query(sql)