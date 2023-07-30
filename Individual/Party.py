"""
=== Class Description ===
The file is supposed to represent a Bank

"""
from __future__ import annotations
from .Individual import Individual
from API_Database import retrieve_indivijual

class Party(Individual):
    """
    The class represents a Bank.

    name : The name  of the Bank
    address: The address of the Bank.
    """
    def __init__(self, name: str, address: str, *args, **kwargs):
        super().__init__(name, address)
    
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