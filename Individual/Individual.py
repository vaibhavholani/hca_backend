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
        self.name = name
        self.address = address

        # check if kwargs has phone_number
        phone_number = kwargs.get("phone_number", None)
        self.phone_number = self._parse_number(phone_number)
        self.table_name = table_name

        # check if kwargs has id
        self.id = kwargs.get('id', None)
        if self.id is not None:
            self.id = int(self.id) 

    def get_id(self) -> int:
        if self.id is not None:
            return self.id
        return get_individual_id_by_name(self.name, self.table_name)
    
    def update(self) -> Dict:
        return update_individual(self)

    def delete(self) -> Dict:
        return delete_by_id(self.get_id(), self.table_name)

    def _parse_number(self, number: str) -> str:
        """
        Checks if the number is a valid number. Defaults to "IN" (Indian) country code.
        """
        # Adding a Failsafe
        if number is None:
            return None
        if type(number) != str: 
            print(f"WARNING: Provided phone number ({number}) is not a string.")
            number = str(number)

        parsed_number = phonenumbers.parse(number, "IN")
        if not phonenumbers.is_valid_number(parsed_number):
            raise DataError({
                "status": "error",
                "message": "Invalid Phone Number",
                "input_errors": {"phone_number": {"error": True, "message": "Invalid Phone Number"}}
            })
        formatted_phone_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return formatted_phone_number


    @classmethod
    def from_dict(cls, obj: Dict, *args, **kwargs) -> Individual:
        return cls(**obj)

    @classmethod
    def retrieve(cls, id: int) -> Individual:
        return cls.from_dict(get_individual_by_id(id, cls.table_name))

    @classmethod
    def insert(cls, obj: Dict,
               get_cls: bool = False) -> Dict:

        entity = cls.from_dict(obj)
        ret = insert_individual(entity, entity.table_name)

        # Add the class object to the return dictionary
        if get_cls and ret["status"] == "okay":
            ret["class"] = entity

        return ret
