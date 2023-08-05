"""
==== Description ====
This class is used to represent a register entry. A register entry is made when
the bill for an order is received.

"""

from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Union
from API_Database import insert_register_entry, update_register_entry, utils
from API_Database import get_register_entry_id, get_register_entry
from Exceptions import DataError
from Entities import Entry


class RegisterEntry(Entry):
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

    _report_attribute_map = {
            "bill_number": "bill_no",
            "register_date": "bill_date",
            "amount": "bill_amt",
            "status": "bill_status"
            }

    def __init__(self,
                 bill_number: int,
                 amount: int,
                 supplier_id: int,
                 party_id: int,
                 register_date: Union[str, datetime],
                 status: str = "N",
                 gr_amount: int = 0,
                 deduction: int = 0,
                 partial_amount: int = 0,
                 table_name="register_entry",
                 *args,
                 **kwargs
                 ) -> None:

        super().__init__(table_name=table_name, *args, **kwargs)
        self.bill_number = bill_number
        self.amount = amount
        self.supplier_id = supplier_id
        self.party_id = party_id
        self.register_date = utils.parse_date(register_date)
        self.gr_amount = gr_amount
        self.deduction = deduction
        self.status = status
        self.partial_amount = partial_amount

    def get_pending_amount(self) -> int:
        return int(self.amount - self.gr_amount - self.deduction - self.partial_amount)

    def update(self) -> Dict:
        return update_register_entry.update_register_entry_data(self)
    
    def get_id(self) -> int:
        return get_register_entry_id(self.supplier_id,
                                    self.party_id, 
                                    self.bill_number,)

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
        data = cls.convert_int_attributes(data, int_attributes)

        return cls(**data)
    
    @classmethod
    def retrieve(cls, supplier_id: int, 
                 party_id: int, 
                 bill_number: Union[List[int], int]) -> Union[RegisterEntry, List[RegisterEntry]]:
        
        # if multiple bills
        if isinstance(bill_number, list):
            bills_data = []
            for bill in bill_number:
                bills_data.append(get_register_entry(supplier_id, party_id, bill))
            return [cls.from_dict(d) for d in bills_data]
        
        # if just one bill
        bill_data = get_register_entry(supplier_id, party_id, bill_number)
        return cls.from_dict(bill_data)

    @classmethod
    def insert(cls, data: Dict, get_cls: bool=False) -> Dict:
        register_entry = cls.from_dict(data)
        if insert_register_entry.check_new_register(register_entry):
            ret = insert_register_entry.insert_register_entry(register_entry)
            if get_cls and ret["status"] == "okay":
                ret["class"] = register_entry
            return ret
        else:
            raise DataError({"status": "error",
                             "message": "Duplicate Bill Number",
                             "input_errors": {"bill_number": {"status": "error", "message": "Bill number already exists"}}})
