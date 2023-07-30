"""
==== Description ====
This class is used to represent a register entry. A register entry is made when
the bill for an order is received.

"""

from __future__ import annotations
import datetime
from typing import List, Dict
from API_Database import insert_register_entry, update_register_entry, utils
from Exceptions import DataError


class RegisterEntry:
    """
    A class that represents a register entry


    ===Attributes===

    bill_number: a unique number that links a RegisterEntry to a MemoEntry
    amount: the amount for which the party has received an order
    date: the date when the bill is received
    supplier: the full name of the supplier
    party: the full name of the party

    """

    supplier_id: int
    party_id: int
    register_date: datetime
    amount: int
    bill_number: int
    date: datetime
    status: str  
    gr_amount: int
    deduction: int
    partial_amount: int

    def __init__(self,
                 bill_number: int,
                 amount: int,
                 supplier_id: int,
                 party_id: int,
                 register_date: str,
                 status: str = "N",
                 gr_amount: int = 0,
                 deduction: int = 0,
                 partial_amount: int = 0,
                 *args,
                 **kwargs
                 ) -> None:

        self.bill_number = bill_number
        self.amount = amount
        self.supplier_id = supplier_id
        self.party_id = party_id
        self.register_date = utils.parse_date(register_date)
        self.gr_amount = gr_amount
        self.deduction = deduction
        self.status = status
        self.partial_amount = partial_amount
        self.pending_amount = self.amount - self.gr_amount - \
            self.deduction - self.partial_amount

    def status_updater(self):

        if self.partial_amount == 0 and self.gr_amount == 0:
            self.status = "N"

        elif self.partial_amount != 0:
            if self.gr_amount != 0:
                self.status = "PG"
            else:
                self.status = "P"

        elif self.gr_amount != 0:
            self.status = "G"

        update_register_entry.update_register_entry_data(self)

    def pending_updater(self):
        self.pending_amount = self.amount - self.gr_amount - \
            self.deduction - self.partial_amount

    @classmethod
    def from_dict(cls, data: Dict) -> RegisterEntry:

        # List of attribute names to be converted to integers
        int_attributes = ["bill_number",
                          "amount",
                          "supplier_id",
                          "party_id",
                          "gr_amount",
                          "deduction",
                          "partial_amount"]

        # Convert the necessary integer attributes from strings to integers
        for attr in int_attributes:
            if attr in data:
                data[attr] = int(data[attr])

        return RegisterEntry(**data)

    @classmethod
    def add(cls, data: Dict) -> Dict:
        register_entry = cls.from_dict(data)
        if insert_register_entry.check_new_register(register_entry):
            return insert_register_entry.insert_register_entry(register_entry)
        else:
            raise DataError({"status": "error",
                             "message": "Duplicate Bill Number",
                             "input_errors": {"bill_number": {"status": "error", "message": "Bill number already exists"}}})
