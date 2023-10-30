from typing import Dict, Union, List
from Individual import Supplier, Party
from Entities import RegisterEntry, MemoEntry, OrderForm, Item, ItemEntry
from Tests import TestKhataReport
from Reports import make_report
from Tests import check_status_and_return_class, cleanup


# Create Khata Report

def report_formatter(report, suppliers, parties, from_date, to_date, all=False):
    # make every element a suppliers intto a dict like {"id": suppliers[i]}
    if isinstance(suppliers, list):
        suppliers = [{"id": supplier} for supplier in suppliers]
    if isinstance(parties, list):
        parties = [{"id": party} for party in parties]
    data = {
        "suppliers": suppliers,
        "parties": parties,
        "report": report,
        "from": from_date,
        "to": to_date,
        "all": all
    }
    return data

if __name__ == "__main__":  
    og_report = make_report(report_formatter("khata_report", [], [], "2022-06-19", "2023-06-19", True))
    print(og_report)

