from typing import Dict, List
from API_Database import retrieve_register_entry, retrieve_memo_entry
from Reports import table

class OrderForm(table.HeaderTable):

    def __init__(self) -> None:
        """Initializes the Order Form report with a preset title."""
        super().__init__('Order Form')

    def generate_total_rows(self, data_rows: List[Dict], before_data: bool=False):
        """Generates total rows for the Order Form report and returns a list of calculated totals."""
        return []