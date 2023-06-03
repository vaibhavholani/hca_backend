from __future__ import annotations
from API_Database import retrieve_partial_payment
from psql import db_connector


def add_partial_amount(supplier_id: int, party_id: int, amount: int) -> None:
    """
    Add partial amount between a supplier and party
    """

    # Open a new connection
    db, cursor = db_connector.cursor()

    partial_amount = int(retrieve_partial_payment.get_partial_payment(supplier_id, party_id))
    amount += partial_amount

    query = "UPDATE supplier_party_account SET partial_amount = {} WHERE supplier_id = {} AND party_id = {}" \
        .format(amount, supplier_id, party_id)

    cursor.execute(query)
    db.commit()
    db.close()
    db_connector.update()


def use_partial_amount(supplier_id: int, party_id: int, amount: int) -> None:
    """
    Use partial amount between a supplier and party
    """

    # Open a new connection
    db, cursor = db_connector.cursor()

    partial_amount = int(retrieve_partial_payment.get_partial_payment(supplier_id, party_id))
    amount = partial_amount - amount
    if amount < 0:
        amount = 0
    query = "UPDATE supplier_party_account SET partial_amount = {} WHERE supplier_id = {} AND party_id = {}" \
        .format(amount, supplier_id, party_id)

    cursor.execute(query)
    db_connector.add_stack(query)
    db.commit()
    db.close()
    db_connector.update()


def update_part_payment(supplier_id: int, party_id: int, memo_id:int, use_memo_id:int) -> None:
    """
    Use partial amount between a supplier and party
    """

    # Memo updates not showing
    # Open a new connection
    db, cursor = db_connector.cursor()

    query = "UPDATE part_payments SET used = {}, use_memo_id = {} WHERE supplier_id = {} AND party_id = {} AND memo_id = {}" \
        .format(True, use_memo_id, supplier_id, party_id, memo_id)
    print(query)
    cursor.execute(query)
    db_connector.add_stack(query)
    db.commit()
    db.close()
    db_connector.update()
