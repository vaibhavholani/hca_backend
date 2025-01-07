from __future__ import annotations
from typing import Union, List, Optional
from datetime import datetime, timedelta
import datetime
from typing import Dict
from Exceptions import DataError
from psql import db_connector, execute_query
from API_Database.utils import parse_date, sql_date
from API_Database.retrieve_partial_payment import get_partial_payment
from API_Database.retrieve_partial_payment import get_partial_payment_bulk
from pypika import Query, Table, Field, functions as fn
import sys
sys.path.append("../")


def check_new_memo(memo_number: int,
                   date: datetime,
                   *args,
                   **kwargs) -> bool:
    """
    Check if the memo already exists.
    """

    query = "select register_date, supplier_id, party_id from memo_entry where memo_number = '{}' order by 1 DESC".format(
        memo_number)
    response = execute_query(query)
    result = response["result"]

    if len(result) > 1:
        raise DataError(
            f"Error with memo_number {memo_number}, more than one entries in memo_entry.")
    if len(result) == 0:
        return True

    memo = result[0]
    if (date - memo["register_date"]).days >= 30:
        return True

    return False


def check_add_memo(memo_number: int, memo_date: str) -> bool:
    """
    Check if the memo already exists.
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    query = "select register_date from memo_entry where memo_number = '{}' order by 1 DESC".format(
        memo_number)
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    if len(data) == 0:
        return True

    # if (memo_date - data[0][0]).days >= 365:
    #     return True
    return False


def get_memo_entry_id(supplier_id: int, party_id: int, memo_number: int) -> int:
    """
    Get the memo_id using memo_number, supplier_id and party_id
    """

    query = "select id from memo_entry where memo_number = {} AND supplier_id = {} AND party_id = {} " \
            "order by register_date DESC;".format(
                memo_number, supplier_id, party_id)

    response = execute_query(query)

    if len(response["result"]) == 0:
        raise (DataError(
            f"No memo entry found with memo_number: {memo_number}, supplier_id: {supplier_id}, party_id: {party_id}"))
    elif len(response["result"]) > 1:
        raise (DataError(
            f"Multiple memo entries found with memo_number: {memo_number}, supplier_id: {supplier_id}, party_id: {party_id}"))
    
    return int(response["result"][0]["id"])


def get_memo_bill_id(memo_id: int, bill_id: Optional[int], type: str, amount: int) -> int:
    memo_bills = Table('memo_bills')
    
    # Start building the query
    query = Query.from_(memo_bills).select(memo_bills.id).where(
        (memo_bills.memo_id == memo_id) &
        (memo_bills.type == type) &
        (memo_bills.amount == amount)
    )
    
    # Conditionally add bill_id to the query if it's not None
    if bill_id is not None:
        query = query.where(memo_bills.bill_id == bill_id)

    sql = query.get_sql()
    
    response = execute_query(sql)
    
    # Handle no results
    if len(response["result"]) == 0:
        raise DataError(
            f"No memo bill found with memo_id: {memo_id}, bill_id: {bill_id}, type: {type}, amount: {amount}"
        )
    
    return response["result"][0]["id"]




def get_memo_bills_by_id(memo_id: int) -> Dict:
    memo_bills = Table('memo_bills')
    query = Query.from_(memo_bills).select(
        memo_bills.id,
        memo_bills.bill_id,
        memo_bills.type,
        memo_bills.amount
    ).where(memo_bills.memo_id == memo_id).orderby(memo_bills.bill_id)
    sql = query.get_sql()
    response = execute_query(sql)
    return response["result"]



def get_memo_entry(memo_id: int) -> Dict:
    # Define tables
    memo_entry_table = Table('memo_entry')
    memo_payments_table = Table('memo_payments')
    memo_bills_table = Table('memo_bills')
    bank_table = Table('bank')
    register_entry_table = Table('register_entry')
    part_payments_table = Table('part_payments')

    # Fetch basic memo data
    select_query = Query.from_(memo_entry_table).select("*").where(memo_entry_table.id == memo_id)
    memo_data = execute_query(select_query.get_sql())["result"][0]

    # Fetch associated payments
    select_query = (
        Query.from_(memo_payments_table)
        .join(bank_table)
        .on(memo_payments_table.bank_id == bank_table.id)
        .select(memo_payments_table.bank_id, bank_table.name.as_('bank_name'), memo_payments_table.cheque_number)
        .where(memo_payments_table.memo_id == memo_id)
    )
    payments_data = execute_query(select_query.get_sql())["result"]

    payments = [{'bank_id': p["bank_id"], 'bank_name': p["bank_name"], 'cheque_number': p["cheque_number"]} for p in payments_data]

    # Fetch associated bills
    select_query = (
        Query.from_(memo_bills_table)
        .left_join(register_entry_table)
        .on(memo_bills_table.bill_id == register_entry_table.id)
        .select(
            memo_bills_table.id,
            memo_bills_table.bill_id,
            register_entry_table.bill_number,
            memo_bills_table.type,
            memo_bills_table.amount
        )
        .where(memo_bills_table.memo_id == memo_id)
        .orderby(register_entry_table.bill_number)
    )
    bills_data = execute_query(select_query.get_sql())["result"]

    # Handle cases where bill_number is None
    for bill in bills_data:
        if bill['bill_number'] is None:
            bill['bill_number'] = -1  # Or any placeholder value or message

    # Determine the mode based on bills_data
    mode = "Full"  # default to Full
    for bill in bills_data:
        if bill["type"] == "PR":
            mode = "Part"
            break
    
    # If the memo is of type 'Full', fetch associated part payments
    part_payments = []
    if mode == "Full":
        select_query = Query.from_(part_payments_table).select("*").where(part_payments_table.use_memo_id == memo_id)
        part_payments_data = execute_query(select_query.get_sql())["result"]
        part_payments = [p["memo_id"] for p in part_payments_data]
    
    # Construct the final data dict
    result = {
        "id": memo_data["id"],
        "memo_number": memo_data["memo_number"],
        "supplier_id": memo_data["supplier_id"],
        "party_id": memo_data["party_id"],
        "amount": memo_data["amount"],
        "gr_amount": memo_data.get("gr_amount", 0),
        "deduction": memo_data.get("deduction", 0),
        "register_date": sql_date(memo_data["register_date"]),
        "mode": mode,
        "memo_bills": bills_data,
        "payment": payments
    }
    
    if part_payments:
        result["selected_part"] = part_payments
    
    return result


def get_all_memo_entries(**kwargs): 
    """
    Get all memo entries only from memo_entry table
    Designed to use for the view menu filtering
    """
    # create query to get all data from regsiter entry using pypika
    memo_entry_table = Table('memo_entry')
    select_query = Query.from_(memo_entry_table).select(
        memo_entry_table.id,
    )

    if "supplier_id" in kwargs:
        supplier_id = int(kwargs["supplier_id"])
        select_query = select_query.where(
            (memo_entry_table.supplier_id == supplier_id)
        )

    if "party_id" in kwargs:
        party_id = int(kwargs["party_id"])
        select_query = select_query.where(
            (memo_entry_table.party_id == party_id)
        )
    
    # Get the raw SQL query from the Pypika query
    sql= select_query.get_sql()

    # Execute the query and fetch data from the database
    response = execute_query(sql)

    memo_entries = response["result"]
    memo_entries_json: List[Dict] = []

    # Fetch json for all valid memo entries
    for memo_entry in memo_entries:
        memo_id = memo_entry["id"]
        memo_entries_json.append(get_memo_entry(memo_id))
    
    return memo_entries_json

def get_total_memo_entity_bulk(supplier_ids: List[int],
                              party_ids: List[int],
                              start_date: datetime.datetime,
                              end_date: datetime.datetime,
                              memo_type: str,
                              supplier_all: bool = False,
                              party_all: bool = False):
    """
    Get total memo amount for multiple suppliers and parties in one query.
    Optimized version that fetches data in bulk when all suppliers/parties are selected.
    """
    # Handle the case if memo_type is "PR"
    if memo_type == "PR":
        
        result = get_partial_payment_bulk(supplier_ids, party_ids, supplier_all, party_all)
        return sum(row["memo_amt"] for row in result)

    # Build WHERE clause based on all flags
    where_clauses = []

    # Add supplier filter only if not all suppliers
    if not supplier_all and supplier_ids:
        supplier_ids_str = ','.join(map(str, supplier_ids))
        where_clauses.append(f"memo_entry.supplier_id IN ({supplier_ids_str})")

    # Add party filter only if not all parties
    if not party_all and party_ids:
        party_ids_str = ','.join(map(str, party_ids))
        where_clauses.append(f"memo_entry.party_id IN ({party_ids_str})")

    # Always add type and date range filters
    where_clauses.extend([
        f"memo_bills.type = '{memo_type}'",
        f"memo_entry.register_date >= '{start_date}'",
        f"memo_entry.register_date <= '{end_date}'"
    ])

    where_clause = " AND ".join(where_clauses)

    query = """
        SELECT COALESCE(SUM(memo_bills.amount), 0) as total_amount
        FROM memo_bills
        JOIN memo_entry ON memo_bills.memo_id = memo_entry.id
        WHERE {}
    """.format(where_clause)

    result = execute_query(query)
    return int(result["result"][0]["total_amount"])

def generate_memo_total(supplier_ids: Union[int, List[int]],
                       party_ids: Union[int, List[int]],
                       start_date: datetime,
                       end_date: datetime,
                       memo_type: str,
                       supplier_all: bool = False,
                       party_all: bool = False):
    """
    Generates the total for the given supplier_ids and party_ids for memo_bills.
    Uses bulk query for better performance.
    """
    # Convert single IDs to lists
    if isinstance(supplier_ids, int):
        supplier_ids = [supplier_ids]
    if isinstance(party_ids, int):
        party_ids = [party_ids]

    # Handle date formats
    if isinstance(start_date, str):
        start_date = parse_date(start_date)
    if isinstance(end_date, str):
        end_date = parse_date(end_date)

    # Use bulk query to get total
    return get_total_memo_entity_bulk(
        supplier_ids, party_ids, 
        start_date, end_date, 
        memo_type,
        supplier_all=supplier_all,
        party_all=party_all
    )
