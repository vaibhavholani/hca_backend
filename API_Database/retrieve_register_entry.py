from __future__ import annotations
from typing import List, Union, Tuple, Dict
from psql import db_connector, execute_query
from API_Database.utils import parse_date, sql_date
from datetime import datetime, timedelta
from pypika import Query, Table, Field, functions as fn
from Exceptions import DataError


def get_all_register_entries(**kwargs):
    """
    Get all register entries and also use 
    """
    # create query to get all data from regsiter entry using pypika
    register_entry_table = Table('register_entry')
    select_query = Query.from_(register_entry_table).select(
        register_entry_table.id,
        register_entry_table.supplier_id,
        register_entry_table.party_id,
        register_entry_table.bill_number,
        fn.ToChar(register_entry_table.register_date,
                  'YYYY-MM-DD').as_("register_date"),
        fn.Cast(register_entry_table.amount, "integer").as_("amount"),
        register_entry_table.partial_amount,
        register_entry_table.status,
        register_entry_table.deduction,
        register_entry_table.gr_amount
    )

    if "supplier_id" in kwargs:
        supplier_id = int(kwargs["supplier_id"])
        select_query = select_query.where(
            (register_entry_table.supplier_id == supplier_id)
        )

    if "party_id" in kwargs:
        party_id = int(kwargs["party_id"])
        select_query = select_query.where(
            (register_entry_table.party_id == party_id)
        )

    # Get the raw SQL query from the Pypika query
    sql = select_query.get_sql()

    # Execute the query and fetch data from the database
    response = execute_query(sql)
    return response["result"]


def get_register_entry_by_id(id: int) -> Dict:
    register_entry_table = Table('register_entry')
    select_query = Query.from_(register_entry_table).select(
        register_entry_table.supplier_id,
        register_entry_table.party_id,
        register_entry_table.bill_number,
        fn.ToChar(register_entry_table.register_date,
                  'YYYY-MM-DD').as_("register_date"),
        fn.Cast(register_entry_table.amount, "integer").as_("amount"),
        register_entry_table.partial_amount,
        register_entry_table.status,
        register_entry_table.deduction,
        register_entry_table.gr_amount
    ).where(
        (register_entry_table.id == id)
    )
    sql = select_query.get_sql()
    data = execute_query(sql)
    if len(data["result"]) == 0:
        raise DataError(f"No Register Entry with id: {id}")
    if len(data["result"]) != 1:
        raise DataError(f"Multiple Register Entries with same id: {id}")
    return data["result"][0]


def get_register_entry_id(supplier_id: int, party_id: int, bill_number: int, register_date: str) -> int:
    """
    Returns primary key id of the register entry
    """

    query = "select id from register_entry where bill_number = '{}' AND supplier_id = '{}' AND party_id = '{}' AND register_date = '{}'" .\
        format(bill_number, supplier_id, party_id, register_date)

    result = db_connector.execute_query(query, False)
    data = result["result"]

    if len(data) == 0:
        raise DataError(
            f"No Register Entry with supplier_id: {supplier_id}, party_id: {party_id}, bill_number: {bill_number}, register_date: {register_date}")
    if len(data) != 1:
        raise DataError(
            f"Multiple Register Entries with same supplier_id: {supplier_id}, party_id: {party_id}, bill_number: {bill_number}, register_date: {register_date}")

    return data[0][0]

# @deprecated


def check_unique_bill_number(supplier_id: int, party_id: int, bill_number: int, date: str) -> bool:
    """
    Check if the bill number if unique
    """
    db, cursor = db_connector.cursor()

    date = parse_date(date)

    query = "select id, register_date from register_entry where " \
            "bill_number = '{}' AND supplier_id = '{}' AND party_id = '{}'". \
        format(bill_number, supplier_id, party_id)
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()

    if len(data) == 0:
        return True

    if (date - data[0][1]).days >= 2:
        return True

    return False


def get_pending_bills(supplier_id: int, party_id: int) -> List[Dict]:
    """
    Returns a list of all pending bill numbers between party and supplier.
    """

    query = """
        SELECT 
            id, 
            bill_number, 
            status, 
            CAST(floor(partial_amount) AS INTEGER) as partial_amount, 
            CAST(floor(amount) AS INTEGER) as amount, 
            gr_amount, 
            deduction,
            to_char(register_date, 'DD/MM/YY') as register_date
        FROM register_entry 
        WHERE supplier_id = '{}' 
        AND party_id = '{}' 
        AND status != '{}'
        ORDER BY register_date DESC
    """.format(supplier_id, party_id, "F")
    response = execute_query(query)
    result = response["result"]
    return result


def get_register_entry(supplier_id: int, party_id: int, bill_number: int, register_date: datetime) -> Dict:
    """
    Return the register entry associated with the given bill number.
    """

    # Define the table
    register_entry_table = Table('register_entry')
    # Build the SELECT query using Pypika
    select_query = Query.from_(register_entry_table).select(
        register_entry_table.supplier_id,
        register_entry_table.party_id,
        register_entry_table.bill_number,
        register_entry_table.register_date,
        fn.Cast(register_entry_table.amount, "integer").as_("amount"),
        register_entry_table.partial_amount,
        register_entry_table.status,
        register_entry_table.deduction,
        register_entry_table.gr_amount
    ).where(
        (register_entry_table.bill_number == bill_number) &
        (register_entry_table.supplier_id == supplier_id) &
        (register_entry_table.party_id == party_id) &
        (register_entry_table.register_date == register_date)
    )

    # Get the raw SQL query from the Pypika query
    sql = select_query.get_sql()

    # Execute the query and fetch data from the database
    data = execute_query(sql)

    # Convert the fetched data into a list of RegisterEntry objects
    result = data["result"]

    if len(result) == 0:
        raise DataError(f"No Register Entry with bill number: {bill_number}")

    if len(result) != 1:
        raise DataError(
            f"Multiple Register Entries with same bill number: {bill_number}")

    return result[0]


def _pop_dict_keys(pop_dict: dict, keys: List[str]) -> dict:
    """
    Removes keys from the dictionary
    """
    for key in keys:
        pop_dict.pop(key, None)
    return pop_dict


def get_khata_data_by_date_bulk(supplier_ids: List[int], party_ids: List[int], start_date: str, end_date: str, supplier_all: bool = False, party_all: bool = False) -> List[Dict]:
    """
    Returns a list of all bill_number's amount and date between the given dates for multiple suppliers and parties.
    Optimized version that fetches data in bulk when all suppliers/parties are selected.
    """
    # Build WHERE clause based on all flags
    bills_where_clauses = []
    memo_where_clauses = []

    # Add supplier filter only if not all suppliers
    if not supplier_all and supplier_ids:
        supplier_ids_str = ','.join(map(str, supplier_ids))
        bills_where_clauses.append(
            f"register_entry.supplier_id IN ({supplier_ids_str})")
        memo_where_clauses.append(
            f"memo_entry.supplier_id IN ({supplier_ids_str})")

    # Add party filter only if not all parties
    if not party_all and party_ids:
        party_ids_str = ','.join(map(str, party_ids))
        bills_where_clauses.append(
            f"register_entry.party_id IN ({party_ids_str})")
        memo_where_clauses.append(f"memo_entry.party_id IN ({party_ids_str})")

    # Always add date range filter
    bills_where_clauses.extend([
        f"register_date >= '{start_date}'",
        f"register_date <= '{end_date}'"
    ])

    # If no where clauses (all suppliers and all parties), just use date range
    bills_where_clause = " AND ".join(bills_where_clauses)
    memo_where_clause = " AND ".join(
        memo_where_clauses) if memo_where_clauses else "TRUE"

    # Use CTE for better query organization
    query = """
        WITH bills_data AS (
            SELECT 
                register_entry.id as bill_id,
                register_entry.bill_number as bill_no,
                to_char(register_entry.register_date, 'DD/MM/YYYY') as bill_date,
                register_entry.amount::integer as bill_amt,
                register_entry.status as bill_status,
                register_entry.supplier_id as subheader_id,
                register_entry.party_id as header_id,
                register_entry.supplier_id,
                register_entry.party_id
            FROM register_entry
            WHERE {}
            ORDER BY register_entry.register_date, register_entry.bill_number
        ),
        memo_data AS (
            SELECT 
                memo_entry.memo_number as memo_no,
                memo_bills.amount as memo_amt,
                to_char(memo_entry.register_date, 'DD/MM/YYYY') as memo_date,
                memo_entry.amount as chk_amt,
                memo_bills.type as memo_type,
                memo_bills.bill_id,
                memo_entry.supplier_id,
                memo_entry.party_id
            FROM memo_entry
            JOIN memo_bills ON memo_entry.id = memo_bills.memo_id
            WHERE {}
        )
        SELECT 
            b.header_id,
            b.subheader_id,
            b.bill_no,
            b.bill_date,
            b.bill_amt,
            b.bill_status,
            m.memo_no,
            m.memo_amt,
            m.memo_date,
            m.chk_amt,
            m.memo_type,
            b.supplier_id,
            b.party_id,
            b.bill_id
        FROM bills_data b
        LEFT JOIN memo_data m ON b.bill_id = m.bill_id 
        AND b.supplier_id = m.supplier_id 
        AND b.party_id = m.party_id
        ORDER BY b.bill_date, b.bill_no;
    """.format(bills_where_clause, memo_where_clause)

    result = execute_query(query)
    bills_data = result["result"]

    if len(bills_data) == 0:
        return bills_data

    # Process the results to match original format
    data = []
    dummy_memo = {"memo_no": "", "memo_amt": "",
                  "memo_date": "", "chk_amt": "", "memo_type": ""}

    current_bill = None
    for row in bills_data:
        # Remove internal fields used for sorting/joining
        row.pop("supplier_id", None)
        row.pop("party_id", None)
        row.pop("bill_id", None)

        if current_bill != (row["bill_no"], row["bill_date"]):
            # New bill entry
            current_bill = (row["bill_no"], row["bill_date"])
            if row["memo_no"]:
                # Bill with memo
                data.append(row)
            else:
                # Bill without memo
                bill_data = {k: v for k, v in row.items() if k not in [
                    "memo_no", "memo_amt", "memo_date", "chk_amt", "memo_type"]}
                data.append({**bill_data, **dummy_memo})
        else:
            # Additional memo for same bill
            memo_data = {k: v for k, v in row.items() if k in [
                "memo_no", "memo_amt", "memo_date", "chk_amt", "memo_type"]}
            if any(memo_data.values()):  # Only add if memo has data
                data.append(memo_data)

    return data


def get_khata_data_by_date(supplier_id: int, party_id: int, start_date: str, end_date: str, **kwargs) -> List[Dict]:
    """
    Returns a list of all bill_number's amount and date between the given dates.
    Single supplier-party version that calls the bulk version for consistency.
    """
    data = get_khata_data_by_date_bulk(
        [supplier_id], [party_id], start_date, end_date)
    # Remove header_id and subheader_id for backward compatibility
    for row in data:
        row.pop("header_id", None)
        row.pop("subheader_id", None)
    return data


def get_supplier_register_data_bulk(supplier_ids: List[int], party_ids: List[int], start_date: str, end_date: str, supplier_all: bool = False, party_all: bool = False) -> List[Dict]:
    """
    Returns a list of all bill_number's amount and date for multiple suppliers and parties.
    Optimized version that fetches data in bulk when all suppliers/parties are selected.
    """
    # Build WHERE clause based on all flags
    where_clauses = []

    # Add supplier filter only if not all suppliers
    if not supplier_all and supplier_ids:
        supplier_ids_str = ','.join(map(str, supplier_ids))
        where_clauses.append(f"supplier_id IN ({supplier_ids_str})")

    # Add party filter only if not all parties
    if not party_all and party_ids:
        party_ids_str = ','.join(map(str, party_ids))
        where_clauses.append(f"party_id IN ({party_ids_str})")

    # Always add date range filter
    where_clauses.extend([
        f"register_date >= '{start_date}'",
        f"register_date <= '{end_date}'"
    ])

    # If no where clauses (all suppliers and all parties), just use date range
    where_clause = " AND ".join(where_clauses)

    query = """
        SELECT 
            register_entry.supplier_id as header_id,
            register_entry.party_id as subheader_id,
            to_char(register_date, 'DD/MM/YYYY') as bill_date,
            party.name as party_name,
            supplier.name as supplier_name,
            bill_number as bill_no,
            amount::integer as bill_amt,
            CASE WHEN status='F' THEN '0'
                 ELSE (amount - (partial_amount)-(gr_amount)-(deduction)) 
            END AS pending_amt,
            status,
            register_entry.supplier_id,
            register_entry.party_id
        FROM register_entry 
        JOIN party ON party.id = register_entry.party_id
        JOIN supplier ON supplier.id = register_entry.supplier_id
        WHERE {}
        ORDER BY supplier_name, party_name, register_date, bill_number;
    """.format(where_clause)

    result = execute_query(query)
    data = result["result"]

    # Remove internal IDs before returning
    for row in data:
        row.pop("supplier_id", None)
        row.pop("party_id", None)

    return data


def get_supplier_register_data(supplier_id: int, party_id: int, start_date: str, end_date: str, **kwargs) -> List[Dict]:
    """
    Returns a list of all bill_number's amount and date.
    Single supplier-party version that calls the bulk version for consistency.
    """
    data = get_supplier_register_data_bulk(
        [supplier_id], [party_id], start_date, end_date)
    # Remove header_id and subheader_id for backward compatibility
    for row in data:
        row.pop("header_id", None)
        row.pop("subheader_id", None)
    return data


def get_payment_list_data_bulk(supplier_ids: List[int], party_ids: List[int], start_date: str, end_date: str, supplier_all: bool = False, party_all: bool = False) -> List[Dict]:
    """
    Get all pending bills info between multiple suppliers and parties.
    Optimized version that fetches data in bulk when all suppliers/parties are selected.
    """
    # Build WHERE clause based on all flags
    where_clauses = []

    # Add supplier filter only if not all suppliers
    if not supplier_all and supplier_ids:
        supplier_ids_str = ','.join(map(str, supplier_ids))
        where_clauses.append(f"supplier_id IN ({supplier_ids_str})")

    # Add party filter only if not all parties
    if not party_all and party_ids:
        party_ids_str = ','.join(map(str, party_ids))
        where_clauses.append(f"party_id IN ({party_ids_str})")

    # Always add date range and status filters
    where_clauses.extend([
        f"register_date >= '{start_date}'",
        f"register_date <= '{end_date}'",
        "status != 'F'"
    ])

    # If no where clauses (all suppliers and all parties), just use date range and status
    where_clause = " AND ".join(where_clauses)

    query = """
        WITH pending_bills AS (
            SELECT 
                register_entry.supplier_id as subheader_id,
                register_entry.party_id as header_id,
                register_entry.bill_number AS bill_no,
                CAST(register_entry.amount AS INTEGER) AS bill_amt,
                TO_CHAR(register_entry.register_date, 'DD/MM/YYYY') AS bill_date,
                (register_entry.amount - register_entry.partial_amount - register_entry.gr_amount - register_entry.deduction) AS pending_amt,
                DATE_PART('day', NOW() - register_entry.register_date)::INTEGER AS days,
                register_entry.status,
                register_entry.id AS bill_id,
                register_entry.supplier_id,
                register_entry.party_id
            FROM register_entry
            WHERE {}
            ORDER BY register_date DESC
        )
        SELECT 
            pb.header_id,
            pb.subheader_id,
            pb.bill_no,
            pb.bill_amt,
            pb.bill_date,
            pb.pending_amt,
            pb.days,
            pb.status,
            COALESCE(me.memo_number::text, '') as part_no,
            COALESCE(TO_CHAR(me.register_date, 'DD/MM/YYYY'), '') as part_date,
            COALESCE(mb.amount::text, '') as part_amt,
            pb.supplier_id,
            pb.party_id,
            pb.bill_id
        FROM pending_bills pb
        LEFT JOIN memo_bills mb ON pb.bill_id = mb.bill_id
        LEFT JOIN memo_entry me ON mb.memo_id = me.id
        ORDER BY pb.bill_date DESC;
    """.format(where_clause)

    result = execute_query(query)
    bills_data = result["result"]

    if not bills_data:
        return bills_data

    # Process results to match original format
    data = []
    for bill in bills_data:
        # Remove internal IDs
        bill.pop("supplier_id", None)
        bill.pop("party_id", None)
        bill.pop("bill_id", None)

        # Convert None to empty string for part fields
        bill["part_no"] = bill["part_no"] or ""
        bill["part_date"] = bill["part_date"] or ""
        bill["part_amt"] = bill["part_amt"] or ""

        data.append(bill)

    return data


def get_payment_list_data(supplier_id: int, party_id: int, start_date: str, end_date: str, **kwargs) -> List[Dict]:
    """
    Get all pending bills info between supplier and party.
    Single supplier-party version that calls the bulk version for consistency.
    """
    data = get_payment_list_data_bulk(
        [supplier_id], [party_id], start_date, end_date)
    # Remove header_id and subheader_id for backward compatibility
    for row in data:
        row.pop("header_id", None)
        row.pop("subheader_id", None)
    return data


def get_payment_list_summary_data(supplier_id: int, party_id: int, start_date: str, end_date: str) -> List[Tuple]:
    """
    Get summarised data for all payment lists summary
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    # Find amount less than 40 days
    query1 = "select SUM(amount), SUM(amount) - SUM(partial_amount) - SUM(gr_amount) - SUM(deduction)" \
             "from register_entry where party_id = '{}' AND supplier_id = '{}'" \
             " AND status != 'F' AND DATE_PART('day', NOW() - register_date) < 40 AND register_date >= '{}' " \
             "AND register_date <= '{}';".format(
                 party_id, supplier_id, start_date, end_date)

    # Find amount between 40 and 70 days
    query2 = "select SUM(amount), SUM(amount) - SUM(partial_amount) - SUM(gr_amount) - SUM(deduction) " \
             "from register_entry where party_id = '{}' AND supplier_id = '{}' " \
             "AND status != 'F' AND DATE_PART('day', NOW() - register_date) BETWEEN 40 AND 70 AND register_date >= '{}' AND " \
             "register_date <= '{}';".format(
                 party_id, supplier_id, start_date, end_date)

    # Find amount more than 70 days
    query3 = "select SUM(amount), SUM(amount) - SUM(partial_amount) - SUM(gr_amount) - SUM(deduction) " \
             "from register_entry where party_id = '{}' AND supplier_id = '{}' " \
             "AND status != 'F' AND 70 < DATE_PART('day', NOW() - register_date) AND register_date >= '{}' " \
             "AND register_date <= '{}';".format(
                 party_id, supplier_id, start_date, end_date)

    cursor.execute(query1)
    data1 = cursor.fetchall()
    if data1[0][0] is None:
        data1 = [("-", "-", "-")]

    cursor.execute(query2)
    data2 = cursor.fetchall()

    if data2[0][0] is None:
        data2 = [("-", "-", "-")]

    cursor.execute(query3)
    data3 = cursor.fetchall()

    if data3[0][0] is None:
        data1 = [("-", "-", "-")]

    data = data1 + data2 + data3
    db.close()
    return data


def grand_total_work(supplier_id: int, party_id: int, start_date: str, end_date: str) -> int:
    """
    Get the grand total for each porty for the selected suppliers
    """
    # Open a new connection
    db, cursor = db_connector.cursor()

    query = "select SUM(amount) from register_entry where " \
            "party_id = '{}' AND supplier_id = '{}' AND " \
            "register_date >= '{}' AND register_date <= '{}';".format(
                party_id, supplier_id, start_date, end_date)

    cursor.execute(query)
    data = cursor.fetchall()
    db.close()

    if data[0][0] is None:
        return 0
    return data[0][0]


def legacy_no_memo(curr_pld: Tuple) -> List[Tuple]:
    """
    Returns legacy payment bill with no memos
    """
    if curr_pld[4] < 40:
        bill_tuple = [("-", "-", "-", "-", "-", "-",
                       curr_pld[2], curr_pld[0], curr_pld[3])]
    elif 40 <= curr_pld[4] <= 70:
        bill_tuple = [("-", "-", "-", "-", "-", curr_pld[2],
                       "-", curr_pld[0], curr_pld[3])]
    else:
        bill_tuple = [("-", "-", "-", "-", curr_pld[2],
                       "-", "-", curr_pld[0], curr_pld[3])]

    return bill_tuple


def legacy_one_memo(curr_pld: Tuple, curr_memo: Tuple) -> List[Tuple]:
    """
    Returns legacy payment bill with one memo
    """
    if curr_pld[4] < 40:
        bill_tuple = [(curr_memo[0], curr_memo[1], curr_memo[2],
                       curr_memo[3], "-", "-", curr_pld[2], curr_pld[0], curr_pld[3])]
    elif 40 <= curr_pld[4] <= 70:
        bill_tuple = [(curr_memo[0], curr_memo[1], curr_memo[2],
                       curr_memo[3], "-", curr_pld[2], "-", curr_pld[0], curr_pld[3])]
    else:
        bill_tuple = [(curr_memo[0], curr_memo[1], curr_memo[2],
                       curr_memo[3], curr_pld[2], "-", "-", curr_pld[0], curr_pld[3])]

    return bill_tuple


def legacy_multiple_memo(curr_memo: Tuple) -> List[Tuple]:
    """
    Returns legacy payment bill with multiple memos
    """
    bill_tuple = [(curr_memo[0], curr_memo[1], curr_memo[2],
                   curr_memo[3], "-", "-", "-", "-", "-")]
    return bill_tuple


def legacy_payment_list(supplier_id: int, party_id: int, start_date: str, end_date: str):
    """
    Get the legacy payment list
    """

    # Open a new connection
    db, cursor = db_connector.cursor()

    p_l_d = get_payment_list_data(supplier_id, party_id, start_date, end_date)

    bills_data = [data[0] for data in p_l_d]

    memo_data = []
    for bills in bills_data:
        query_2 = "select memo_entry.memo_number, memo_bills.amount, memo_bills.type, " \
                  "to_char(memo_entry.register_date, 'DD/MM/YYYY') " \
                  "from memo_entry JOIN memo_bills on (memo_entry.id = memo_bills.memo_id) " \
                  "where memo_bills.bill_number = '{}' AND memo_entry.supplier_id = '{}' " \
                  "AND memo_entry.party_id = '{}'; " \
            .format(bills, supplier_id, party_id, start_date, end_date)
        cursor.execute(query_2)
        add_memo_data = cursor.fetchall()
        memo_data.append(add_memo_data)

    legacy_data = []
    for entry in range(len(bills_data)):

        curr_pld = p_l_d[entry]
        curr_memo = memo_data[entry]
        bill_tuples = []
        if len(curr_memo) == 0:
            bill_tuples.extend(legacy_no_memo(curr_pld))
        elif len(curr_memo) == 1:
            bill_tuples.extend(legacy_one_memo(curr_pld, curr_memo[0]))
        else:
            # Add the first entry and fill the rest with spaces
            bill_tuples.extend(legacy_one_memo(curr_pld, curr_memo[0]))
            # Make functions to make execution easier?
            for memos in curr_memo[1:]:
                bill_tuples.extend(legacy_multiple_memo(memos))

        legacy_data.extend(bill_tuples)

    return legacy_data


def get_total_bill_entity_bulk(supplier_ids: List[int], party_ids: List[int], start_date: str, end_date: str, column_name: str, pending: bool = False, days: dict = {}, supplier_all: bool = False, party_all: bool = False) -> int:
    """
    Bulk version of get_total_bill_entity that calculates totals for multiple suppliers and parties in a single query.
    Optimized version that fetches data in bulk when all suppliers/parties are selected.
    """
    # Build WHERE clause based on all flags
    where_clauses = []

    # Add supplier filter only if not all suppliers
    if not supplier_all and supplier_ids:
        supplier_ids_str = ','.join(map(str, supplier_ids))
        where_clauses.append(f"supplier_id IN ({supplier_ids_str})")

    # Add party filter only if not all parties
    if not party_all and party_ids:
        party_ids_str = ','.join(map(str, party_ids))
        where_clauses.append(f"party_id IN ({party_ids_str})")

    # Add date range filter
    where_clauses.extend([
        f"register_date >= '{start_date}'",
        f"register_date <= '{end_date}'"
    ])

    # Add pending status filter if needed
    if pending:
        where_clauses.append("status != 'F'")

    # Add days conditions if provided
    if 'over' in days and 'under' in days:
        where_clauses.append(
            f"DATE_PART('day', NOW() - register_date) >= {days['under']}")
        where_clauses.append(
            f"DATE_PART('day', NOW() - register_date) < {days['over']}")
    elif 'over' in days:
        where_clauses.append(
            f"DATE_PART('day', NOW() - register_date) >= {days['over']}")
    elif 'under' in days:
        where_clauses.append(
            f"DATE_PART('day', NOW() - register_date) < {days['under']}")

    # Combine all WHERE clauses
    where_clause = " AND ".join(where_clauses) if where_clauses else "TRUE"

    # Build and execute query
    query = f"""
        SELECT COALESCE(SUM({column_name}), 0) as total
        FROM register_entry
        WHERE {where_clause}
    """

    result = execute_query(query)
    total = result["result"][0]["total"]

    # Convert to integer if it's a Decimal
    return int(total)


def generate_total(supplier_ids: Union[int, List[int]],
                   party_ids: Union[int, List[int]],
                   start_date: Union[datetime, str],
                   end_date: Union[datetime, str],
                   column_name: str,
                   pending: bool = False,
                   days: dict = {},
                   supplier_all: bool = False,
                   party_all: bool = False) -> int:
    """
    Generates the total for the given supplier_ids and party_ids.
    Uses optimized bulk query instead of iterating through individual supplier-party pairs.

    Args:
        supplier_ids: Single supplier ID or list of supplier IDs
        party_ids: Single party ID or list of party IDs
        start_date: Start date for filtering
        end_date: End date for filtering
        column_name: Name of the column to sum
        pending: If True, only include non-finalized entries
        days: Dict with optional 'over' and 'under' keys for age filtering
        supplier_all: If True, include all suppliers
        party_all: If True, include all parties

    Returns:
        Integer total sum of the specified column
    """
    # Convert single IDs to lists
    if isinstance(supplier_ids, int):
        supplier_ids = [supplier_ids]
    if isinstance(party_ids, int):
        party_ids = [party_ids]

    # Use bulk query to get total in one database call
    return get_total_bill_entity_bulk(
        supplier_ids=supplier_ids,
        party_ids=party_ids,
        start_date=start_date,
        end_date=end_date,
        column_name=column_name,
        pending=pending,
        days=days,
        supplier_all=supplier_all,
        party_all=party_all
    )
