"""
==== Description ====
This class is used to represent a bill in a memo_entry.

"""

from __future__ import annotations
from typing import List
from API_Database import insert_memo_entry

class MemoBill:

    """Create a memo for a bill."""

    def __init__(self, memo_id: int, bill_number: int, amount: int, memo_type: str) -> None:

        self.memo_id = memo_id
        self.bill_number = bill_number
        self.amount = amount
        self.type = memo_type


def call(memo_id: int, bill_number: int, amount: int, memo_type: str) -> None:
    """
    Create a memo bill and insert it into the database.
    """
    bill = MemoBill(memo_id, bill_number, amount, memo_type)
    insert_memo_entry.insert_memo_bills(bill)

