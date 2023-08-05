"""
=== Class Description ===
The file is supposed to represent a Individual

"""
from __future__ import annotations
from API_Database import get_individual_id_by_name, insert_individual
from API_Database import get_individual_by_id
from API_Database import delete_by_id
from typing import Dict

class Individual:
    """
    The class represents a Individual.

    name : The name of the Individual
    short_name: The short name of the Individual
    address: The address of the Individual.
    """
    def __init__(self, name: str, address: str, table_name: str, *args, **kwargs):
        self.name = name
        self.address = address
        self.table_name = table_name
    
    def get_id(self) -> int:
        return get_individual_id_by_name(self.name, self.table_name)
    
    def delete(self):
        return delete_by_id(self.get_id(), self.table_name)
    
    @classmethod
    def create_individual(cls, obj: Dict) -> Individual:
        return cls(**obj)
    
    @classmethod
    def retrieve(cls, id: int) -> Individual:
        return cls.create_individual(**get_individual_by_id(id, cls.table_name))
    
    @classmethod
    def insert(cls, obj: Dict, 
               get_cls: bool = False) -> Dict:
        entity = cls.create_individual(obj)
        ret = insert_individual(entity, entity.table_name)
        
        # Add the class object to the return dictionary
        if get_cls and ret["status"] == "okay":
            ret["class"] = entity

        return ret



