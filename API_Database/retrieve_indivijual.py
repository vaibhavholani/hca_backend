from __future__ import annotations
from typing import List, Tuple
from psql import db_connector

def get_all_names_ids(name: str) -> dict:
    """
    Get all <name> ids and names returned in a dictionary
    """
    # Open a new connection
    db, cursor = db_connector.cursor(True)

    query = f"select id, name from {name}"
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return data

def get_party_name_by_id(party_id: int) -> str:
    """
    Get party name by ID
    """
    # Open a new connection
    db, cursor = db_connector.cursor()
    query = "select name from party where id = '{}';".format(party_id)
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return data[0][0]

def get_supplier_name_by_id(supplier_id: int) -> str:
    """
    Get supplier name by ID
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    query = "select name from supplier where id = '{}';".format(supplier_id)
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return data[0][0]
