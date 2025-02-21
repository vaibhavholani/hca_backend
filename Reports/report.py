from __future__ import annotations
from typing import List, Dict
from Reports import khata_report, payment_list, supplier_register, order_form
from API_Database import parse_date, sql_date, retrieve_indivijual
import json
import decimal
from datetime import datetime

class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        """Custom default method for JSON encoding of datetime and numeric types."""
        if isinstance(obj, datetime):
            return obj.strftime('%d/%m/%Y')
        elif isinstance(obj, decimal.Decimal) or isinstance(obj, float):
            return int(obj)
        return super(CustomEncoder, self).default(obj)

class Report:
    _preset = {'Khata Report': {'class': khata_report.KhataReport, 'type': 'header_subheader'}, 'Payment List': {'class': payment_list.PaymentList, 'type': 'header_subheader'}, 'Supplier Register': {'class': supplier_register.SupplierRegister, 'type': 'header'}, 'Order Form': {'class': order_form.OrderForm, 'type': 'header'}}

    def __init__(self, title: str, party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str, test_mode: bool=False) -> None:
        """Initializes the Report object with title, party IDs, supplier IDs, date range, and an optional test mode flag."""
        self.title = title.replace('_', ' ').title()
        self.table = self._preset[self.title]['class']()
        self.report_type = self._preset[self.title]['type']
        self.header_ids = supplier_ids if self.table.header_supplier else party_ids
        self.subheader_ids = supplier_ids if not self.table.header_supplier else party_ids
        self.start_date = sql_date(parse_date(start_date))
        self.end_date = sql_date(parse_date(end_date))

    def generate_table(self, supplier_all: bool=False, party_all: bool=False) -> Dict:
        """
        Generate table data. Uses bulk methods when all flags are set.
        """
        if self.report_type == 'header':
            if self.table.data_rows_bulk is not None:
                return self.generate_header_table_bulk(supplier_all, party_all)
            return self.generate_header_table()
        elif self.report_type == 'header_subheader':
            if self.table.data_rows_bulk is not None:
                return self.generate_header_subheader_table_bulk(supplier_all, party_all)
            return self.generate_header_subheader_table()

    def generate_header_subheader_table_bulk(self, supplier_all: bool, party_all: bool) -> Dict:
        """
        Bulk version of generate_header_subheader_table that fetches all data in one query.
        When supplier_all or party_all is True, omits the corresponding IN clause.
        """
        try:
            all_data = {'title': self.title, 'from': self.start_date, 'to': self.end_date, 'headings': []}
            header_names = {}
            subheader_names = {}
            try:
                (data_rows, part_data, special_rows, cumulatives) = self.table.generate_data_rows_bulk(self.header_ids, self.subheader_ids, self.start_date, self.end_date, supplier_all=supplier_all, party_all=party_all)
            except Exception as e:
                print(f'Error fetching bulk data: {str(e)}')
                return all_data
            header_cumulatives = cumulatives.get('headers', {})
            subheader_cumulatives = cumulatives.get('subheaders', {})
            current_header = None
            current_subheader = None
            current_header_data = None
            current_subheader_data = None
            for row in data_rows:
                header_id = row.pop('header_id', current_header)
                subheader_id = row.pop('subheader_id', current_subheader)
                if header_id != current_header:
                    if current_header_data and current_header_data['subheadings']:
                        all_data['headings'].append(current_header_data)
                    current_header = header_id
                    current_header_data = {'title': header_names.get(header_id) or self.table.header_entity.get_report_name(header_id), 'subheadings': []}
                    header_names[header_id] = current_header_data['title']
                    if header_id in header_cumulatives:
                        current_header_data['cumulative'] = header_cumulatives[header_id]
                    current_subheader = None
                if subheader_id != current_subheader:
                    current_subheader = subheader_id
                    current_subheader_data = {'title': subheader_names.get(subheader_id) or self.table.subheader_entity.get_report_name(subheader_id), 'dataRows': [], 'partRows': [], 'displayOnIndex': True}
                    if part_data:
                        current_subheader_data['partRows'] = part_data.get(header_id, {}).get(subheader_id, [])
                    subheader_names[subheader_id] = current_subheader_data['title']
                    subheader_key = f'{header_id}_{subheader_id}'
                    if subheader_key in subheader_cumulatives:
                        current_subheader_data['cumulative'] = subheader_cumulatives[subheader_key]
                    current_header_data['subheadings'].append(current_subheader_data)
                current_subheader_data['dataRows'].append(row)
            if current_header_data and current_header_data['subheadings']:
                all_data['headings'].append(current_header_data)
            for heading in all_data['headings']:
                for subheading in heading['subheadings']:
                    if self.table.part_display_mode == 'column':
                        subheading['dataRows'] = self.table.merge_dicts_parallel(subheading.pop('partRows'), subheading['dataRows'])
                    elif self.table.part_display_mode == 'row':
                        subheading['dataRows'].extend(subheading.pop('partRows'))
                    subheading['specialRows'] = self.table.generate_total_rows(subheading['dataRows'])
                    for row in subheading['dataRows']:
                        for column in self.table.numeric_columns:
                            try:
                                if column in row:
                                    row[column] = self.table._format_indian_currency(row[column])
                            except Exception as e:
                                print(f'Error formatting column {column}: {str(e)}')
            return json.loads(json.dumps(all_data, cls=CustomEncoder))
        except Exception as e:
            print(f'Error generating bulk table: {str(e)}')
            return {'title': self.title, 'from': self.start_date, 'to': self.end_date, 'headings': []}

    def generate_header_table_bulk(self, supplier_all: bool, party_all: bool) -> Dict:
        """
        Bulk version of generate_header_table that fetches all data in one query.
        When supplier_all or party_all is True, omits the corresponding IN clause.
        """
        try:
            all_data = {'title': self.title, 'from': self.start_date, 'to': self.end_date, 'headings': []}
            header_names = {}
            try:
                (data_rows, part_data, special_rows, cumulatives) = self.table.generate_data_rows_bulk(self.header_ids, self.subheader_ids, self.start_date, self.end_date, supplier_all=supplier_all, party_all=party_all)
            except Exception as e:
                print(f'Error fetching bulk data: {str(e)}')
                return all_data
            current_header = None
            current_header_data = None
            for row in data_rows:
                header_id = row.pop('header_id', None)
                subheader_id = row.pop('subheader_id', None)
                if not header_id:
                    continue
                if header_id != current_header:
                    if current_header_data and current_header_data['subheadings'][0]['dataRows']:
                        all_data['headings'].append(current_header_data)
                    current_header = header_id
                    current_header_data = {'title': header_names.get(header_id) or self.table.header_entity.get_report_name(header_id), 'subheadings': [{'title': '', 'dataRows': [], 'partRows': [], 'displayOnIndex': False}]}
                    header_names[header_id] = current_header_data['title']
                    if header_id in cumulatives['headers']:
                        current_header_data['cumulative'] = cumulatives['headers'][header_id]
                    if part_data:
                        current_header_data['subheadings'][0]['partRows'] = part_data.get(header_id, [])
                current_header_data['subheadings'][0]['dataRows'].append(row)
            if current_header_data and current_header_data['subheadings'][0]['dataRows']:
                all_data['headings'].append(current_header_data)
            for heading in all_data['headings']:
                subheading = heading['subheadings'][0]
                if self.table.part_display_mode == 'column':
                    subheading['dataRows'] = self.table.merge_dicts_parallel(subheading.pop('partRows'), subheading['dataRows'])
                elif self.table.part_display_mode == 'row':
                    subheading['dataRows'].extend(subheading.pop('partRows'))
                else:
                    subheading.pop('partRows')
                subheading['specialRows'] = self.table.generate_total_rows(subheading['dataRows'])
                for row in subheading['dataRows']:
                    for column in self.table.numeric_columns:
                        try:
                            if column in row:
                                row[column] = self.table._format_indian_currency(row[column])
                        except Exception as e:
                            print(f'Error formatting column {column}: {str(e)}')
            return json.loads(json.dumps(all_data, cls=CustomEncoder))
        except Exception as e:
            print(f'Error generating bulk table: {str(e)}')
            return {'title': self.title, 'from': self.start_date, 'to': self.end_date, 'headings': []}

    def generate_header_subheader_table(self) -> Dict:
        """
        Generate data rows such that there is a table between in each header and subheader
        """
        all_data = {}
        all_data['title'] = self.title
        all_data['from'] = self.start_date
        all_data['to'] = self.end_date
        all_headings = []
        for header_id in self.header_ids:
            table_data = {}
            title = self.table.header_entity.get_report_name(header_id)
            table_data['title'] = title
            filter_subheaders = self.table.filter_subheader(header_id, self.subheader_ids)
            subheadings = []
            for subheader_id in filter_subheaders:
                (data_rows, special_rows, cumulative) = self.table.generate_data_rows(header_id, subheader_id, self.start_date, self.end_date)
                if len(data_rows) != 0:
                    subheader_title = self.table.subheader_entity.get_report_name(subheader_id)
                    subheading = {'title': subheader_title, 'dataRows': data_rows, 'specialRows': special_rows, 'displayOnIndex': True}
                    if len(cumulative) != 0:
                        subheading['cumulative'] = cumulative
                    subheadings.append(subheading)
            if len(subheadings) != 0:
                table_data['subheadings'] = subheadings
                cumulative = self.table.generate_cumulative(header_id, self.subheader_ids, self.start_date, self.end_date)
                if len(cumulative) != 0:
                    table_data['cumulative'] = cumulative
                all_headings.append(table_data)
        all_data['headings'] = all_headings
        json_data = json.loads(json.dumps(all_data, cls=CustomEncoder))
        return json_data

    def generate_header_table(self) -> Dict:
        """
        Generate data rows such that there is only one table between in each header and all it's subheaders
        """
        all_data = {}
        all_data['title'] = self.title
        all_data['from'] = self.start_date
        all_data['to'] = self.end_date
        all_headings = []
        for header_id in self.header_ids:
            table_data = {}
            title = self.table.header_entity.get_report_name(header_id)
            table_data['title'] = title
            (data_rows, special_rows, cumulative) = self.table.generate_data_rows(header_id, self.subheader_ids, self.start_date, self.end_date)
            if len(data_rows) != 0:
                table_data['subheadings'] = [{'title': '', 'dataRows': data_rows, 'specialRows': special_rows, 'displayOnIndex': False}]
                cumulative = self.table.generate_cumulative(header_id, self.subheader_ids, self.start_date, self.end_date)
                if len(cumulative) != 0:
                    table_data['cumulative'] = cumulative
                all_headings.append(table_data)
        all_data['headings'] = all_headings
        json_data = json.loads(json.dumps(all_data, cls=CustomEncoder))
        return json_data

    def _dump_json(self, data: Dict) -> None:
        """Serializes the report data into JSON format using a custom encoder."""
        return json.dumps(data, cls=CustomEncoder)