from __future__ import annotations
from Entities import RegisterEntry
from API_Database import retrieve_register_entry
from psql import db_connector


def update_register_entry_data(entry: RegisterEntry) -> None:
    """
    Update changes made to the register entry by a memo_entry
    """
   

    entry_id = retrieve_register_entry.get_register_entry_id(entry.supplier_id, entry.party_id, entry.bill_number)

    update_register_entry_by_id(entry, entry_id)

def update_register_entry_by_id(entry: RegisterEntry, entry_id):

     # Open a new connection
    db, cursor = db_connector.cursor()

    query = "UPDATE register_entry SET supplier_id= {}, party_id= {}, register_date = '{}', " \
            "amount = {}, partial_amount = '{}', status = '{}', " \
            "deduction = '{}', gr_amount = '{}', bill_number = {} WHERE id = {}"\
        .format(entry.supplier_id, entry.party_id, str(entry.date), entry.amount, 
                entry.part_payment, entry.status, entry.deduction, entry.gr_amount, 
                entry.bill_number, entry_id)

    try: 
        cursor.execute(query)
    except: 
        return {"status": "error", "message": "Could not update Register Entry. Please contact Vaibhav"}
    
    db.commit()
    db.close()

    return {"status": "okay"}




def fix_problems():

    db, cursor = db_connector.cursor()

    sql = f"UPDATE register_entry SET gr_amount = 0 and status = 'N' where supplier_id = {998} and party_id = {70}"

    cursor.execute(sql)

    db.commit()
    db.close()

