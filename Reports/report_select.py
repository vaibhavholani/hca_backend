from typing import Dict
import json
from Reports import report
from Reports import payment_list_summary, grand_total_report, legacy_payment_list
from API_Database import efficiency
import sys
sys.path.append("../")


def make_report(data: Dict) -> Dict:

    supplier_ids = [element["id"]
                    for element in json.loads(data["suppliers"])]
    party_ids = [element["id"] for element in json.loads(data["parties"])]
    select = data['report']
    start_date = data['from']
    end_date = data['to']

    # if supplier_ids or party_ids are ints, convert them to lists
    if isinstance(supplier_ids, int):
        supplier_ids = [supplier_ids]
    if isinstance(party_ids, int):
        party_ids = [party_ids]

    options = ["khata_report", "supplier_register", "payment_list", "order_form",
               "payment_list_summary", "grand_total_list", "legacy_payment_list"]

    party_ids, supplier_ids = efficiency.smart_selection(
        supplier_ids, party_ids, start_date, end_date)

    if select in options[0:4]:
        report_obj = report.Report(
            select, party_ids, supplier_ids, start_date, end_date)
        report_data = report_obj.generate_table()
        return report_data

    elif select == options[3]:
        report_obj = payment_list_summary.execute(
            party_ids, supplier_ids, start_date, end_date)
    elif select == options[4]:
        report_obj = grand_total_report.execute(
            party_ids, supplier_ids, start_date, end_date)
    elif select == options[5]:
        report_obj = legacy_payment_list.execute(
            party_ids, supplier_ids, start_date, end_date)
    else:
        raise Exception("Invalid Option")
    return report_obj
