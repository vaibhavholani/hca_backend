"""
=== Class Description ===
The file is supposed to represent a Transporter

"""
from __future__ import annotations
from API_Database import insert_individual
from typing import Dict 

class Transporter:
    """
    The class represents a Transporter.

    name : The name  of the Transporter
    address: The address of the Transporter.

    """

    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address


def create_transporter(obj: Dict) -> None:
    transporter = Transporter(**obj)
    insert_individual.insert_transporter(transporter)
