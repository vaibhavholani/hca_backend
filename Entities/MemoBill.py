"""
==== Description ====
This class is used to represent a bill in a memo_entry.

"""

from __future__ import annotations
from typing import List, Dict
from .Entry import Entry

class MemoBill(Entry):

    """Create a memo for a bill."""

    def __init__(self, bill_number: int, 
                 amount: int, 
                 memo_type: str,
                 table_name: str = "memo_bills") -> None:
        super().__init__(table_name=table_name)
        self.bill_number = bill_number
        self.amount = amount
        self.type = memo_type
    
    def __str__(self) -> str:
        return f"Memo Bill: Bill Number: {self.bill_number}, Amount: {self.amount}, Type: {self.type}"

