from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Union
from API_Database import utils, get_order_form
from API_Database import insert_order_form, update_order_form_data
from API_Database import get_order_form_id, check_new_order_form
from Exceptions import DataError
from Entities import Entry

class OrderForm(Entry):
    """
    A class that represents an order form.

    ===Attributes===

    order_form_number: a unique number that identifies an order form
    register_date: the date when the order form is registered
    supplier: the full name of the supplier
    party: the full name of the party
    status: the status of the order form
    """
    supplier_id: int
    party_id: int
    order_form_number: int
    register_date: datetime
    status: str

    def __init__(self, supplier_id: int, party_id: int, order_form_number: int, register_date: Union[str, datetime], status: str='', delivered: bool=False, table_name='order_form', *args, **kwargs) -> None:
        """Initializes an OrderForm with supplier ID, party ID, order form number, register date, status, and delivery flag."""
        super().__init__(*args, table_name=table_name, **kwargs)
        self.supplier_id = supplier_id
        self.party_id = party_id
        self.order_form_number = order_form_number
        self.register_date = utils.sql_date(utils.parse_date(register_date))
        self.status = status
        self.delivered = delivered

    def get_id(self) -> int:
        """Returns the ID of the OrderForm; computes it if not already set."""
        super_id = super().get_id()
        if super_id is not None:
            return super_id
        return get_order_form_id(self.supplier_id, self.party_id, self.order_form_number)

    def update(self) -> Dict:
        """Updates the OrderForm in the database and returns the update status."""
        return update_order_form_data(self)

    @classmethod
    def from_dict(cls, data: Dict, *args, **kwargs) -> OrderForm:
        """Creates an OrderForm instance from a dictionary of attributes, converting necessary fields to integers."""
        int_attributes = ['order_form_number', 'supplier_id', 'party_id']
        data = cls.convert_int_attributes(data, int_attributes)
        return cls(**data)

    @classmethod
    def retrieve(cls, supplier_id: int, party_id: int, order_form_number: int) -> OrderForm:
        """Retrieves an OrderForm from the database based on supplier ID, party ID, and order form number."""
        order_form_data = get_order_form(supplier_id, party_id, order_form_number)
        return cls.from_dict(order_form_data)

    @classmethod
    def insert(cls, data: Dict, get_cls: bool=False) -> Dict:
        """Inserts a new OrderForm into the database after validating uniqueness; returns the insertion status."""
        order_form = cls.from_dict(data)
        if check_new_order_form(order_form):
            ret = insert_order_form(order_form)
            if get_cls and ret['status'] == 'okay':
                ret['class'] = order_form
            return ret
        else:
            raise DataError({'status': 'error', 'message': 'Duplicate Order Form Number', 'input_errors': {'order_form_number': {'status': 'error', 'message': 'Order form number already exists'}}})