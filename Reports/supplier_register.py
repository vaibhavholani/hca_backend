from typing import Dict, List
from API_Database import retrieve_register_entry, retrieve_memo_entry
from Reports import table

class SupplierRegister(table.HeaderTable):
    def __init__(self) -> None:
        super().__init__("Supplier Register")
    
    def generate_total_rows(self, data_rows: List[Dict], before_data: bool = False):
        total_rows = []

        for column in self.total_rows_columns:
            total = 0
            try:
                for row in data_rows:
                    if column in row:
                        amount = int(row[column]) if row[column] != "" else 0
                        total += amount
                # Generate total rows
                if (column == "bill_amt"): 
                    total_rows.append(self._total_row_dict("Total (=) ", total, column, before_data))
                elif (column == "pending_amt"):
                    total_rows.append(self._total_row_dict("Pending (=) ", total, column, before_data))
                else:
                    total_rows.append(self._total_row_dict("Total (=) ", total, column, before_data))
            except:
                print(f"Error in generating total rows for column {column} in row {row}")
        
        return total_rows