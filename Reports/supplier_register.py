from typing import Dict, List
from API_Database import retrieve_register_entry, retrieve_memo_entry
from Reports import table

class SupplierRegister(table.HeaderTable):

    def __init__(self) -> None:
        """Initializes the Supplier Register report with a preset title."""
        super().__init__('Supplier Register')

    def generate_total_rows(self, data_rows: List[Dict], before_data: bool=False):
        """
        Generate total rows for Supplier Register with optimized calculations.
        Uses a single pass through data with dictionary-based totals.
        """
        total_rows = []
        totals = {column: 0 for column in self.total_rows_columns}
        try:
            for row in data_rows:
                for column in self.total_rows_columns:
                    if column in row:
                        value = str(row[column]).replace(',', '') if row[column] != '' else '0'
                        value = value.split('.')[0]
                        amount = int(value)
                        totals[column] += amount
            for column in self.total_rows_columns:
                total = totals[column]
                label = 'Pending (=) ' if column == 'pending_amt' else 'Total (=) '
                total_rows.append(self._total_row_dict(label, total, column, before_data))
        except Exception as e:
            print(f'Error in generate_total_rows: {str(e)}')
        return total_rows