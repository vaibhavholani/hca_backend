from __future__ import annotations
from typing import List, Dict, Union
from datetime import datetime
from Individual import Supplier, Party
from API_Database import efficiency, parse_date
from API_Database import retrieve_register_entry, retrieve_partial_payment, retrieve_order_form
from itertools import zip_longest


class MetaTable:

    _preset = {
        "Khata Report": {
            "header_entity": Party,
            "subheader_entity": Supplier,
            "data_rows": retrieve_register_entry.get_khata_data_by_date,
            "numeric_columns": ["bill_amt", "memo_amt", "chk_amt"],
            "total_rows_columns": ["bill_amt", "memo_amt",],
            "part_display_mode": "row"},
        "Supplier Register": {
            "header_entity": Supplier,
            "subheader_entity": Party,
            "data_rows": retrieve_register_entry.get_supplier_register_data,
            "numeric_columns": ["bill_amt", "pending_amt"],
            "total_rows_columns": ["bill_amt", "pending_amt"],
            "part_display_mode": "none"
        },
        "Payment List": {
            "header_entity": Party,
            "subheader_entity": Supplier,
            "data_rows": retrieve_register_entry.get_payment_list_data,
            "numeric_columns": ["bill_amt", "part_amt"],
            "total_rows_columns": ["part_amt", "bill_amt"],
            "part_display_mode": "column"},
        "Order Form": {
            "header_entity": Supplier,
            "subheader_entity": Party,
            "data_rows": retrieve_order_form.get_order_form_report_data,
            "numeric_columns": ["order_no"],
            "total_rows_columns": [],
            "part_display_mode": "none"
        }
    }

    def __init__(self, title: str) -> None:

        self.title = title
        self.header_entity = self._preset[title]["header_entity"]
        self.subheader_entity = self._preset[title]["subheader_entity"]
        self.filter_subheader = efficiency.filter_out_parties if self.header_entity is Supplier else efficiency.filter_out_supplier
        self.data_rows = self._preset[title]["data_rows"]
        self.numeric_columns = self._preset[title]["numeric_columns"]
        self.total_rows_columns = self._preset[title]["total_rows_columns"]
        self.part_display_mode = self._preset[title]["part_display_mode"]

        # to auto select header_entity
        self.header_supplier = True if self.header_entity is Supplier else False

    def generate_total_rows(self, data_rows: Dict, before_data: bool = False):
        """
        Generate total values for certain columns
        """
        raise NotImplementedError

    def generate_cumulative(self,
                            header_ids: Union[List[int], int],
                            subheader_ids: Union[List[int], int],
                            start_date: str,
                            end_date: str):
        """
        Generate cumulative values for certain columns
        """
        return {}

    def generate_part_rows(self, supplier_id: int, party_id: int, **kwargs):
        """
        Generate part rows for a given header and subheader
        """
        return retrieve_partial_payment.get_partial_payment(supplier_id, party_id)

    def _generate_special_row(self, entity_name: str, value: str, column: str, before_data: bool = False):
        return {"name": entity_name, "value": self._format_indian_currency(value), "column": column, "beforeData": before_data}

    def _total_row_dict(self, name: str, numeric: int, column: str, before_data: bool, negative: bool = False):
        value = self._format_indian_currency(numeric, negative=negative)
        return {"name": name, "value": value, "column": column, "numeric": numeric, "beforeData": before_data}

    def _generate_input_args(self, header_ids: Union[List[int], int],
                             subheader_ids: Union[List[int], int],
                             start_date: str,
                             end_date: str,
                             force_list_args: bool = False,
                             force_int_args: bool = False):
        """
        Function to map header and subheader ids to party_id and supplier_id
        """
        # handle the casee when header_ids and subheader_ids are int
        if force_int_args or (isinstance(header_ids, int) and isinstance(subheader_ids, int) and not force_list_args):
            input_args = {
                "party_id" if self.header_entity is Party else "supplier_id": header_ids,
                "supplier_id" if self.subheader_entity is Supplier else "party_id": subheader_ids,
                "start_date": start_date,
                "end_date": end_date
            }
        else:
            input_args = {
                "party_ids" if self.header_entity is Party else "supplier_ids": header_ids,
                "supplier_ids" if self.subheader_entity is Supplier else "party_ids": subheader_ids,
                "start_date": start_date,
                "end_date": end_date
            }
        return input_args

    @staticmethod
    def _format_indian_currency(number, negative: bool = False):
        s, *d = str(number).partition(".")
        r = ",".join([s[x-2:x]
                     for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        if negative:
            return "".join(["- ", r] + d)
        return "".join([r] + d)

    @staticmethod
    def merge_dicts_parallel(dict_a, dict_b):
        merged_dicts = []
        for dict_a_i, dict_b_i in zip_longest(dict_a, dict_b, fillvalue={}):
            # remove keys in dict_b_i which are already in dict_a_i
            for key in dict_a_i:
                if key in dict_b_i:
                    dict_b_i.pop(key)
                    print(
                        "WARNING: Duplicate keys in second dict is removed in merge_dicts_parallel")
            merged_dict = {**dict_a_i, **dict_b_i}
            merged_dicts.append(merged_dict)
        return merged_dicts

    @staticmethod
    def _format_date(date: datetime) -> str:
        # if not instance of datetime, parse date
        if not isinstance(date, datetime):
            date = parse_date(date)
        return date.strftime("%d/%m/%Y")


class HeaderSubheaderTable(MetaTable):

    def __init__(self, title: str) -> None:
        super().__init__(title)

    def generate_data_rows(self, header_id: int, subheader_id: int, start_date: str, end_date: str) -> tuple[List[Dict], List[Dict]]:
        """
        Generate data rows for a given header and subheader
        """
        input_args = self._generate_input_args(
            header_id, subheader_id, start_date, end_date)

        data_rows = self.data_rows(**input_args)

        # add part rows
        if self.part_display_mode == "column":
            data_rows = self.merge_dicts_parallel(
                self.generate_part_columns(**input_args), data_rows)
        elif self.part_display_mode == "row":
            data_rows.extend(self.generate_part_rows(**input_args))

        # generate speical rows
        total_rows = self.generate_total_rows(data_rows)

        cumulative = self.generate_cumulative(
            header_id, subheader_id, start_date, end_date)

        # format numeric columns
        for row in data_rows:
            for column in self.numeric_columns:
                try:
                    if column in row:
                        row[column] = self._format_indian_currency(
                            (row[column]))
                except:
                    print(
                        f"Error in formatting column {column} in row {row} to Indian Currency")

        return data_rows, total_rows, cumulative

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


class HeaderTable(MetaTable):
    def __init__(self, title: str) -> None:
        super().__init__(title)

    def generate_data_rows(self, header_id: int, subheader_ids: int, start_date: str, end_date: str) -> tuple[List[Dict], List[Dict]]:
        """
        Generate data rows for a given header and subheader
        """

        data_rows = []

        for subheader_id in subheader_ids:
            input_args = self._generate_input_args(
                header_id, subheader_id, start_date, end_date)
            register_data = self.data_rows(**input_args)

            # pop "party_name" if header enetity is party and vice versa
            if self.header_entity is Party:
                for register in register_data:
                    if "party_name" in register:
                        register.pop("party_name")
            elif self.header_entity is Supplier:
                for register in register_data:
                    if "supplier_name" in register:
                        register.pop("supplier_name")

            # add part rows
            if self.part_display_mode == "column":
                data_rows = self.merge_dicts_parallel(
                    self.generate_part_columns(**input_args), data_rows)
            elif self.part_display_mode == "row":
                data_rows.extend(self.generate_part_rows(**input_args))

            data_rows.extend(register_data)

        # generate speical rows
        total_rows = self.generate_total_rows(data_rows)

        # format numeric columns
        for row in data_rows:
            for column in self.numeric_columns:
                try:
                    if column in row:
                        row[column] = self._format_indian_currency(
                            (row[column]))
                except:
                    print(
                        f"Error in formatting column {column} in row {row} to Indian Currency")

        # Empty cumulative
        cumulative = {}

        return data_rows, total_rows, cumulative
