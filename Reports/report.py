from __future__ import annotations
from typing import List, Dict
from Indivijuval import Supplier, Party
from API_Database import efficiency
from API_Database import retrieve_register_entry, retrieve_partial_payment
import datetime
import json
import decimal

# Custom JSON encoder for Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)
    
class Report: 
    def __init__(self, 
                 title: str,
                 party_ids: List[int], 
                 supplier_ids: List[int], 
                 start_date: str, 
                 end_date: str) -> None:
        
        self.title = title.replace('_', ' ').title()
        self.table = Table(self.title)
        self.header_ids = supplier_ids if self.table.header_supplier else party_ids
        self.subheader_ids = supplier_ids if not self.table.header_supplier else party_ids
        self.start_date = start_date
        self.end_date = end_date

        # self.start_date = (datetime.datetime.strptime(start_date, "%Y-%m-%d")).strftime('%d/%m/%Y')
        # self.end_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d")).strftime('%d/%m/%Y')
        
    def generate_table(self) -> Dict:
        
        all_data = {}
        all_data["title"] = self.title
        all_data["from"] = self.start_date
        all_data["to"] = self.end_date
        all_headings = []
        
        for header_id in self.header_ids:
          table_data = {}

          title = self.table.header_entity.get_report_name(header_id)

          table_data["title"] = title
          
          filter_subheaders = self.table.filter_subheader(header_id, self.subheader_ids)
          
          subheadings = []
          for subheader_id in filter_subheaders:
            
            # json for data rows
            data_rows, special_rows = self.table.generate_data_rows(header_id, subheader_id, self.start_date, self.end_date)
            
            if len(data_rows) != 0:
              subheader_title = self.table.subheader_entity.get_report_name(subheader_id)

              subheading = {"title": subheader_title, "dataRows": data_rows, "specialRows": special_rows}
              subheadings.append(subheading)
          
          if len(subheadings) != 0:
            table_data["subheadings"] = subheadings
            all_headings.append(table_data)
            
        all_data["headings"] = all_headings
        json_data = json.loads(json.dumps(all_data, cls=DecimalEncoder))

        return json_data

class Table:
    
    _preset = {
        "Khata Report": {
            "header_entity": Party.Party,
            "subheader_entity": Supplier.Supplier,
            "data_rows": retrieve_register_entry.get_khata_data_by_date,
            "numeric_columns": ["bill_amt", "memo_amt", "chk_amt"],
            "total_rows_columns": ["bill_amt", "memo_amt",]},
        "Supplier Register": {
            "header_entity": Supplier.Supplier,
            "subheader_entity": Party.Party,
            "data_rows": retrieve_register_entry.get_supplier_register_data, 
            "numeric_columns": ["bill_amt"],
            "total_rows_columns": ["bill_amt"]},
          "Payment List": {
            "header_entity": Party.Party,
            "subheader_entity": Supplier.Supplier,
            "data_rows": retrieve_register_entry.get_payment_list_data, 
            "numeric_columns": ["bill_amt"],
            "total_rows_columns": ["bill_amt"]}
            }
        
    def __init__(self, title: str) -> None:
        self.title = title
        self.header_entity = self._preset[title]["header_entity"]
        self.subheader_entity = self._preset[title]["subheader_entity"]
        self.filter_subheader = efficiency.filter_out_parties if self.header_entity is Supplier.Supplier else efficiency.filter_out_supplier
        self.data_rows = self._preset[title]["data_rows"]
        self.numeric_columns = self._preset[title]["numeric_columns"]
        self.total_rows_columns = self._preset[title]["total_rows_columns"]

        # to auto select header_entity
        self.header_supplier = True if self.header_entity is Supplier.Supplier else False
    
    def generate_data_rows(self, header_id: int, subheader_id: int, start_date: str, end_date: str):
        """
        Generate data rows for a given header and subheader
        """
        input_args = {
            "party_id" if self.header_entity is Party.Party else "supplier_id": header_id,
            "supplier_id" if self.subheader_entity is Supplier.Supplier else "party_id": subheader_id,
            "start_date": start_date,
            "end_date": end_date
        }
        
        data_rows = self.data_rows(**input_args)
        # add part rows
        data_rows.extend(self.generate_part_rows(**input_args))
        
        # generate speical rows 
        total_rows = self.generate_total_rows(data_rows)

        # format numeric columns
        for row in data_rows:
            for column in self.numeric_columns:
                try:
                    if column in row:
                      row[column] = self._format_indian_currency((row[column]))
                except:
                    print(f"Error in formatting column {column} in row {row} to Indian Currency")
        
        return data_rows, total_rows
    
    def generate_total_rows(self, data_rows: Dict, before_data: bool = False):
      """
      Generate total values for certain columns
      """

      # ASSUMPTION: "memo_amt" total must show decreased GR and LESS values and then show total value
      # ASSUMPTION: "bill_amt" total must remove total GR and LESS in them and then show pending value
      total_rows = []

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
                  amount = int(row[column])
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
    
    def generate_special_row(self, entity_name: str, value: str, column: str, before_data: bool = False):
      return {"name": entity_name, "value": self._format_indian_currency(value), "column": column, "beforeData": before_data}
    
    def generate_part_rows(self, supplier_id: int, party_id: int, **kwargs):
      """
      Generate part rows for a given header and subheader
      """
      return retrieve_partial_payment.get_partial_payment(supplier_id, party_id)
    
    def generate_part_columns(self, supplier_id: int, party_id: int, **kwargs):
      """
      Generate part columns for a given header and subheader
      """
      return retrieve_partial_payment.get_partial_payment_columns(supplier_id, party_id)
       

    def _total_row_dict(self, name: str, numeric: int, column: str, before_data: bool, negative: bool = False):
      value = self._format_indian_currency(numeric, negative=negative)
      return {"name": name, "value": value, "column": column, "numeric": numeric, "beforeData": before_data}
    
    @staticmethod
    def _format_indian_currency(number, negative: bool = False):
      s, *d = str(number).partition(".")
      r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
      if negative:
        return "".join(["- ", r] + d)
      return "".join([r] + d)
    
