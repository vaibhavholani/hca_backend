from __future__ import annotations
from psql import db_connector
from Entities import MemoEntry


def insert_partial_payment(entry: MemoEntry) -> None:
    """
    Inserts partial payment between the account of supplier and party.
    """

    # Open a new connection
    db, cursor = db_connector.cursor()

    sql = "INSERT INTO supplier_party_account (supplier_id, party_id, partial_amount) " \
          "VALUES (%s, %s, %s)"
    val = (entry.supplier_id, entry.party_id, entry.amount)

    cursor.execute(sql, val)
    db_connector.add_stack_val(sql, val)
    db.commit()
    db.close()
    db_connector.update()
