"""
=== Class Description ===
The file is supposed to represent a Bank

"""
from __future__ import annotations
from typing import Dict
from .Individual import Individual

class Transporter(Individual):
    """
    The class represents a Bank.

    name : The name  of the Bank
    address: The address of the Bank.

    """

    def __init__(self, name: str, address: str, *args, **kwargs):
        super().__init__(name, address)