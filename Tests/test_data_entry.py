from __future__ import annotations
from .util import insert_party, insert_supplier, delete_party, delete_supplier
from typing import Dict, List, Callable, Union

class Skeleton:

    def __init__(self, data: Dict, insert: Union[List[Callable], Callable], update: Callable, retrieve: Callable, delete: Callable) -> None:
        """Initializes the test data entry with provided data and CRUD operation functions."""
        self.data = data
        self.insert = insert
        self.update = update
        self.retrieve = retrieve
        self.delete_func = delete

    def insert_and_retrieve(self):
        """Inserts test data into the database and retrieves the inserted entry for validation."""
        if 'supplier_id' in self.data:
            insert_supplier(self.data['supplier_id'])
        if 'party_id' in self.data:
            insert_party(self.data['party_id'])
        if isinstance(self.insert, list):
            result = self.data
            for func in self.insert:
                result = func(result)
        else:
            result = self.insert(self.data)
        return self.retrieve(result)

    def update_and_retrieve(self, updates: Dict):
        """Updates test data using provided changes and retrieves the updated entry for verification."""
        return self.retrieve()

    def delete(self):
        """Deletes the test data entry from the database."""
        self.delete_func(self.data)