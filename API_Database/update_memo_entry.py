from __future__ import annotations
from psql import db_connector, execute_query
from API_Database import retrieve_memo_entry
import datetime
from typing import Dict
from Entities import MemoEntry
import sys
sys.path.append("../")


def update_memo_entry_data(entry: MemoEntry) -> None:
    """
    Update changes made to  a memo_entry
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    entry_id = MemoEntry.get_memo_entry_id(entry.supplier_id,
                                                      entry.party_id,
                                                      entry.memo_number)

    if entry.mode != "Good Return":
        query = "UPDATE memo_entry SET amount = amount + '{}' " \
                "WHERE id = {}"\
            .format(entry.amount, entry_id)
    else:
        query = "UPDATE memo_entry SET gr_amount = gr_amount + '{}' " \
                "WHERE id = {}" \
            .format(entry.amount, entry_id)

    cursor.execute(query)
    db.commit()
    db.close()


def update_memo_amount(id: int, custom_amount: int = 0):

    # Open a new connection
    db, cursor = db_connector.cursor(True)

    query = f"SELECT supplier_id, party_id, memo_bills.amount as amount, memo_bills.type as type, memo_bills.bill_number as bill_number from memo_bills join memo_entry on memo_bills.memo_id = memo_entry.id where memo_bills.memo_id = {id}"

    cursor.execute(query)

    data = cursor.fetchall()

    amount = 0

    for bills in data:

        if bills["type"] in ['D', 'G', 'C']:
            pass
        else:
            amount += bills["amount"]

    if custom_amount != 0:
        amount = custom_amount

    query = f"UPDATE memo_entry SET amount = {amount} WHERE id = {id}"
    cursor.execute(query)

    db.commit()
    db.close()


def update_memo_entry_from_obj(data: Dict):

    # Open a new connection
    db, cursor = db_connector.cursor(True)

    memo_number = int(data["memo_number"])
    supplier_id = int(data['supplier_id'])
    party_id = int(data['party_id'])
    register_date = (datetime.datetime.strptime(
        data['register_date'], "%Y-%m-%d"))
    memo_id = int(data["id"])

    query = f"UPDATE memo_entry SET memo_number = {memo_number}, supplier_id={supplier_id}, party_id = {party_id}, register_date='{register_date}' where id={memo_id}"

    try:
        cursor.execute(query)
    except:
        return {"status": "error", "message": "Could not update Memo Entry. Please contact Vaibhav"}

    db.commit()
    db.close()

    return {"status": "okay"}
