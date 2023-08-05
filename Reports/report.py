from __future__ import annotations
from typing import List, Dict
from Reports import khata_report, payment_list, supplier_register
from API_Database import parse_date, sql_date
import json
import decimal
from datetime import datetime

# Custom JSON encoder for Decimal objects
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%d/%m/%Y")
        elif isinstance(obj, decimal.Decimal) or isinstance(obj, float):
            return int(obj)
        
        return super(CustomEncoder, self).default(obj)

class Report: 
    
    _preset = {"Khata Report": {"class": khata_report.KhataReport, "type": "header_subheader"},
               "Payment List": {"class": payment_list.PaymentList, "type": "header_subheader"} ,
               "Supplier Register": {"class": supplier_register.SupplierRegister, "type": "header"}
              }

    def __init__(self, 
                 title: str,
                 party_ids: List[int], 
                 supplier_ids: List[int], 
                 start_date: str, 
                 end_date: str, 
                 test_mode: bool= False) -> None:
        
        self.title = title.replace('_', ' ').title()
        # Setting the correct preset
        self.table = self._preset[self.title]["class"]()
        self.report_type = self._preset[self.title]["type"]
        self.header_ids = supplier_ids if self.table.header_supplier else party_ids
        self.subheader_ids = supplier_ids if not self.table.header_supplier else party_ids
        self.start_date = sql_date(parse_date(start_date))
        self.end_date = sql_date(parse_date(end_date))

        # self.start_date = (datetime.datetime.strptime(start_date, "%Y-%m-%d")).strftime('%d/%m/%Y')
        # self.end_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d")).strftime('%d/%m/%Y')
    
    def generate_table(self) -> Dict:
        if self.report_type == "header":
          return self.generate_header_table()
        elif self.report_type == "header_subheader":
          return self.generate_header_subheader_table()
        
    def generate_header_subheader_table(self) -> Dict:
        """
        Generate data rows such that there is a table between in each header and subheader
        """
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
            data_rows, special_rows, cumulative = self.table.generate_data_rows(header_id, subheader_id, self.start_date, self.end_date)
            
            if len(data_rows) != 0:
              subheader_title = self.table.subheader_entity.get_report_name(subheader_id)

              subheading = {"title": subheader_title, 
                            "dataRows": data_rows, 
                            "specialRows": special_rows, 
                            "displayOnIndex": True}
              if len(cumulative) != 0:
                subheading["cumulative"] = cumulative
              
              subheadings.append(subheading)
          
          if len(subheadings) != 0:
            table_data["subheadings"] = subheadings
            # calculate cumulative values only if cumulatiive is no an empty dict
            cumulative = self.table.generate_cumulative(header_id, self.subheader_ids, self.start_date, self.end_date)
            if len(cumulative) != 0:
              table_data["cumulative"] = cumulative
            all_headings.append(table_data)
            
        all_data["headings"] = all_headings
        json_data = json.loads(json.dumps(all_data, cls=CustomEncoder))

        return json_data
  
    def generate_header_table(self) -> Dict:
          """
          Generate data rows such that there is only one table between in each header and all it's subheaders
          """
          all_data = {}
          all_data["title"] = self.title
          all_data["from"] = self.start_date
          all_data["to"] = self.end_date
          all_headings = []
          
          for header_id in self.header_ids:
            table_data = {}

            title = self.table.header_entity.get_report_name(header_id)

            table_data["title"] = title
            
            # json for data rows
            data_rows, special_rows, cumulative = self.table.generate_data_rows(header_id, self.subheader_ids, self.start_date, self.end_date)
            
            if len(data_rows) != 0:
              table_data["subheadings"] = [{"title": "", "dataRows": data_rows, "specialRows": special_rows, "displayOnIndex": False}]
              
              # calculate cumulative values only if cumulatiive is no an empty dict
              cumulative = self.table.generate_cumulative(header_id, self.subheader_ids, self.start_date, self.end_date)

              if len(cumulative) != 0:
                table_data["cumulative"] = cumulative
              
              all_headings.append(table_data)
              
          all_data["headings"] = all_headings
          json_data = json.loads(json.dumps(all_data, cls=CustomEncoder))

          return json_data

    def _dump_json(self, data: Dict) -> None:
      return json.dumps(data, cls=CustomEncoder)