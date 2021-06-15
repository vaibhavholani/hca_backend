from __future__ import annotations
from psql import db_connector
from Entities import RegisterEntry


def check_new_register(entry: RegisterEntry) -> bool:
    """
    Check if the register_entry already exists.
    """

    # Open a new connection
    db, cursor = db_connector.cursor()

    query = "select id from register_entry where bill_number = '{}' AND supplier_id = '{}' AND party_id = '{}'".format(
        entry.bill_number, entry.supplier_id, entry.party_id)
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    if len(data) == 0:
        return True
    return False


def insert_register_entry(entry: RegisterEntry) -> None:
    """
    Insert a register_entry into the database.
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    sql = "INSERT INTO register_entry (supplier_id, party_id, register_date, amount, bill_number, status, " \
          "d_amount, d_percent) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (entry.supplier_id, entry.party_id, str(entry.date), entry.amount, entry.bill_number, entry.status,
           entry.d_amount, entry.d_percent)

    cursor.execute(sql, val)
    db_connector.add_stack_val(sql, val)
    db.commit()
    db.close()
    db_connector.update()
