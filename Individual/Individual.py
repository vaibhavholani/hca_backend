"""
=== Class Description ===
The file is supposed to represent a Individual
"""
from __future__ import annotations
from typing import Dict
import phonenumbers
from API_Database import get_individual_id_by_name, insert_individual
from API_Database import get_individual_by_id, update_individual
from API_Database import delete_by_id
from Exceptions import DataError

class Individual:
    """
    The class represents a Individual.

    name : The name of the Individual
    short_name: The short name of the Individual
    address: The address of the Individual.
    """

    def __init__(self, name: str, address: str, table_name: str, *args, **kwargs):
        """Initializes an Individual with a name, address, table name, and optionally a phone number and ID."""
        self.name = name
        self.address = address
        phone_number = kwargs.get('phone_number', None)
        self.phone_number = self._parse_number(phone_number)
        self.table_name = table_name
        self.id = kwargs.get('id', None)
        if self.id is not None:
            self.id = int(self.id)

    def get_id(self) -> int:
        """Returns the individual's ID, or retrieves it based on name if not already set."""
        if self.id is not None:
            return self.id
        return get_individual_id_by_name(self.name, self.table_name)

    def update(self) -> Dict:
        """Updates the individual's record in the database and returns the update status."""
        return update_individual(self)

    def delete(self) -> Dict:
        """Deletes the individual's record from the database and returns the deletion status."""
        return delete_by_id(self.get_id(), self.table_name)

    def _parse_number(self, number: str) -> str:
        """
        Checks if the number is a valid number. Defaults to "IN" (Indian) country code.
        """
        if number is None:
            return None
        if type(number) != str:
            print(f'WARNING: Provided phone number ({number}) is not a string.')
            number = str(number)
        parsed_number = phonenumbers.parse(number, 'IN')
        if not phonenumbers.is_valid_number(parsed_number):
            raise DataError({'status': 'error', 'message': 'Invalid Phone Number', 'input_errors': {'phone_number': {'error': True, 'message': 'Invalid Phone Number'}}})
        formatted_phone_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return formatted_phone_number

    @classmethod
    def from_dict(cls, obj: Dict, *args, **kwargs) -> Individual:
        """Creates an Individual instance from a dictionary of attributes."""
        return cls(**obj)

    @classmethod
    def retrieve(cls, id: int) -> Individual:
        """Retrieves an Individual by ID from the database and returns an instance."""
        return cls.from_dict(get_individual_by_id(id, cls.table_name))

    @classmethod
    def insert(cls, obj: Dict, get_cls: bool=False) -> Dict:
        """Inserts a new Individual into the database and returns the insertion status, optionally including the instance."""
        entity = cls.from_dict(obj)
        ret = insert_individual(entity, entity.table_name)
        if get_cls and ret['status'] == 'okay':
            ret['class'] = entity
        return ret