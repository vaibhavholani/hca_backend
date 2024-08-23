from __future__ import annotations
from .util import insert_party, insert_supplier, delete_party, delete_supplier
from typing import Dict, List, Callable, Union

class Skeleton:
    def __init__(self, 
                 data: Dict, 
                 insert: Union[List[Callable], Callable], 
                 update: Callable,
                 retrieve: Callable,
                 delete: Callable) -> None:
        
        self.data = data
        self.insert = insert
        self.update = update
        self.retrieve = retrieve
        self.delete_func = delete
        
    def insert_and_retrieve(self):

        # If there is a supplier id or party id in data, insert the supplier or party first
        if "supplier_id" in self.data:
            insert_supplier(self.data["supplier_id"])
        if "party_id" in self.data:
            insert_party(self.data["party_id"])

        # Check if insert is a list of callables
        if isinstance(self.insert, list):
            result = self.data
            for func in self.insert:
                result = func(result)
        else:
            result = self.insert(self.data)

        # Retrieve the entry from the database
        return self.retrieve(result)
        # After return, there should be asserts making sure data is entered correctly

    def update_and_retrieve(self, updates: Dict):
        # write a function here for adding the updates

        # return the retrieved entry from the database (don't know how this will work)
        return self.retrieve()

    def delete(self):
        self.delete_func(self.data)
        # after this we wanna check if the entry is deleted from the database
    
