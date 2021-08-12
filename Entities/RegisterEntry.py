"""
==== Description ====
This class is used to represent a register entry. A register entry is made when
the bill for an order is received.

"""

from __future__ import annotations
import sys
sys.path.append("../")
from API_Database import insert_register_entry, update_register_entry
from typing import List, Dict
import datetime


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

    bill_number: int
    amount: int
    date: datetime
    supplier_name: str
    party_name: str
    gr_amount: int

    def __init__(self, bill: int, amount: int, supplier_id: int, party_id: int,
                 date: str) -> None:

        self.bill_number = bill
        self.amount = amount
        self.supplier_id = supplier_id
        self.party_id = party_id
        try:
            self.date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            self.date = datetime.datetime.strptime(date, "%d/%m/%Y")

        # Deduction AMOUNT and Deduction PERCENT
        self.gr_amount = 0
        self.deduction = 0

        self.status = "N"
        self.part_payment = 0
        self.pending_amount = self.amount - self.gr_amount - self.deduction - self.part_payment
    
    def status_updater(self):

        if self.part_payment == 0 and self.gr_amount == 0:
            self.status = "N"
        
        elif self.part_payment != 0:
            if self.gr_amount != 0:
                self.status = "PG"
            else: 
                self.status = "P"
        
        elif self.gr_amount != 0:
            self.status = "G"
        
        update_register_entry.update_register_entry_data(self)
    
    def pending_updater(self):
        self.pending_amount = self.amount - self.gr_amount - self.deduction - self.part_payment



def call(bill: int, amount: int, supplier: Dict, party: Dict,  date: str) -> RegisterEntry:
    register = RegisterEntry(bill, amount, int(supplier["id"]), int(party["id"]), date)
    if insert_register_entry.check_new_register(register):
        insert_register_entry.insert_register_entry(register)
    return register

def create(bill: int, amount: int, supplier: Dict, party: Dict,  date: str) -> Dict:
    register = RegisterEntry(bill, amount, int(supplier["id"]), int(party["id"]), date)
    if insert_register_entry.check_new_register(register):
        insert_register_entry.insert_register_entry(register)
        return {"status": "okay"}
    return {"status": "error", "bill_num": {"error": True, "message": "Duplicate Bill Number"}}


def create_instance(data: Dict)  -> RegisterEntry:

    bill_number = int(data["bill_number"])
    amount = int(data["amount"])
    supplier_id = int(data["supplier_id"])
    party_id = int(data["party_id"])
    date = data["register_date"]

    register = RegisterEntry(bill_number, amount, supplier_id, party_id, date)

    register.gr_amount = int(data["gr_amount"])
    register.deduction = int(data["deduction"])
    register.status = data["status"]
    register.part_payment = int(data["partial_amount"])
    return register
    








