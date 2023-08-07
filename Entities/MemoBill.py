"""
==== Description ====
This class is used to represent a bill in a memo_entry.

"""

from __future__ import annotations
from typing import List, Dict
from API_Database import get_memo_bill_id, get_partial_payment_by_memo_id
from API_Database import delete_by_id
from Exceptions import DataError
from .RegisterEntry import RegisterEntry
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

    def get_id(self, memo_id: int) -> int:
        """
        Get the memo bill id from the database.
        """
        return get_memo_bill_id(memo_id=memo_id,
                                bill_number=self.bill_number,
                                type=self.type,
                                amount=self.amount)

    def undo(self, memo_id: int, supplier_id: int, party_id: int) -> Dict:
        """
        Undo the effect of the memo bill on the register entry.
        """

        # Handle the case when
        if self.type == "PR":
            # Find the part payment
            part_payment = get_partial_payment_by_memo_id(memo_id)
            if part_payment["used"]:
                raise DataError(
                    f"Part Payment {part_payment['memo_number']} is used")
            else:
                ret = delete_by_id(part_payment["id"], "part_payments")
        else:
            # Remove the effect of the memo bill from the register entry
            register_entry = RegisterEntry.retrieve(
                supplier_id, party_id, self.bill_number)
            if self.type == "F":
                register_entry.status = "N"
            elif self.type == "D":
                register_entry.deduction -= self.amount
            elif self.type == "G":
                register_entry.gr_amount -= self.amount
            ret = register_entry.update()
        return ret

    def delete(self, memo_id: int, supplier_id: int, party_id: int) -> Dict:
        """
        Delete the memo bill from the database.
        """

        memo_bill_id = self.get_id(memo_id)

        # remove the effect of the memo bill
        ret = self.undo(memo_id, supplier_id, party_id)

        # Delete the memo bill
        ret = delete_by_id(memo_bill_id, self.table_name)

        return ret

    def __str__(self) -> str:
        return f"Memo Bill: Bill Number: {self.bill_number}, Amount: {self.amount}, Type: {self.type}"
