import sys
sys.path.append("../")
from API_Database import efficiency
from Reports import payment_list_summary, grand_total_report, legacy_payment_list
from Reports import report
import datetime


def make_report(select, supplier_ids, party_ids, start_date, end_date):

    # if supplier_ids or party_ids are ints, convert them to lists
    if isinstance(supplier_ids, int):
        supplier_ids = [supplier_ids]
    if isinstance(party_ids, int):
        party_ids = [party_ids]
    
    options = ["khata_report", "supplier_register", "payment_list", "payment_list_summary", "grand_total_list", "legacy_payment_list" ]
    start_date = (datetime.datetime.strptime(start_date, "%Y-%m-%d")).strftime('%d/%m/%Y')
    end_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d")).strftime('%d/%m/%Y')
    party_ids, supplier_ids = efficiency.smart_selection(supplier_ids, party_ids, start_date, end_date)

    if select in options[0:3]:
        report_obj = report.Report(select, party_ids, supplier_ids, start_date, end_date)
        report_data = report_obj.generate_table()
        return report_data
    
    elif select == options[3]:
        report_obj =  payment_list_summary.execute(party_ids, supplier_ids, start_date, end_date)
    elif select == options[4]:
        report_obj =  grand_total_report.execute(party_ids, supplier_ids, start_date, end_date)
    elif select == options[5]:
        report_obj =  legacy_payment_list.execute(party_ids, supplier_ids, start_date, end_date)
    else:
        raise Exception("Invalid Option")
    return report_obj