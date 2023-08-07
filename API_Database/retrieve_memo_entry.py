from __future__ import annotations
from typing import Union, List
from datetime import datetime, timedelta
import datetime
from typing import Dict
from Exceptions import DataError
from psql import db_connector, execute_query
from API_Database.utils import parse_date
from API_Database.retrieve_partial_payment import get_partial_payment
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


def get_memo_bill_id(memo_id: int, bill_number: int, type: str, amount: int) -> Dict:

    memo_bills = Table('memo_bills')
    query = Query.from_(memo_bills).select(
        memo_bills.id).where((memo_bills.memo_id == memo_id) &
                             (memo_bills.bill_number == bill_number) &
                             (memo_bills.type == type) &
                             (memo_bills.amount == amount))
    sql = query.get_sql()
    response = execute_query(sql)
    if len(response["result"]) == 0:
        raise (DataError(
            f"No memo bill found with memo_id: {memo_id}, bill_number: {bill_number}, type: {type}, amount: {amount}"))
    return response["result"][0]["id"]


def get_memo_bills_by_id(memo_id: int) -> Dict:

    # Open a new connection
    db, cursor = db_connector.cursor(True)

    query = "select id, bill_number, type, amount from memo_bills where memo_id = '{}'".format(
        memo_id)

    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    return data


def get_total_memo_entity(supplier_id: int,
                          party_id: int,
                          start_date: datetime.datetime,
                          end_date: datetime.datetime,
                          memo_type: str):

    # Handle the case if memo_type is "PR"
    if memo_type == "PR":
        result = get_partial_payment(supplier_id, party_id)
        total_amount = 0
        for row in result:
            total_amount += row["memo_amt"]
        return total_amount

    memo_entry = Table('memo_entry')
    memo_bills = Table('memo_bills')

    # Creating the base query
    query = Query.from_(memo_bills).select(
        fn.Sum(memo_bills.amount).as_('total_amount'))

    # Joining memo_bills with memo_entry to filter the bills based on supplier_id, party_id, and type
    query = query.join(memo_entry).on(memo_bills.memo_id == memo_entry.id)

    # Adding the WHERE conditions
    query = query.where(memo_entry.supplier_id == supplier_id)
    query = query.where(memo_entry.party_id == party_id)
    query = query.where(memo_bills.type == memo_type)
    query = query.where(memo_entry.register_date.between(start_date, end_date))

    # Executing the query
    db, cursor = db_connector.cursor(True)
    cursor.execute(query.get_sql())
    result = cursor.fetchall()

    # If the sum is None, return 0 else return integer value of sum
    total_amount = result[0]["total_amount"]
    result = 0 if total_amount is None else int(total_amount)

    # Closing the connection
    db.close()
    return result


def generate_memo_total(supplier_ids: Union[int, List[int]],
                        party_ids: Union[int, List[int]],
                        start_date: datetime,
                        end_date: datetime,
                        memo_type: str):
    """
    Generates the total for the given supplier_ids and party_ids for memo_bills

    Parameters:
    supplier_ids (Union[int, List[int]]): Supplier IDs to consider for total calculation
    party_ids (Union[int, List[int]]): Party IDs to consider for total calculation
    start_date (datetime): Start date for filtering memo_bills based on register_date
    end_date (datetime): End date for filtering memo_bills based on register_date
    memo_type (str): Type of memo_bills to consider for total calculation

    Returns:
    int: The calculated total for memo_bills based on the provided parameters
    """

    # Handling single supplier_id and party_id
    if isinstance(supplier_ids, int):
        supplier_ids = [supplier_ids]
    if isinstance(party_ids, int):
        party_ids = [party_ids]

    # Handling date
    if isinstance(start_date, str):
        start_date = parse_date(start_date)
    if isinstance(end_date, str):
        end_date = parse_date(end_date)

    # Use calculate_memo_totals function and find the total for each supplier_id, party_id, and memo_type
    total = 0
    for supplier_id in supplier_ids:
        for party_id in party_ids:
            total += get_total_memo_entity(supplier_id,
                                           party_id, start_date, end_date, memo_type)
    return total
