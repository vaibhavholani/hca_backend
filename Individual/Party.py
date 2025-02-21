"""
=== Class Description ===
The file is supposed to represent a Party

"""
from __future__ import annotations
from .Individual import Individual
from API_Database import retrieve_indivijual

class Party(Individual):
    """
    The class represents a Party.

    name : The name  of the Party
    address: The address of the Party.
    """
    table_name = 'party'

    def __init__(self, name: str, address: str, *args, **kwargs):
        """Initializes a Party instance by invoking the parent initializer with a preset table name."""
        super().__init__(name, address, table_name=self.table_name, **kwargs)

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
        return 'Party Name: ' + retrieve_indivijual.get_party_name_by_id(party_id)