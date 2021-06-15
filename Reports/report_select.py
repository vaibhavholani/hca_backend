import sys
sys.path.append("../")
from API_Database import efficiency
from Reports import khata_report, supplier_register_report, payment_list_report
from Reports import payment_list_summary, grand_total_report, legacy_payment_list
import datetime


def make_report(select, supplier_ids, party_ids, start_date, end_date):

    options = ["khata_report", "supplier_register", "payment_list", "payment_list_summary", "grand_total_list", "legacy_payment_list" ]
    start_date = (datetime.datetime.strptime(start_date, "%Y-%m-%d")).strftime('%d/%m/%Y')
    end_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d")).strftime('%d/%m/%Y')
    smart_ids = efficiency.smart_selection(supplier_ids, party_ids, start_date, end_date)
    print(smart_ids)
    if select == options[0]:
        khata_report.execute(smart_ids[0], smart_ids[1], start_date, end_date)
    elif select == options[1]:
        supplier_register_report.execute(smart_ids[0], smart_ids[1], start_date, end_date)
    elif select == options[2]:
        payment_list_report.execute(smart_ids[0], smart_ids[1], start_date, end_date)
    elif select == options[3]:
        payment_list_summary.execute(smart_ids[0], smart_ids[1], start_date, end_date)
    elif select == options[4]:
        grand_total_report.execute(smart_ids[0], smart_ids[1], start_date, end_date)
    else:
        legacy_payment_list.execute(smart_ids[0], smart_ids[1], start_date, end_date)