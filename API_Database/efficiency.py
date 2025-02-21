from __future__ import annotations
from psql import db_connector
import datetime
from typing import List, Tuple

def intersection(lst1, lst2):
    """Returns the intersection of two lists as a new list."""
    return list(set(lst1) & set(lst2))

def smart_selection(suppliers: List[int], parties: List[int], start_date: datetime, end_date: datetime) -> Tuple:
    """
    Filter out the the suppliers and party with data
    """
    (db, cursor) = db_connector.cursor()
    query = "\n    (SELECT supplier_id, party_id \n     FROM register_entry \n     WHERE register_date BETWEEN '{}' AND '{}')\n    UNION\n    (SELECT supplier_id, party_id \n     FROM order_form \n     WHERE register_date BETWEEN '{}' AND '{}')\n    ".format(str(start_date), str(end_date), str(start_date), str(end_date))
    cursor.execute(query)
    data = cursor.fetchall()
    smart_supplier = []
    smart_party = []
    for tups in data:
        smart_supplier.append(tups[0])
        smart_party.append(tups[1])
    new_supplier = [supplier for supplier in suppliers if supplier in smart_supplier]
    new_party = [party for party in parties if party in smart_party]
    return (new_party, new_supplier)

def filter_out_parties(supplier_id: int, parties: List[int]) -> List[int]:
    """
    Get all the parties the supplier has worked with
    """
    (db, cursor) = db_connector.cursor()
    query = '\n        SELECT party_id FROM register_entry WHERE supplier_id = {}\n        UNION\n        SELECT party_id FROM order_form WHERE supplier_id = {}\n    '.format(supplier_id, supplier_id)
    cursor.execute(query)
    data = cursor.fetchall()
    smart_party = []
    for tups in data:
        smart_party.append(tups[0])
    new_party = [party for party in parties if party in smart_party]
    return new_party

def filter_out_supplier(party_id: int, suppliers: List[int]) -> List[int]:
    """
    Get all the suppliers the party has worked with
    """
    (db, cursor) = db_connector.cursor()
    query = '\n        SELECT supplier_id FROM register_entry WHERE party_id = {}\n        UNION\n        SELECT supplier_id FROM order_form WHERE party_id = {}\n    '.format(party_id, party_id)
    cursor.execute(query)
    data = cursor.fetchall()
    smart_supplier = []
    for tups in data:
        smart_supplier.append(tups[0])
    new_supplier = [supplier for supplier in suppliers if supplier in smart_supplier]
    return new_supplier