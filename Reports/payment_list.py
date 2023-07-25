from typing import Dict, List
from API_Database import retrieve_register_entry, retrieve_memo_entry
from Reports import table

class PaymentList(table.Table):
    def __init__(self) -> None:
        super().__init__("Payment List")
    
    def generate_cumulative(self, header_ids: List[int], 
                                subheader_ids: List[int], 
                                start_date: str, 
                                end_date: str,):
        
        input_args = self._generate_input_args(header_ids, subheader_ids, start_date, end_date)

        total_pending_amount = retrieve_register_entry.generate_total(**input_args, 
                                               column_name="amount", 
                                               pending=True)
        
        total_part = retrieve_memo_entry.generate_memo_total(**input_args,
                                                             memo_type="PR")
        pending = total_pending_amount - total_part

        return {"name": "Total Pending", "value": self._format_indian_currency(pending)}
    
    def generate_total_rows(self, data_rows: Dict, before_data: bool = False):
        total_rows = []
        # total for the all tables between supplier and party
        header_total_rows = []
        
        # WARNING: only used when pending amt when both bill_amt and memo_amt are calculated 
        bill_subtotal = 0
        part_subtotal = 0

        for column in self.total_rows_columns:
            total = 0
            total_under_sixty = 0
            total_above_sixty = 0
            total_above_one_twenty = 0
            try:
                for row in data_rows:
                    if column in row:
                        amount = int(row[column]) if row[column] != "" else 0
                        total += amount
                        if column == "bill_amt" and "days" in row:
                            days = int(row["days"])
                            if  days <= 60:
                                total_under_sixty += amount
                            if days > 60 and days <= 120:
                                total_above_sixty += amount
                            if days > 120:
                                total_above_one_twenty += amount

                # Generate total rows
                
                if column == "bill_amt":
                    bill_subtotal = total

                    total_rows.extend(
                    [
                    self._total_row_dict(f"<60 days (+)", total_under_sixty, column, before_data),
                    self._total_row_dict(f"60-120 days (+)", total_above_sixty, column, before_data),
                    self._total_row_dict(f">120 days (+)", total_above_one_twenty, column, before_data),
                    self._total_row_dict("Subtotal (=)", total, column, before_data),]
                    )
                elif column=="part_amt": 
                    part_subtotal = total
                    total_rows.append(self._total_row_dict("Total (=)", total, column, before_data))
            except:
                print(f"Error in generating total rows for column {column} in row {row}")
      
        # add pending amount if both bill_amt and memo_amt are calculated
        if "bill_amt" in self.total_rows_columns and "part_amt" in self.total_rows_columns:
            pending_amt = bill_subtotal - part_subtotal
            total_rows.append(self._total_row_dict("Part (-)", part_subtotal, "bill_amt", before_data, negative=True))
            total_rows.append(self._total_row_dict("Pending (=)", pending_amt, "bill_amt", before_data))
      
        return total_rows