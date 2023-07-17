from __future__ import annotations
from typing import List, Dict
from Reports import khata_report, payment_list
import json
import decimal

# Custom JSON encoder for Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class Report: 
    
    _preset = {"Khata Report": khata_report.KhataReport, 
               "Payment List": payment_list.PaymentList}
    def __init__(self, 
                 title: str,
                 party_ids: List[int], 
                 supplier_ids: List[int], 
                 start_date: str, 
                 end_date: str) -> None:
        
        self.title = title.replace('_', ' ').title()
        self.table = self._preset[self.title]()
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
              # subheading = {"title": subheader_title, "dataRows": data_rows}
              subheadings.append(subheading)
          
          if len(subheadings) != 0:
            table_data["subheadings"] = subheadings
            all_headings.append(table_data)
            
        all_data["headings"] = all_headings
        json_data = json.loads(json.dumps(all_data, cls=DecimalEncoder))

        return json_data
