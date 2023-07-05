from __future__ import annotations
from typing import List, Dict
from Indivijuval import Supplier, Party
from API_Database import efficiency
from API_Database import retrieve_register_entry, retrieve_indivijual, retrieve_partial_payment
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

        # define report presets
        self.header_entity = Party.Party if self.title == "Khata Report" else Supplier.Supplier
        self.subheader_entity = Supplier.Supplier if self.title == "Khata Report" else Party.Party
        
    def generate_table(self) -> Dict:
        
        all_data = {}
        all_data["title"] = self.title
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
            "numeric_columns": ["amount", "memo_amt"],
            "total_rows_columns": ["amount", "memo_amt"]},
        "Supplier Register": {
            "header_entity": Supplier.Supplier,
            "subheader_entity": Party.Party,
            "data_rows": retrieve_register_entry.get_supplier_register_data, 
            "numeric_columns": ["amount"],
            "total_rows_columns": ["amount"]},
          "Payment List": {
            "header_entity": Party.Party,
            "subheader_entity": Supplier.Supplier,
            "data_rows": retrieve_register_entry.get_payment_list_data, 
            "numeric_columns": ["amount"],
            "total_rows_columns": ["amount"]}
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
        # generate speical rows 
        total_rows = self.generate_total_rows(data_rows)
        total_rows.append(self.generate_special_row("Part", "5000", "amount", False))

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
      total_rows = []
      for column in self.total_rows_columns:
          
          total = 0
          try:
            for row in data_rows:
                if column in row:
                  total += int(row[column])
            total = self._format_indian_currency(total)
            total_rows.append({"name": "Total", "value": total, "column": column, "beforeData": before_data})
          except:
             print(f"Error in generating total rows for column {column} in row {row}")
      return total_rows
    
    def generate_special_row(self, entity_name: str, value: str, column: str, before_data: bool = False):
      return {"name": entity_name, "value": self._format_indian_currency(value), "column": column, "beforeData": before_data}
    

    @staticmethod
    def _format_indian_currency(number):
      s, *d = str(number).partition(".")
      r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
      return "".join([r] + d)