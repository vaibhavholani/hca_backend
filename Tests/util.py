from __future__ import annotations
from typing import Dict
from psql import execute_query

def delete_supplier(supplier_id: int) -> None:
    """
    Delete a supplier from the database based on the supplier ID.
    """
    # Open a new connection
    sql = f"DELETE FROM supplier WHERE id = {supplier_id}"
    return 


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
