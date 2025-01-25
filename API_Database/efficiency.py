from __future__ import annotations
from psql import db_connector
import datetime
from typing import List, Tuple


def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))


def smart_selection(suppliers: List[int], parties: List[int], start_date: datetime, end_date: datetime) -> Tuple:
    """
    Filter out the the suppliers and party with data
    """

    db, cursor = db_connector.cursor()

    # Query to fetch supplier_id and party_id from both register_entry and order_form tables between the given dates
    query = """
    (SELECT supplier_id, party_id 
     FROM register_entry 
     WHERE register_date BETWEEN '{}' AND '{}')
    UNION
    (SELECT supplier_id, party_id 
     FROM order_form 
     WHERE register_date BETWEEN '{}' AND '{}')
    """.format(str(start_date), str(end_date), str(start_date), str(end_date))


    cursor.execute(query)
    data = cursor.fetchall()

    smart_supplier = []
    smart_party = []

    for tups in data:
        smart_supplier.append(tups[0])
        smart_party.append(tups[1])

    new_supplier = [supplier for supplier in suppliers if supplier in smart_supplier]
    new_party = [party for party in parties if party in smart_party]

    return new_party, new_supplier


def filter_out_parties(supplier_id: int, parties: List[int]) -> List[int]:
    """
    Get all the parties the supplier has worked with
    """

    db, cursor = db_connector.cursor()
    # Combining the query for register_entry and order_form using UNION
    query = """
        SELECT party_id FROM register_entry WHERE supplier_id = {}
        UNION
        SELECT party_id FROM order_form WHERE supplier_id = {}
    """.format(supplier_id, supplier_id)

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
    db, cursor = db_connector.cursor()
    query = """
        SELECT supplier_id FROM register_entry WHERE party_id = {}
        UNION
        SELECT supplier_id FROM order_form WHERE party_id = {}
    """.format(party_id, party_id)
    
    cursor.execute(query)
    data = cursor.fetchall()
    smart_supplier = []

    for tups in data:
        smart_supplier.append(tups[0])

    new_supplier = [supplier for supplier in suppliers if supplier in smart_supplier]

    return new_supplier