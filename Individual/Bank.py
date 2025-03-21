"""
=== Class Description ===
The file is supposed to represent a Bank

"""
from __future__ import annotations
from API_Database import insert_individual
from typing import Dict
from .Individual import Individual

class Bank(Individual):
    """
    The class represents a Bank.

    name : The name  of the Bank
    address: The address of the Bank.

    """
    table_name = 'bank'

    def __init__(self, name: str, address: str, *args, **kwargs):
        """Initializes a Bank instance with a name and address."""
        super().__init__(name, address, table_name=self.table_name, **kwargs)