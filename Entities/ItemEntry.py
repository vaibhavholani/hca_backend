from __future__ import annotations
from typing import List, Dict, Union
from API_Database import insert_item_entry, update_item_entry, retrieve_item_entry
from API_Database import get_item_entry_id
from Entities import Entry


class ItemEntry(Entry):
    """
    A class that represents an item entry in the inventory system.

    ===Attributes===

    id: ID of the item entry (if retrieved or after insertion)
    register_entry_id: the ID of the register entry.
    item_id: the ID of the item.
    quantity: quantity of the item.
    rate: rate of the item.
    """

    def __init__(self,
                 register_entry_id: int,
                 item_id: int,
                 quantity: int,
                 rate: int,
                 table_name="item_entry",
                 *args,
                 **kwargs) -> None:
        super().__init__(table_name=table_name, *args, **kwargs)
        self.register_entry_id = register_entry_id
        self.item_id = item_id
        self.quantity = quantity
        self.rate = rate

    def update(self, update_data: Dict) -> Dict:
        """
        Updates the item entry based on the provided update_data dictionary.
        """
        for key, value in update_data.items():
            setattr(self, key, value)
        return update_item_entry(self)

    def get_id(self) -> int:
        """
        Returns the ID of the item entry.
        """
        super_id = super().get_id()
        if super_id is not None: return super_id
        
        return get_item_entry_id(self.register_entry_id,
                            self.item_id)


    @classmethod
    def from_dict(cls, data: Dict, *args, **kwargs) -> ItemEntry:
        """
        Creates an instance of ItemEntry from a dictionary of attributes.
        """
        return cls(**data)

    @classmethod
    def retrieve(cls, register_entry_id: int = None, item_id: int = None) -> Union[ItemEntry, List[ItemEntry]]:
        """
        Retrieves an item entry or a list of item entries based on given criteria.
        """
        data = retrieve_item_entry(register_entry_id, item_id)

        if isinstance(data, list):
            return [cls.from_dict(entry) for entry in data]
        return cls.from_dict(data)

    @classmethod
    def insert(cls, data: Dict, get_cls: bool = False) -> Dict:
        """
        Inserts a new item entry into the database.
        """
        new_entry = cls.from_dict(data)
        ret = insert_item_entry(new_entry)

        if get_cls and ret["status"] == "okay":
            ret["class"] = new_entry

        return ret
