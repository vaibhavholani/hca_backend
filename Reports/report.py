from __future__ import annotations
from typing import List, Dict
from Reports import khata_report, payment_list, supplier_register, order_form
from API_Database import parse_date, sql_date, retrieve_indivijual
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
               "Payment List": {"class": payment_list.PaymentList, "type": "header_subheader"},
               "Supplier Register": {"class": supplier_register.SupplierRegister, "type": "header"},
               "Order Form": {"class": order_form.OrderForm, "type": "header"}
               }

    def __init__(self,
                 title: str,
                 party_ids: List[int],
                 supplier_ids: List[int],
                 start_date: str,
                 end_date: str,
                 test_mode: bool = False) -> None:

        self.title = title.replace('_', ' ').title()
        # Setting the correct preset
        self.table = self._preset[self.title]["class"]()
        self.report_type = self._preset[self.title]["type"]
        self.header_ids = supplier_ids if self.table.header_supplier else party_ids
        self.subheader_ids = supplier_ids if not self.table.header_supplier else party_ids
        self.start_date = sql_date(parse_date(start_date))
        self.end_date = sql_date(parse_date(end_date))

    def generate_table(self, supplier_all: bool = False, party_all: bool = False) -> Dict:
        """
        Generate table data. Uses bulk methods when all flags are set.
        """
        if self.report_type == "header":
            if supplier_all or party_all:
                return self.generate_header_table_bulk(supplier_all, party_all)
            return self.generate_header_table()
        elif self.report_type == "header_subheader":
            if supplier_all or party_all:
                return self.generate_header_subheader_table_bulk(supplier_all, party_all)
            return self.generate_header_subheader_table()

    def generate_header_subheader_table_bulk(self, supplier_all: bool, party_all: bool) -> Dict:
        """
        Bulk version of generate_header_subheader_table that fetches all data in one query.
        When supplier_all or party_all is True, omits the corresponding IN clause.
        """
        try:
            # Initialize report structure
            all_data = {
                "title": self.title,
                "from": self.start_date,
                "to": self.end_date,
                "headings": []
            }

            # Cache for entity names to avoid repeated DB lookups
            header_names = {}
            subheader_names = {}

            # Get all data in one query with error handling
            try:
                data_rows, special_rows, cumulatives = self.table.generate_data_rows_bulk(
                    self.header_ids, self.subheader_ids, 
                    self.start_date, self.end_date,
                    supplier_all=supplier_all, party_all=party_all)
            except Exception as e:
                print(f"Error fetching bulk data: {str(e)}")
                return all_data

            # Extract header and subheader cumulatives from bulk result
            header_cumulatives = cumulatives.get('headers', {})
            subheader_cumulatives = cumulatives.get('subheaders', {})

            # Group data by header_id and subheader_id more efficiently
            grouped_data = {}
            for row in data_rows:
                header_id = row.pop("header_id", None)
                subheader_id = row.pop("subheader_id", None)
                
                if not header_id or not subheader_id:
                    continue

                if header_id not in grouped_data:
                    grouped_data[header_id] = {}
                if subheader_id not in grouped_data[header_id]:
                    grouped_data[header_id][subheader_id] = []
                grouped_data[header_id][subheader_id].append(row)

            # Format data into report structure
            for header_id in grouped_data:
                try:
                    # Get header name from cache or fetch and cache it
                    if header_id not in header_names:
                        header_names[header_id] = self.table.header_entity.get_report_name(header_id)

                    table_data = {
                        "title": header_names[header_id],
                        "subheadings": []
                    }

                    # Add header cumulative if available
                    if header_id in header_cumulatives:
                        table_data["cumulative"] = header_cumulatives[header_id]
                    
                    # Process subheadings
                    for subheader_id, subheader_data in grouped_data[header_id].items():
                        if not subheader_data:
                            continue

                        # Get subheader name from cache or fetch and cache it
                        if subheader_id not in subheader_names:
                            subheader_names[subheader_id] = self.table.subheader_entity.get_report_name(subheader_id)

                        # Calculate totals for this subheader's data
                        subheader_special_rows = self.table.generate_total_rows(subheader_data)

                        subheading = {
                            "title": subheader_names[subheader_id],
                            "dataRows": subheader_data,
                            "specialRows": subheader_special_rows,
                            "displayOnIndex": True
                        }

                        # Add subheader cumulative if available
                        subheader_key = f"{header_id}_{subheader_id}"
                        if subheader_key in subheader_cumulatives:
                            subheading["cumulative"] = subheader_cumulatives[subheader_key]

                        table_data["subheadings"].append(subheading)

                    if table_data["subheadings"]:
                        all_data["headings"].append(table_data)

                except Exception as e:
                    print(f"Error processing header {header_id}: {str(e)}")
                    continue

            return json.loads(json.dumps(all_data, cls=CustomEncoder))

        except Exception as e:
            print(f"Error generating bulk table: {str(e)}")
            return {
                "title": self.title,
                "from": self.start_date,
                "to": self.end_date,
                "headings": []
            }

    def generate_header_table_bulk(self, supplier_all: bool, party_all: bool) -> Dict:
        """
        Bulk version of generate_header_table that fetches all data in one query.
        When supplier_all or party_all is True, omits the corresponding IN clause.
        """
        try:
            # Initialize report structure
            all_data = {
                "title": self.title,
                "from": self.start_date,
                "to": self.end_date,
                "headings": []
            }

            # Cache for entity names to avoid repeated DB lookups
            header_names = {}

            # Get all data in one query with error handling
            try:
                data_rows, special_rows, base_cumulative = self.table.generate_data_rows_bulk(
                    self.header_ids, self.subheader_ids, 
                    self.start_date, self.end_date,
                    supplier_all=supplier_all, party_all=party_all)
            except Exception as e:
                print(f"Error fetching bulk data: {str(e)}")
                return all_data

            # Pre-calculate cumulative values for all headers to avoid redundant calculations
            header_cumulatives = {}
            for header_id in self.header_ids:
                try:
                    cumulative = self.table.generate_cumulative(
                        header_id, self.subheader_ids, self.start_date, self.end_date)
                    if cumulative:
                        header_cumulatives[header_id] = cumulative
                except Exception as e:
                    print(f"Error calculating cumulative for header {header_id}: {str(e)}")
                    continue

            # Group data by header_id more efficiently
            grouped_data = {}
            for row in data_rows:
                header_id = row.pop("header_id", None)
                if not header_id:
                    continue
                    
                if header_id not in grouped_data:
                    grouped_data[header_id] = []
                grouped_data[header_id].append(row)

            # Format data into report structure
            for header_id, header_data in grouped_data.items():
                try:
                    if not header_data:
                        continue

                    # Get header name from cache or fetch and cache it
                    if header_id not in header_names:
                        header_names[header_id] = self.table.header_entity.get_report_name(header_id)

                    table_data = {
                        "title": header_names[header_id],
                        "subheadings": [{
                            "title": "",
                            "dataRows": header_data,
                            "specialRows": special_rows,
                            "displayOnIndex": False
                        }]
                    }

                    # Add header cumulative if available
                    if header_id in header_cumulatives:
                        table_data["cumulative"] = header_cumulatives[header_id]

                    all_data["headings"].append(table_data)

                except Exception as e:
                    print(f"Error processing header {header_id}: {str(e)}")
                    continue

            return json.loads(json.dumps(all_data, cls=CustomEncoder))

        except Exception as e:
            print(f"Error generating bulk table: {str(e)}")
            return {
                "title": self.title,
                "from": self.start_date,
                "to": self.end_date,
                "headings": []
            }

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

            filter_subheaders = self.table.filter_subheader(
                header_id, self.subheader_ids)

            subheadings = []
            for subheader_id in filter_subheaders:
                # json for data rows
                data_rows, special_rows, cumulative = self.table.generate_data_rows(
                    header_id, subheader_id, self.start_date, self.end_date)

                if len(data_rows) != 0:
                    subheader_title = self.table.subheader_entity.get_report_name(
                        subheader_id)

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
                cumulative = self.table.generate_cumulative(
                    header_id, self.subheader_ids, self.start_date, self.end_date)
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
            data_rows, special_rows, cumulative = self.table.generate_data_rows(
                header_id, self.subheader_ids, self.start_date, self.end_date)

            if len(data_rows) != 0:
                table_data["subheadings"] = [
                    {"title": "", "dataRows": data_rows, "specialRows": special_rows, "displayOnIndex": False}]

                # calculate cumulative values only if cumulatiive is no an empty dict
                cumulative = self.table.generate_cumulative(
                    header_id, self.subheader_ids, self.start_date, self.end_date)

                if len(cumulative) != 0:
                    table_data["cumulative"] = cumulative

                all_headings.append(table_data)

        all_data["headings"] = all_headings
        json_data = json.loads(json.dumps(all_data, cls=CustomEncoder))

        return json_data

    def _dump_json(self, data: Dict) -> None:
        return json.dumps(data, cls=CustomEncoder)
