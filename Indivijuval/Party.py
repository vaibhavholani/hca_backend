"""
=== Class Description ===
The file is supposed to represent a Party

"""
from __future__ import annotations
from API_Database import insert_individual
from API_Database import retrieve_indivijual
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
    
    @staticmethod
    def get_party_name_by_id(party_id: int) -> str:
        """
        Get party name by ID
        """
        return retrieve_indivijual.get_party_name_by_id(party_id)
    
    @staticmethod
    def get_report_name(party_id: int) -> str:
        """
        Get party name by ID for report
        """
        return "Party Name: " + retrieve_indivijual.get_party_name_by_id(party_id)


def create_party(obj: Dict) -> None:

    party =  Party(**obj)
    insert_individual.insert_party(party)
