"""
==== Description ====
This class is used to represent a bill in a memo_entry.

"""

from __future__ import annotations
from typing import List, Dict
from API_Database import insert_memo_entry

class MemoBill:

    """Create a memo for a bill."""

    def __init__(self, memo_id: int, bill_number: int, amount: int, memo_type: str) -> None:

        self.memo_id = memo_id
        self.bill_number = bill_number
        self.amount = amount
        self.type = memo_type


def call(obj: Dict) -> None:
    """
    Create a memo bill and insert it into the database.
    """
    bill = MemoBill(**obj)
    insert_memo_entry.insert_memo_bills(bill)

