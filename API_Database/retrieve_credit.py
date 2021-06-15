from __future__ import annotations
import sys
sys.path.append("../")
from psql import db_connector


def get_credit(supplier_id: int, party_id: int) -> dict:
    """
    Returns the partial payment without bill between the party and supplier.
    """
    # Open a new connection
    db, cursor = db_connector.cursor(True)
    
    query = "select partial_amount from supplier_party_account where supplier_id = '{}' AND party_id = '{}'".format(supplier_id, party_id)
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()

    return data