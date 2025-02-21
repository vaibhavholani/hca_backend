from typing import Dict, List
from API_Database import delete_by_id

class Entry:

    def __init__(self, table_name: str, *args, **kwargs) -> None:
        """Initializes an Entry with a table name and an optional ID."""
        self.table_name = table_name
        self.id = kwargs.get('id', None)
        if self.id is not None:
            self.id = int(self.id)

    def get_id(self) -> int:
        """Returns the ID of the Entry."""
        return self.id

    def delete(self) -> Dict:
        """Deletes the Entry from the database by calling delete_by_id with the entry's ID and table name."""
        return delete_by_id(self.get_id(), self.table_name)

    @staticmethod
    def convert_int_attributes(obj: Dict, int_attributes: List):
        """
        Convert the necessary integer attributes from strings to integers
        """
        for attr in int_attributes:
            if attr in obj:
                if type(obj[attr]) == str:
                    obj[attr] = int(obj[attr].strip())
                elif type(obj[attr]) == List:
                    obj[attr] = [int(x) for x in obj[attr]]
        return obj