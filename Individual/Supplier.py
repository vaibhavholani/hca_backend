"""
=== Class Description ===
The file is supposed to represent a Supplier

"""
from __future__ import annotations
from API_Database import retrieve_indivijual
from .Individual import Individual

class Supplier(Individual):
    """
    The class represents a supplier.

    name : The name  of the Supplier
    short_name: The short name of the Supplier
    address: The address of the supplier.

    """
    table_name = 'supplier'

    def __init__(self, name: str, address: str, *args, **kwargs) -> None:
        """Initializes a Supplier instance by invoking the parent initializer with a preset table name."""
        super().__init__(name, address, table_name=self.table_name, **kwargs)

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
        return 'Supplier Name: ' + retrieve_indivijual.get_supplier_name_by_id(supplier_id)