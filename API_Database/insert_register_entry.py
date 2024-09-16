from __future__ import annotations
from psql import execute_query
from API_Database import sql_date
from pypika import Query, Table


def check_new_register(entry) -> bool:
    """
    Check if the register_entry already exists.
    """
    
    # Open a new connection
    query = "select id from register_entry where bill_number = '{}' AND supplier_id = '{}' AND party_id = '{}' AND register_date = '{}'".format(
        entry.bill_number, entry.supplier_id, entry.party_id, entry.register_date)
    response = execute_query(query)
    if len(response["result"]) == 0:
        return True
    return False


def insert_register_entry(entry) -> None:
    """
    Insert a register_entry into the database.
    """
    
    # Define the table
    register_entry_table = Table('register_entry')

    # Build the INSERT query using Pypika
    insert_query = Query.into(register_entry_table).columns(
        'supplier_id',
        'party_id',
        'register_date',
        'amount',
        'bill_number',
        'status',
        'gr_amount',
        'deduction'
    ).insert(
        entry.supplier_id,
        entry.party_id,
        entry.register_date,
        entry.amount,
        entry.bill_number,
        entry.status,
        entry.gr_amount,
        entry.deduction
    )

    # Get the raw SQL query and parameters from the Pypika query
    sql = insert_query.get_sql()
    # Execute the query
    return execute_query(sql)
