from __future__ import annotations
from typing import List, Dict, Optional
from API_Database import get_memo_bill_id, get_partial_payment_by_memo_id
from API_Database import delete_by_id
from Exceptions import DataError
from .RegisterEntry import RegisterEntry
from .Entry import Entry

class MemoBill(Entry):

    def __init__(self, bill_id: Optional[int],
                 amount: int,
                 memo_type: str,
                 table_name: str = "memo_bills", 
                 *args,
                 **kwargs) -> None:

        super().__init__(table_name=table_name, *args, **kwargs)
        self.bill_id = bill_id  # bill_id can be None
        self.amount = amount
        self.type = memo_type

    def get_id(self, memo_id: int) -> int:
        super_id = super().get_id()
        if super_id is not None:
            return super_id

        return MemoBill.get_memo_bill_id(memo_id=memo_id,
                                         bill_id=self.bill_id,
                                         type=self.type,
                                         amount=self.amount)

    def undo(self, memo_id: int, supplier_id: int, party_id: int) -> Dict:
        if self.type == "PR":
            # Handle partial payment
            part_payment = get_partial_payment_by_memo_id(memo_id)
            if part_payment["used"]:
                raise DataError(
                    f"Part Payment {part_payment['memo_number']} is used")
            else:
                ret = delete_by_id(part_payment["id"], "part_payments")
        else:
            if self.bill_id is None:
                raise DataError("bill_id is None for non-PR memo bill")
            register_entry = RegisterEntry.retrieve_by_id(self.bill_id)

            if self.type == "F":
                register_entry.status = "N"
            elif self.type == "D":
                register_entry.deduction -= self.amount
            elif self.type == "G":
                register_entry.gr_amount -= self.amount
            ret = register_entry.update()
        return ret

    def delete(self, memo_id: int, supplier_id: int, party_id: int) -> Dict:
        memo_bill_id = self.get_id(memo_id)
        ret = self.undo(memo_id, supplier_id, party_id)
        ret = delete_by_id(memo_bill_id, self.table_name)
        return ret

    @staticmethod
    def get_memo_bill_id(memo_id: int, bill_id: Optional[int], type: str, amount: int) -> int:
        return get_memo_bill_id(memo_id=memo_id,
                                bill_id=bill_id,
                                type=type,
                                amount=amount)

    @classmethod
    def from_dict(cls, data: Dict, *args, **kwargs) -> MemoBill:
        int_attributes = ["amount"]

        if "bill_id" in data and data["bill_id"] is not None:
            data["bill_id"] = int(data["bill_id"])
        else:
            data["bill_id"] = None

        if "type" not in data:
            raise DataError("Memo Bill type not found")
        elif data["type"] not in ["F", "D", "G", "PR"]:
            raise DataError(
                f"Memo Bill type {data['type']} not supported")
        else:
            data["memo_type"] = data["type"]

        data = cls.convert_int_attributes(data, int_attributes)
        return cls(**data)

    def __str__(self) -> str:
        return f"Memo Bill: Bill ID: {self.bill_id}, Amount: {self.amount}, Type: {self.type}"
