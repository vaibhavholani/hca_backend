from __future__ import annotations
from psql import db_connector
from Indivijuval import Supplier, Party, Bank, Transporter


def insert_supplier(supplier: Supplier) -> None:

    # Open a new connection
    db, cursor = db_connector.cursor()

    sql = "INSERT INTO supplier (name, address) VALUES (%s, %s)"
    val = (supplier.name, supplier.address)

    cursor.execute(sql, val)
    db_connector.add_stack_val(sql, val)
    db.commit()
    db.close()
    db_connector.update()


def insert_party(party: Party) -> None:
    # Open a new connection
    db, cursor = db_connector.cursor()

    sql = "INSERT INTO party (name, address) VALUES (%s, %s)"
    val = (party.name, party.address)

    cursor.execute(sql, val)
    db_connector.add_stack_val(sql, val)
    db.commit()
    db.close()
    db_connector.update()


def insert_bank(bank: Bank) -> None:
    # Open a new connection
    db, cursor = db_connector.cursor()

    sql = "INSERT INTO bank (name, address) VALUES (%s, %s)"
    val = (bank.name, bank.address)

    cursor.execute(sql, val)
    db_connector.add_stack_val(sql, val)
    db.commit()
    db.close()
    db_connector.update()


def insert_transporter(transporter: Transporter) -> None:
    # Open a new connection
    db, cursor = db_connector.cursor()

    sql = "INSERT INTO Transport (name, address) VALUES (%s, %s)"
    val = (transporter.name, transporter.address)

    cursor.execute(sql, val)
    db_connector.add_stack_val(sql, val)
    db.commit()
    db.close()
    db_connector.update()

