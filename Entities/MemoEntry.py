"""
==== Description ====
This class is used to represent a memo entry.

"""

from __future__ import annotations
from typing import List, Dict
import datetime
from API_Database import insert_memo_entry
from API_Database import retrieve_memo_entry
from API_Database import retrieve_partial_payment, insert_partial_payment
from API_Database import  update_memo_entry, update_partial_amount, update_register_entry
from API_Database import retrieve_register_entry
from Entities import RegisterEntry, MemoBill

class MemoEntry:

    """
    A class that represents a memo entry

    ===Attributes===

    amount: the amount for which the party has received an order
    date: the date

    """
    memo_number: int
    supplier_name: str
    party_name: str
    amount: int
    date: datetime
    bank_name: str
    cheque_number: int
    selected_bills: List

    def __init__(self, obj: Dict) -> None:

        self.memo_number = int(obj["memo_number"])
        self.supplier_id = int(obj['supplier_id'])
        self.party_id = int(obj['party_id'])
        self.amount = int(obj['amount'])
        self.mode = obj["memo_type"]
        self.date = (datetime.datetime.strptime(obj['memo_date'], "%Y-%m-%d"))
        self.date_string = self.date
        self.payment_info =[(info["id"], (info["cheque"])) for info in (obj['payment'])] 
        selected_bills = [int(bill["bill_number"]) for bill in obj["selected_bills"]]
        self.selected_bills = retrieve_register_entry.get_register_entry_bill_numbers\
            (self.supplier_id, self.party_id, selected_bills)
        self.insert_memo_database()
        self.memo_id = self.get_memo_id()
        self.credit = int(obj["credit"]) if "credit" in obj else 0
        self.deduction = int(obj["deduction"]) if "deduction" in obj else 0

        # TODO: Need the update the partial being used 
        # TODO: Need to store all information about the way credit is being used
        #       and how much

    def insert_memo_database(self) -> None:
        """
        Adds memo to the database if the memo is new.
        """
        if retrieve_memo_entry.check_add_memo(self.memo_number, self.date_string):
            insert_memo_entry.insert_memo_entry(self)
        else:
            update_memo_entry.update_memo_entry_data(self)
        insert_memo_entry.insert_memo_payemts(self)

    def insert_memo_bill_database(self, bills: RegisterEntry) -> None:
        """
        Adds bills to the attached memo to the database.
        """
        bills.pending_updater()
        update_register_entry.update_register_entry_data(bills)
        amount = self.amount
        if self.mode == "Full":
            amount = bills.pending_amount
        MemoBill.call(self.memo_id, bills.bill_number, amount, self.mode[0].upper())

    def get_memo_id(self) -> int:
        """
        Update memo id once the memo is added into the database.
        """
        return retrieve_memo_entry.get_id_by_memo_number(self.memo_number, self.supplier_id, self.party_id)

    def full_payment(self) -> None:
        """
        Used to complete full payment for bill(s)
        """
        # Loop to update the status of the selected bills
        for bills in self.selected_bills:
            if self.deduction > 0:
                if bills.pending_amount <= self.deduction: 
                    bills.deduction += bills.pending_amount
                    self.deduction -= bills.pending_amount
                    self.database_memo_bill(bills.bill_number, bills.pending_amount, "D")
                else: 
                    bills.deduction += self.deduction
                    self.database_memo_bill(bills.bill_number, self.deduction, "D")
                    self.deduction = 0
                    
            bills.status = "F"
            self.insert_memo_bill_database(bills)

    def partial_payment_bill(self) -> None:
        """
        Used to complete partial payment for bill(s)
        """

        # Loop to update the status of the selected bills

        for bills in self.selected_bills:

            # Updating Bill Status
            if (bills.pending_amount - self.amount <= 0):
                bills.status = "F"
            elif bills.status == "N":
                bills.status = "P"
            elif bills.status == "G":
                bills.status = "PG"
            
            # Updating deductions  
            if self.deduction > 0:
                bills.deduction += self.deduction
                self.database_memo_bill(bills.bill_number, self.deduction, "D")
                self.deduction = 0
            
            # Updating Part payments
            bills.part_payment = bills.part_payment + self.amount
            self.insert_memo_bill_database(bills)

    def database_memo_bill(self, bill_number: int, deduct_amount: int, type: str = 'D'): 
        """
        Store the deductions made in a memo bill
        """
        MemoBill.call(self.memo_id, bill_number, deduct_amount, type)


    def database_partial_payment(self):
        """
        Store partial payments into the database
        """
        if retrieve_partial_payment.get_partial_payment(self.supplier_id, self.party_id) == -1:
            insert_partial_payment.insert_partial_payment(self)
        else:
            update_partial_amount.add_partial_amount(self.supplier_id, self.party_id, self.amount)

        MemoBill.call(self.memo_id, -1, self.amount, "PR")

    def goods_return(self) -> None:
        """
        Adds goods return to supplier party account.
        """

        balance = self.amount
        for bills in self.selected_bills:
            if balance > 0: 
                if (bills.status == "P" or bills.status == "PG"):
                    bills.status = "PG"
                elif bills.status == "N":
                    bills.status = "G"

                if bills.pending_amount >= balance: 
                    bills.gr_amount += balance
                    self.database_memo_bill(bills.bill_number, balance, 'G')
                    balance = 0
                else: 
                    bills.gr_amount += bills.pending_amount
                    balance -= bills.pending_amount
                    self.database_memo_bill(bills.bill_number, bills.pending_amount, "G")
                
                update_register_entry.update_register_entry_data(bills)

    def insert(self):
        """
        Insert the memo entry into the database
        """
        if self.mode == "Full":
            self.full_payment()
        elif self.mode == "Partial":
                self.partial_payment_bill()
        elif self.mode == "Credit":
                self.database_partial_payment()
        else: 
            self.goods_return()
        
        if self.credit > 0:
            update_partial_amount.use_partial_amount(self.supplier_id, self.party_id, self.credit)
            self.database_memo_bill(-1, self.credit, "C")

        update_memo_entry.update_memo_amount(self.memo_id)
            
def call(obj: Dict):

    memo_number = int(obj["memo_number"])
    supplier_id = int(obj['supplier_id'])
    party_id = int(obj['party_id'])
    date = (datetime.datetime.strptime(obj['memo_date'], "%Y-%m-%d"))

    if not (retrieve_memo_entry.check_new_memo(memo_number, date, supplier_id, party_id)):
        return {"status": "error", "memo_number": {"error": True, "message": "Duplicate memo Number for different supplier and party"}}
    else: 
        memo = MemoEntry(obj)
        memo.insert()
        return {"status": "okay"}