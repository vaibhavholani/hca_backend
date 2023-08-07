"""
==== Description ====
This class is used to represent a memo entry.

"""

from __future__ import annotations
from typing import List, Dict, Union
from datetime import datetime
from .RegisterEntry import RegisterEntry
from .Entry import Entry
from .MemoBill import MemoBill
from API_Database import insert_memo_entry
from API_Database import retrieve_memo_entry, get_memo_entry_id
from API_Database import update_part_payment
from API_Database import parse_date, sql_date, delete_memo_payments
from Exceptions import DataError


class MemoEntry(Entry):

    """
    A class that represents a memo entry

    ===Attributes===

    amount: the amount for which the party has received an order
    date: the date

    """
    memo_number: int
    supplier_id: int
    party_id: int
    amount: int
    gr_amount: int
    deduction: int
    mode: str
    register_date: datetime
    selected_bills: List[RegisterEntry]
    payment: List[Dict[Union[int, str]]]
    part_payment: List[int]

    _report_attribute_mapping = {
    "memo_number": "memo_no",
    "register_date": "memo_date",
    "amount": "chk_amt",
    "type": "memo_type"
}

    def __init__(self,
                 memo_number: int,
                 supplier_id: int,
                 party_id: int,
                 amount: int,
                 mode: str,
                 register_date: Union[str, datetime],
                 selected_bills: List[int] = [],
                 payment: List[Dict[Union[int, str]]] = [],
                 selected_part: List[Dict[int]] = [],
                 gr_amount: int = 0,
                 deduction: int = 0,
                 table_name: str = "memo_entry",
                 *args,
                 **kwargs
                 ) -> None:

        super().__init__(table_name=table_name,*args, **kwargs)

        self.memo_number = memo_number
        self.supplier_id = supplier_id
        self.party_id = party_id
        self.amount = amount
        self.register_date = sql_date(parse_date(register_date))
        self.gr_amount = gr_amount
        self.deduction = deduction

        self.mode = mode
        self.selected_bills = \
            RegisterEntry.retrieve(
                self.supplier_id,
                self.party_id,
                selected_bills)
        
        self.payment = [
            {"bank_id": int(info["id"]),
             "cheque_number": int(info["cheque"])}
            for info in (payment)]

        self.part_payment = [int(memo_id) for memo_id in selected_part]

        # Memo Bills
        self.memo_bills: List[MemoBill] = []

    def full_payment(self) -> None:
        """
        Used to complete full payment for bill(s)
        """
        # auto assign gr_amount and deduction
        self._auto_assign("gr_amount")
        self._auto_assign("deduction")

        # set bills status to F
        for bill in self.selected_bills:
            bill.status = "F"
            pending_amount = bill.get_pending_amount()
            # Add Memo Bills
            self.memo_bills.append(
                MemoBill(bill.bill_number,
                         pending_amount,
                         "F")
            )

            # update register entry data
            bill.update()

    def database_partial_payment(self):
        """
        Store partial payments into the database
        """

        # Add Memo bill
        self.memo_bills.append(
            MemoBill(-1,
                     self.amount,
                     "PR")
        )

    def generate_memo_bills_and_update_status(self):
        """
        Insert the memo entry into the database
        """
        if self.mode == "Full":
            self.full_payment()

        elif self.mode == "Part":
            self.database_partial_payment()

    def _auto_assign(self, attr_name: str) -> None:
        """
        Automatically assign the amount to the selected bill
        """
        assign_amount = getattr(self, attr_name)
        for bill in self.selected_bills:
            pending_amount = bill.get_pending_amount()

            if assign_amount != 0:
                if pending_amount >= assign_amount:
                    # Assign the whole amount
                    used_amount = assign_amount
                    assign_amount = 0
                else:
                    # Assign the pending amount
                    used_amount = pending_amount
                    assign_amount -= pending_amount

                # update register entry data
                if used_amount != 0:
                    bill_previous_amount = getattr(bill, attr_name)
                    bill_new_amount = bill_previous_amount + used_amount
                    setattr(bill, attr_name, bill_new_amount)

                    # create memo bill
                    memo_bill = MemoBill(bill.bill_number,
                                used_amount,
                                attr_name[0].upper())
                    # create a memo bill
                    self.memo_bills.append(memo_bill)

    def get_id(self) -> int:
        return get_memo_entry_id(self.supplier_id,
                                    self.party_id, 
                                    self.memo_number)
    
    def delete(self) -> Dict:
        """
        Delete the memo entry from the database
        """
        memo_id = self.get_id()

        # Delete the memo bills
        for memo_bill in self.memo_bills:
            ret = memo_bill.delete(memo_id, self.supplier_id, self.party_id)

        # Delete the memo payments
        ret = delete_memo_payments(memo_id)

        # Delete the memo payments
        # check if the a part payment was used in the memo and then remove that
        for part_memo_id in self.part_payment:
            ret = update_part_payment(self.supplier_id,
                                        self.party_id,
                                        memo_id=part_memo_id,
                                        used=False)

        # Delete the memo entry
        ret = super().delete()
        return ret
    
    @staticmethod
    def check_new(memo_number: int,
                  register_date: Union[str, datetime], 
                  *args, 
                  **kwargs) -> bool:

        memo_number = int(memo_number)
        register_date = parse_date(register_date)
        return retrieve_memo_entry.check_new_memo(memo_number,
                                                  register_date)

    @classmethod
    def from_dict(cls, data: Dict) -> MemoEntry:
        # List of attribute names to be converted to integers
        int_attributes = ["memo_number",
                            "supplier_id",
                            "party_id",
                            "amount",
                            "selected_bills",
                            "gr_amount",
                            "deduction"]
        
        # parse selected bills to only have "id"
        if "selected_bills" in data:
            data["selected_bills"] = [int(bill["bill_number"]) for bill 
                                      in data["selected_bills"]]

        data = cls.convert_int_attributes(data, int_attributes)

        return cls(**data)

    @classmethod
    def insert(cls, data: Dict, get_cls: bool=False) -> Dict:
        """
        Adds a memo to the database
        """
        #  Check for valid memo number
        if not cls.check_new(**data):
            return {
                "status": "error",
                "message": "Duplicate memo number",
                "input_errors": {"memo_number": {"error": True, "message": "Duplicate memo number"}}
            }

        memo = cls.from_dict(data)
        # Generate Memo Bills and Update the status of the bills
        memo.generate_memo_bills_and_update_status()

        # Insert Memo into the database
        ret = insert_memo_entry.insert_memo_entry(memo)
        if get_cls:
            if get_cls and ret["status"] == "okay":
                ret["class"] = memo

        return ret
