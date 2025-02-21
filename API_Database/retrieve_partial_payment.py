from __future__ import annotations
from typing import Dict, List
from psql import db_connector, execute_query
from Exceptions import DataError

def get_partial_payment_bulk(supplier_ids: List[int], party_ids: List[int], supplier_all: bool=False, party_all: bool=False) -> List[Dict]:
    """
    Returns the partial payments without bills for multiple suppliers and parties.
    Optimized version that fetches data in bulk when all suppliers/parties are selected.
    """
    where_clauses = []
    if not supplier_all and supplier_ids:
        supplier_ids_str = ','.join(map(str, supplier_ids))
        where_clauses.append(f'part_payments.supplier_id IN ({supplier_ids_str})')
    if not party_all and party_ids:
        party_ids_str = ','.join(map(str, party_ids))
        where_clauses.append(f'part_payments.party_id IN ({party_ids_str})')
    where_clauses.append('part_payments.used = false')
    where_clause = ' AND '.join(where_clauses)
    query = "\n        WITH unused_parts AS (\n            SELECT memo_id\n            FROM part_payments\n            WHERE {}\n        )\n        SELECT\n            memo_entry.supplier_id as supplier_id, \n            memo_entry.party_id as party_id,\n            memo_entry.memo_number as memo_no,\n            to_char(memo_entry.register_date, 'DD/MM/YYYY') as memo_date,\n            memo_entry.amount as chk_amt,\n            memo_bills.amount as memo_amt,\n            memo_bills.type as memo_type\n        FROM unused_parts\n        JOIN memo_entry ON memo_entry.id = unused_parts.memo_id\n        JOIN memo_bills ON memo_entry.id = memo_bills.memo_id\n        JOIN supplier ON memo_entry.supplier_id = supplier.id\n        JOIN party ON memo_entry.party_id = party.id\n        WHERE memo_bills.type = 'PR'\n        ORDER BY supplier.name, party.name, memo_entry.register_date, memo_entry.memo_number;\n    ".format(where_clause)
    result = execute_query(query)
    return result['result']

def get_partial_payment(supplier_id: int, party_id: int) -> List[Dict]:
    """
    Returns the partial payment without bill between the party and supplier.
    Single supplier-party version that calls the bulk version for consistency.
    """
    return get_partial_payment_bulk([supplier_id], [party_id])

def get_partial_payment_by_memo_id(memo_id: int) -> Dict:
    """Retrieves partial payment details for a given memo ID; raises DataError if not exactly one record is found."""
    query = "select id, memo_id, used from part_payments where memo_id = '{}'".format(memo_id)
    response = execute_query(query)
    if len(response['result']) > 1 or len(response['result']) == 0:
        raise DataError(f'More than one party payment added with memo_id: {memo_id}')
    return response['result'][0]