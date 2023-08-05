from __future__ import annotations
from typing import Dict
from psql import db_connector, execute_query
from API_Database import retrieve_memo_entry
from Entities import MemoEntry, MemoBill
from .update_partial_amount import update_part_payment
from Exceptions import DataError
from pypika import Query, Table


def insert_memo_entry(entry: MemoEntry) -> Dict:

    # Insert Memo Entry using pypika
    status = insert_memo(entry)

    # Get Memo ID
    memo_id = retrieve_memo_entry.get_id_by_memo_number(entry.memo_number,
                                                        entry.supplier_id,
                                                        entry.party_id)

    # Insert Memo Bills
    for bill in entry.memo_bills:
        status = insert_memo_bill(bill, memo_id)

    # Insert Memo Payments
    for payment in entry.payment:
        payment["memo_id"] = memo_id
        status = insert_memo_payment(payment)

    if entry.mode == "Full":
        for part_memo_id in entry.part_payment:
            status = update_part_payment(entry.supplier_id,
                                         entry.party_id,
                                         memo_id=part_memo_id,
                                         use_memo_id=memo_id)

        return status

    elif entry.mode == "Part":
        return insert_part_memo(entry, memo_id)

    else:
        raise DataError("Invalid Memo Type")


def insert_memo(entry: MemoEntry) -> None:
    """
    Insert a memo_entry into the memo_entry table.
    """

    # Define the table
    memo_entry_table = Table('memo_entry')

    # Build the INSERT query using Pypika
    insert_query = Query.into(memo_entry_table).columns(
        'supplier_id',
        'party_id',
        'memo_number',
        'register_date',
        'amount',
        'gr_amount',
        'deduction'
    ).insert(
        entry.supplier_id,
        entry.party_id,
        entry.memo_number,
        entry.register_date,
        entry.amount,
        entry.gr_amount,
        entry.deduction
    )

    # Get the raw SQL query and parameters from the Pypika query
    sql = insert_query.get_sql()

    # Execute the query
    return execute_query(sql)


def insert_memo_bill(entry: MemoBill, memo_id: int) -> None:
    """
    Insert all the bills attached to the same memo number.
    """
    memo_bills_table = Table('memo_bills')
    insert_query = Query.into(memo_bills_table).columns(
        'memo_id',
        'bill_number',
        'type',
        'amount'
    ).insert(
        memo_id,
        entry.bill_number,
        entry.type,
        entry.amount
    )

    sql = insert_query.get_sql()
    return execute_query(sql)


def insert_memo_payment(payment: Dict) -> None:
    """
    Add the memo paymentns for the given memo_entry
    """

    memo_payments_table = Table('memo_payments')
    insert_query = Query.into(memo_payments_table).columns(
        'memo_id',
        'bank_id',
        'cheque_number'
    ).insert(
        payment["memo_id"],
        payment["bank_id"],
        payment["cheque_number"]
    )
    sql = insert_query.get_sql()
    return execute_query(sql)


def insert_part_memo(entry: MemoEntry, memo_id) -> None:
    """
    Insert all the bills attached to the same memo number.
    """

    part_payments_table = Table('part_payments')
    insert_query = Query.into(part_payments_table).columns(
        'supplier_id',
        'party_id',
        'memo_id'
    ).insert(
        entry.supplier_id,
        entry.party_id,
        memo_id
    )

    sql = insert_query.get_sql()
    return execute_query(sql)
