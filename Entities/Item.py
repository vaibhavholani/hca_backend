from __future__ import annotations
from typing import List, Dict, Union
from API_Database import insert_item, update_item, retrieve_item
from API_Database import get_item_id
from Exceptions import DataError
from Entities import Entry

class Item(Entry):
    """
    A class that represents an item in the inventory.

    ===Attributes===

    id: ID of the item (if retrieved or after insertion)
    supplier_id: the ID of the supplier.
    name: the name of the item.
    color: the color of the item.
    """

    def __init__(self, supplier_id: int, name: str, color: str='N/A', table_name='item', *args, **kwargs) -> None:
        """Initializes an Item with supplier ID, name, and color (defaults to 'N/A')."""
        super().__init__(*args, table_name=table_name, **kwargs)
        self.supplier_id = supplier_id
        self.name = name
        self.color = color

    def update(self, update_data: Dict) -> Dict:
        """
        Updates the item based on the provided update_data dictionary.
        """
        for (key, value) in update_data.items():
            setattr(self, key, value)
        return update_item(self)

    def get_id(self) -> int:
        """
        Returns the ID of the item.
        """
        super_id = super().get_id()
        if super_id is not None:
            return super_id
        return get_item_id(self.supplier_id, self.name, self.color)

    @classmethod
    def from_dict(cls, data: Dict, *args, **kwargs) -> Item:
        """
        Creates an instance of Item from a dictionary of attributes.
        """
        return cls(**data)

    @classmethod
    def retrieve(cls, supplier_id: int, name: str, color: str) -> Union[Item, List[Item]]:
        """
        Retrieves an item or a list of items based on given criteria.
        """
        data = retrieve_item(supplier_id, name, color)
        return cls.from_dict(data)

    @classmethod
    def get_cls(cls, supplier_id: int, name: str, color: str) -> Item:
        """
        Retrieves an instance of the Item class based on the provided criteria.
        """
        data = cls.retrieve(supplier_id=supplier_id, name=name, color=color)
        if not data:
            raise DataError({'status': 'error', 'message': 'Item not found', 'input_errors': {'name': {'status': 'error', 'message': 'Invalid criteria'}}})
        return data[0]

    @classmethod
    def insert(cls, data: Dict, get_cls: bool=False) -> Dict:
        """
        Inserts a new item into the database.
        """
        new_item = cls.from_dict(data)
        ret = insert_item(new_item)
        if get_cls and ret['status'] == 'okay':
            ret['class'] = new_item
        return ret