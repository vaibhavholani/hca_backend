from typing import Dict
from Reports import table

class KhataReport(table.HeaderSubheaderTable):
    def __init__(self) -> None:
        super().__init__("Khata Report")
    
    def generate_total_rows(self, data_rows: Dict, before_data: bool = False):
      # ASSUMPTION: "memo_amt" total must show decreased GR and LESS values and then show total value
      # ASSUMPTION: "bill_amt" total must remove total GR and LESS in them and then show pending value
      total_rows = []
      header_total_rows = []

      # WARNING: only used when pending amt when both bill_amt and memo_amt are calculated 
      bill_subtotal = 0
      memo_subtotal = 0

      for column in self.total_rows_columns:
          total = 0
          total_gr = 0
          total_less = 0
          total_paid = 0
          gr_percent = 0
          less_percent = 0
          try:
            for row in data_rows:
                if column in row:
                  amount = int(row[column]) if row[column] != "" else 0
                  total += amount
                  if column == "memo_amt" and "memo_type" in row:
                    if row["memo_type"] == "G":
                      total_gr += amount
                    if row["memo_type"] == "D":
                      total_less += amount

            # Additional Calculation
            total_paid = total - total_gr - total_less
            if total != 0:
                gr_percent = total_gr / total * 100
                less_percent = total_less / total * 100

            # Generate total rows
            total_rows.append(self._total_row_dict("Subtotal", total, column, before_data))
            if column == "memo_amt":
              # adding information for peding amount caclulation
              memo_subtotal = total

              total_rows.extend(
              [self._total_row_dict(f"{gr_percent:.2f}% GR (-)", total_gr, column, before_data, negative=True),
              self._total_row_dict(f"{less_percent:.2f}% Less (-)", total_less, column, before_data, negative=True),
              self._total_row_dict("Total Paid (=)", total_paid, column, before_data),]
              )
            if column == "bill_amt":
               bill_subtotal = total
          
          except:
             print(f"Error in generating total rows for column {column} in row {row}")
      
      # add pending amount if both bill_amt and memo_amt are calculated
      if "bill_amt" in self.total_rows_columns and "memo_amt" in self.total_rows_columns:
        pending_amt = bill_subtotal - memo_subtotal
        total_rows.append(self._total_row_dict("Paid+GR (-)", memo_subtotal, "bill_amt", before_data, negative=True))
        total_rows.append(self._total_row_dict("Pending (=)", pending_amt, "bill_amt", before_data))
      
      return total_rows