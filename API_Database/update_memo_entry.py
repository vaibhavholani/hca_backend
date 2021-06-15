from __future__ import annotations
from Entities import MemoEntry
from API_Database import retrieve_memo_entry
from psql import db_connector


def update_memo_entry_data(entry: MemoEntry) -> None:
    """
    Update changes made to  a memo_entry
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    entry_id = retrieve_memo_entry.get_id_by_memo_number(entry.memo_number, entry.supplier_id, entry.party_id)

    if entry.mode != "Good Return":
        query = "UPDATE memo_entry SET amount = amount + '{}' " \
                "WHERE id = {}"\
            .format(entry.amount, entry_id)
    else:
        query = "UPDATE memo_entry SET gr_amount = gr_amount + '{}' " \
                "WHERE id = {}" \
            .format(entry.amount, entry_id)

    cursor.execute(query)
    db_connector.add_stack(query)
    db.commit()
    db.disconnect()
    db_connector.update()
