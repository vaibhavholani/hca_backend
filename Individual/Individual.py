"""
=== Class Description ===
The file is supposed to represent a Individual

"""
from __future__ import annotations
from API_Database import insert_individual
from API_Database import retrieve_indivijual
from typing import Dict

class Individual:
    """
    The class represents a Individual.

    name : The name of the Individual
    short_name: The short name of the Individual
    address: The address of the Individual.
    """

    def __init__(self, name: str, address: str, *args, **kwargs):
        self.name = name
        self.address = address
    
    @classmethod
    def create_individual(cls, obj: Dict) -> Individual:
        return cls(**obj)
