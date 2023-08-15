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
                    table_name: str = "memo_bills", 
                    *args,
                    **kwargs) -> None:

        super().__init__(table_name=table_name, *args, **kwargs)
        self.bill_number = bill_number
        self.amount = amount
        self.type = memo_type

    def get_id(self, memo_id: int) -> int:
        """
        Get the memo bill id from the database.
        """
        super_id = super().get_id()
        if super_id is not None: return super_id

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

    @classmethod
    def from_dict(cls, data: Dict, *args, **kwargs) -> MemoBill:
        """Construct a MemoBill instance from a dictionary."""
        # List of attribute names to be converted to integers
        int_attributes = ["bill_number", "amount"]

        # Make sure type is in data and only of type "F", "D", "G", "PR" and then cast it memo_type
        if "type" not in data:
            raise DataError("Memo Bill type not found")
        elif data["type"] not in ["F", "D", "G", "PR"]:
            raise DataError(
                f"Memo Bill type {data['type']} not supported")
        else:
            data["memo_type"] = data["type"]

        data = cls.convert_int_attributes(data, int_attributes)
        # Return the created instance
        return cls(**data)

    def __str__(self) -> str:
        return f"Memo Bill: Bill Number: {self.bill_number}, Amount: {self.amount}, Type: {self.type}"
