from __future__ import annotations
from psql import db_connector


def get_partial_payment(supplier_id: int, party_id: int) -> int:
    """
    Returns the partial payment without bill between the party and supplier.
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    query = "select partial_amount from supplier_party_account where supplier_id = '{}' AND party_id = '{}'".format(
        supplier_id, party_id)
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    db.close()

    if len(data) == 0 or data[0][0] is None:
        return -1
    return int(data[0][0])
