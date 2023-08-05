from typing import List, Dict, Tuple
from Reports import Report, KhataReport
from Entities import RegisterEntry, MemoEntry
import json

class TestKhataTable(KhataReport):

    def __init__(self) -> None:
        super().__init__()
        self.register_columns = ["register_date", "bill_number", "amount", "status"]
   
    def generate_data_rows(self, header_id: int, 
                           subheader_id: int, 
                           start_date: str, 
                           end_date: str, 
                           register_entries: List[RegisterEntry],
                           memo_entries: List[MemoEntry]
                           ) -> Tuple[List[Dict], List[Dict]]:
        """
        Generate data rows for a given header and subheader
        """

        input_args = self._generate_input_args(header_id, subheader_id, start_date, end_date)
        
        # generate data rows
        data_rows = self.generate_register_rows(register_entries, **input_args)
        # add part rows
        # if self.part_display_mode == "column":
        #     data_rows = self.merge_dicts_parallel(self.generate_part_columns(**input_args), data_rows )
        # elif self.part_display_mode == "row":
        #     data_rows.extend(self.generate_part_rows(**input_args))
        
        # # generate speical rows 
        total_rows = self.generate_total_rows(data_rows)

        cumulative = self.generate_cumulative(header_id, subheader_id, start_date, end_date)

        # format numeric columns
        for row in data_rows:
            for column in self.numeric_columns:
                try:
                    if column in row:
                        row[column] = self._format_indian_currency((row[column]))
                except:
                    print(f"Error in formatting column {column} in row {row} to Indian Currency")
        
        return data_rows, total_rows, cumulative
    
    def generate_register_rows(self, register_entries: List[RegisterEntry], **kwargs):
        """
        Generate register rows for a given header and subheader
        """
        register_columns = []
        for register_entry in register_entries:
            register_row = {}
            for column in self.register_columns:
                report_column_name=RegisterEntry._report_attribute_map[column]
                register_attr = getattr(register_entry, column)
                if column == "register_date":
                    register_row[report_column_name] = self._format_date(register_attr)
                else:
                    register_row[report_column_name] = register_attr
            # add dummy memo columns
            dummy_memo = {"memo_no": "", "memo_amt": "", "memo_date": "", "memo_type": ""}
            register_row = {**register_row, **dummy_memo}
            register_columns.append(register_row)

        return register_columns

        
    def generate_part_columns(self, supplier_id: int, party_id: int, **kwargs):
        """
        Generate part columns for a given header and subheader
        """
        part_data = self.generate_part_rows(supplier_id, party_id)
        part_columns = []
        for part in part_data:
            part_column = {}
            for part_key in part:
                if part_key == "memo_no":
                    part_column["part_no"] = part[part_key]
                elif part_key == "memo_date":
                    part_column["part_date"] = part[part_key]
                elif part_key == "memo_amt":
                    part_column["part_amt"] = part[part_key]
            part_columns.append(part_column)
        return part_columns
   
   
class TestKhataReport(Report):
    def __init__(self, 
                 title: str,
                 party_ids: List[int], 
                 supplier_ids: List[int], 
                 start_date: str, 
                 end_date: str,) -> None:
        
        super().__init__(title=title,
                         party_ids=party_ids,
                         supplier_ids=supplier_ids,
                         start_date=start_date,
                         end_date=end_date,
                         test_mode=True)
        self.table = TestKhataTable()
    
    def generate_table(self, register_entries: List[RegisterEntry], memo_entries: List[MemoEntry]):
        
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
            data_rows, special_rows, cumulative = self.table.generate_data_rows(
                header_id, 
                subheader_id, 
                self.start_date, 
                self.end_date, 
                register_entries,
                memo_entries)
            
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
        json_data = json.loads(self._dump_json(all_data))

        return json_data
        
        
        