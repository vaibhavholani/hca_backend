from __future__ import annotations
from typing import Dict
from psql import db_connector


def insert_supplier(supplier_id: int) -> None:
    # Open a new connection
    db, cursor = db_connector.cursor()

    # Check if the supplier already exists
    sql_insert = """
        INSERT INTO supplier (id, name, address)
        SELECT %s, %s, %s
        WHERE NOT EXISTS (
            SELECT id FROM supplier WHERE id = %s
        )
    """
    val_insert = (supplier_id, 'test_supplier', 'supplier_address', supplier_id)

    cursor.execute(sql_insert, val_insert)
    db.commit()
    db.close()
    db_connector.update()


def insert_party(party_id: int) -> None:
    # Open a new connection
    db, cursor = db_connector.cursor()

    # Insert the party if it doesn't already exist
    sql_insert = """
        INSERT INTO party (id, name, address)
        SELECT %s, %s, %s
        WHERE NOT EXISTS (
            SELECT id FROM party WHERE id = %s
        )
    """
    val_insert = (party_id, 'test_party', 'party_address', party_id)

    cursor.execute(sql_insert, val_insert)
    db.commit()
    db.close()
    db_connector.update()

def delete_supplier(supplier_id: int) -> None:
    """
    Delete a supplier from the database based on the supplier ID.
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    sql = "DELETE FROM supplier WHERE id = %s"
    val = (supplier_id,)

    cursor.execute(sql, val)
    db.commit()
    db.close()
    db_connector.update()


def delete_party(party_id: int) -> None:
    """
    Delete a party from the database based on the party ID.
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    sql = "DELETE FROM party WHERE id = %s"
    val = (party_id,)

    cursor.execute(sql, val)
    db.commit()
    db.close()
    db_connector.update()
