from typing import Dict, List
from API_Database import retrieve_register_entry, retrieve_memo_entry
from Reports import table

class OrderForm(table.HeaderTable):
    def __init__(self) -> None:
        super().__init__("Order Form")
    
    def generate_total_rows(self, data_rows: List[Dict], before_data: bool = False):
        return []