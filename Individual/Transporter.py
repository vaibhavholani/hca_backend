"""
=== Class Description ===
The file is supposed to represent a Transporter

"""
from __future__ import annotations
from typing import Dict
from .Individual import Individual

class Transporter(Individual):
    """
    The class represents a Transporter.

    name : The name  of the Transporter
    address: The address of the Transporter.

    """
    table_name = 'transport'

    def __init__(self, name: str, address: str, *args, **kwargs):
        """Initializes a Transporter instance by invoking the parent initializer with a preset table name."""
        super().__init__(name, address, table_name=self.table_name, **kwargs)