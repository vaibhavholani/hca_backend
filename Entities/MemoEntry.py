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
from API_Database import retrieve_memo_entry, get_memo_entry, get_memo_entry_id, get_memo_bills_by_id
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
                 **kwargs) -> None:

        super().__init__(table_name=table_name, *args, **kwargs)

        self.memo_number = memo_number
        self.supplier_id = supplier_id
        self.party_id = party_id
        self.amount = amount
        self.register_date = sql_date(parse_date(register_date))
        self.gr_amount = gr_amount
        self.deduction = deduction
        self.mode = mode

        # selected_bills is now a list of register_entry IDs
        self.selected_bills = RegisterEntry.retrieve_by_id_list(selected_bills)
        self.payment = payment
        self.part_payment = [int(memo_id) for memo_id in selected_part]
        self.memo_bills: List[MemoBill] = []

    def full_payment(self) -> None:
        self._auto_assign("gr_amount")
        self._auto_assign("deduction")

        for bill in self.selected_bills:
            bill.status = "F"
            pending_amount = bill.get_pending_amount()
            self.memo_bills.append(
                MemoBill(bill.get_id(),  # Use the register_entry ID
                         pending_amount,
                         "F")
            )
            bill.update()

    def database_partial_payment(self):
        """
        Store partial payments into the database
        """

        # Add Memo bill
        self.memo_bills.append(
            MemoBill(None,
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
                    memo_bill = MemoBill(bill.get_id(),
                                         used_amount,
                                         attr_name[0].upper())
                    # create a memo bill
                    self.memo_bills.append(memo_bill)

    def get_id(self) -> int:
        super_id = super().get_id()
        if super_id is not None: return super_id
        
        return MemoEntry.get_memo_entry_id(self.supplier_id,
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

    @staticmethod
    def get_memo_entry_id(supplier_id: int, party_id: int, memo_number: int) -> int:
        """
        Get the memo entry id
        """
        return get_memo_entry_id(supplier_id, party_id, memo_number)

    @staticmethod
    def get_memo_entry(memo_id: int) -> Dict:
        """
        Get the memo entry
        """
        return get_memo_entry(memo_id)

    @staticmethod
    def get_json(supplier_id: int, party_id: int, memo_number: int) -> Dict:
        """
        Get the json data for the memo entry
        """
        memo_id = MemoEntry.get_memo_entry_id(supplier_id, party_id, memo_number)
        data = MemoEntry.get_memo_entry(memo_id)
        return data

    @staticmethod
    def get_memo_bills_by_id(memo_id: int) -> List[Dict]:
        """
        Get the memo bills for a memo entry
        """
        return get_memo_bills_by_id(memo_id)

    @classmethod
    def retrieve(cls, supplier_id: int, party_id: int, memo_number: int) -> MemoEntry:
        """
        Retrieve a memo entry from the database
        """
        data = cls.get_json(supplier_id, party_id, memo_number)
        memo_entry = cls.from_dict(data, parse_memo_bills=True)

        return memo_entry

    @classmethod
    def from_dict(cls, data: Dict, parse_memo_bills: bool = False) -> MemoEntry:
        # List of attribute names to be converted to integers
        int_attributes = ["memo_number",
                          "supplier_id",
                          "party_id",
                          "amount",
                          "selected_bills",
                          "gr_amount",
                          "deduction"]

        if "selected_bills" in data:
            data["selected_bills"] = [int(bill["id"]) for bill in data["selected_bills"]]

        if "payment" in data:
            for payment_index in range(len(data["payment"])):
                info = data["payment"][payment_index]
                if "id" in info:
                    info["bank_id"] = int(info["id"])
                    del info["id"]
                if "cheque" in info:
                    info["cheque_number"] = int(info["cheque"])
                    del info["cheque"]
                data["payment"][payment_index] = info

        data = cls.convert_int_attributes(data, int_attributes)
        memo_entry = cls(**data)

        if parse_memo_bills:
            if "memo_bills" not in data:
                raise DataError("Memo Bills not found in Data. MemoEntry from Dict Failed")

            memo_bills = data["memo_bills"]
            memo_entry.memo_bills = [MemoBill.from_dict(
                memo_bill) for memo_bill in memo_bills]

        return memo_entry

    @classmethod
    def insert(cls, data: Dict, get_cls: bool = False) -> Dict:
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
