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
                 header_ids: List[int], 
                 subheader_ids: List[int], 
                 start_date: str, 
                 end_date: str) -> None:
        
        self.title = title.replace('_', ' ').title()
        self.header_ids = header_ids
        self.subheader_ids = subheader_ids
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

          title = self.header_entity.get_report_name(header_id)

          table_data["title"] = title
          
          filter_subheaders = efficiency.filter_out_supplier(header_id, self.subheader_ids)
          
          subheadings = []
          for subheader_id in filter_subheaders:
            
            add_table = True
            # json for data rows
            data_rows = retrieve_register_entry.get_khata_data_by_date(subheader_id, header_id, self.start_date, self.end_date)
            
            if len(data_rows) != 0:
              subheader_title = self.subheader_entity.get_report_name(subheader_id)

              # extract json for total rows
              total_rows = self.generate_total_rows(data_rows, ["amount", "memo_amt"])
              # extract json for special rows
              total_rows.append(self.generate_special_row("Part", "5000", "amount", False))

              subheading = {"title": subheader_title, "dataRows": data_rows, "specialRows": total_rows}
              subheadings.append(subheading)
          
          if len(subheadings) != 0:
            table_data["subheadings"] = subheadings
            all_headings.append(table_data)
            
        all_data["headings"] = all_headings
        json_data = json.loads(json.dumps(all_data, cls=DecimalEncoder))
        return json_data
    
    def generate_total_rows(self, data_rows: Dict, columnNames: List[str], before_data: bool = False):
      """
      Generate total values for certain columns
      """
      total_rows = []
      for column in columnNames:
          
          total = 0
          try:
            for row in data_rows:
                if column in row:
                  total += int(row[column])
            total_rows.append({"name": "Total", "value": total, "column": column, "beforeData": before_data})
          except:
             print(f"Error in generating total rows for column {column} in row {row}")
      return total_rows
    
    def generate_special_row(self, entity_name: str, value: str, column: str, before_data: bool = False):
      return {"name": entity_name, "value": value, "column": column, "beforeData": before_data}
          
                
                
        

class Table:
    """
    Returns table data json in the following format
    {
        "title": "Party Name: ...",
        "subheadings": [
          {
            "title": "Supplier Name: ...",
            "dataRows": [{  }],
            "specialRows": [
              {"name": "Total", "value": 1200000.0,"column": "BillNo", "beforeData": false}
            ]
          },
        ]
      }
    """
    def __init__(self) -> None:
        pass