"""
=== Class Description ===
The file is supposed to represent a Supplier

"""
from __future__ import annotations
from API_Database import insert_individual
from API_Database import retrieve_indivijual
from typing import Dict
class Supplier:
    """
    The class represents a supplier.

    name : The name  of the Supplier
    short_name: The short name of the Supplier
    address: The address of the supplier.

    """

    def __init__(self, name: str, address: str) -> None:

        self.name = name
        self.address = address
    
    @staticmethod
    def get_supplier_name_by_id(supplier_id: int) -> str:
        """
        Get supplier name by ID
        """
        return retrieve_indivijual.get_supplier_name_by_id(supplier_id)
    
    @staticmethod
    def get_report_name(supplier_id: int) -> str:
        """
        Get supplier name by ID for report
        """
        return "Supplier Name: " + retrieve_indivijual.get_supplier_name_by_id(supplier_id)


def create_supplier(obj:Dict) -> None:
    """
    Create and return a Supplier

    :param name: The name  of the Supplier
    :param short_name: The short name of the Supplier
    :param address: The address of the supplier.
    :return: Supplier
    """
    return Supplier(**obj)


