"""
=== Class Description ===
The file is supposed to represent a Party

"""
from __future__ import annotations
from API_Database import insert_individual
from typing import Dict

class Party:
    """
    The class represents a Party.

    name : The name  of the Party
    short_name: The short name of the Party
    address: The address of the Party.

    """

    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address


def create_party(obj: Dict) -> None:

    party =  Party(**obj)
    insert_individual.insert_party(party)
