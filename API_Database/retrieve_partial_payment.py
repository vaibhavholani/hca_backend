from __future__ import annotations
from typing import Dict, List
from psql import db_connector, execute_query
from Exceptions import DataError

def get_partial_payment_bulk(supplier_ids: List[int], party_ids: List[int], supplier_all: bool = False, party_all: bool = False) -> List[Dict]:
    """
    Returns the partial payments without bills for multiple suppliers and parties.
    Optimized version that fetches data in bulk when all suppliers/parties are selected.
    """
    # Build WHERE clause based on all flags
    where_clauses = []

    # Add supplier filter only if not all suppliers
    if not supplier_all and supplier_ids:
        supplier_ids_str = ','.join(map(str, supplier_ids))
        where_clauses.append(f"part_payments.supplier_id IN ({supplier_ids_str})")

    # Add party filter only if not all parties
    if not party_all and party_ids:
        party_ids_str = ','.join(map(str, party_ids))
        where_clauses.append(f"part_payments.party_id IN ({party_ids_str})")

    # Always add used=false filter
    where_clauses.append("part_payments.used = false")

    # If no where clauses (all suppliers and all parties), just use used=false
    where_clause = " AND ".join(where_clauses)

    query = """
        WITH unused_parts AS (
            SELECT memo_id
            FROM part_payments
            WHERE {}
        )
        SELECT 
            memo_entry.memo_number as memo_no,
            to_char(memo_entry.register_date, 'DD/MM/YYYY') as memo_date,
            memo_entry.amount as chk_amt,
            memo_bills.amount as memo_amt,
            memo_bills.type as memo_type
        FROM unused_parts
        JOIN memo_entry ON memo_entry.id = unused_parts.memo_id
        JOIN memo_bills ON memo_entry.id = memo_bills.memo_id
        WHERE memo_bills.type = 'PR'
        ORDER BY memo_entry.register_date, memo_entry.memo_number;
    """.format(where_clause)

    result = execute_query(query)
    return result["result"]

def get_partial_payment(supplier_id: int, party_id: int) -> List[Dict]:
    """
    Returns the partial payment without bill between the party and supplier.
    Single supplier-party version that calls the bulk version for consistency.
    """
    return get_partial_payment_bulk([supplier_id], [party_id])

def get_partial_payment_by_memo_id(memo_id: int) -> Dict: 
    query = "select id, memo_id, used from part_payments where memo_id = '{}'".format(memo_id)
    response = execute_query(query)

    if len(response["result"]) > 1 or len(response["result"]) == 0:
        raise DataError(f"More than one party payment added with memo_id: {memo_id}")
    
    return response["result"][0]
