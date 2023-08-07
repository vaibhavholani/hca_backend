from typing import Dict, Union
from Individual import Supplier, Party
from Entities import RegisterEntry, MemoEntry
from Tests import TestKhataReport
from Reports import make_report
from Exceptions import DataError


def check_status_and_return_class(status: Dict) -> Union[Supplier, Party, RegisterEntry, MemoEntry]:
    if status["status"] == "okay":
        return status["class"]
    else:
        raise DataError(status)

# Function to find differences between two dictionaries
def find_differences(dict1, dict2, parent_key=""):
    diff = {}
    for key in dict1:
        if key not in dict2:
            diff[parent_key + key] = dict1[key]
        elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            nested_diff = find_differences(
                dict1[key], dict2[key], parent_key + key + ".")
            diff.update(nested_diff)
        elif dict1[key] != dict2[key]:
            diff[parent_key + key] = dict1[key]
    return diff

try : 
    del_supplier = False
    del_party = False
    del_register_entry = False
    del_part_memo = False
    del_full_memo = False

    # TODO: Add try except and check deletion
    test_supplier_input = {"name": "test_supplier4343",
                        "address": "test_address"}


    test_party_input = {"name": "test_party4333",
                        "address": "test_address"}

    # Create a supplier and party instance
    test_supplier = check_status_and_return_class(
        Supplier.insert(test_supplier_input, get_cls=True))
    del_supplier = True

    test_party = check_status_and_return_class(
        Party.insert(test_party_input, get_cls=True))
    del_party = True

    # Find the supplier and party id
    test_supplier_id = test_supplier.get_id()
    test_party_id = test_party.get_id()
    bill_amount = 5000

    bill_input = {"bill_number": "142345",
                "amount": bill_amount,
                "supplier_id": test_supplier_id,
                "party_id": test_party_id,
                "register_date": "2023-06-19"}

    # Create a Register Entry
    register_entry = check_status_and_return_class(
        RegisterEntry.insert(bill_input, get_cls=True))
    del_register_entry = True

    # Create Khata Report
    og_report = make_report("khata_report", [test_supplier_id], [
                            test_party_id], "2023-06-19", "2023-06-19")

    # Want to create a khata report here and check the output
    report = TestKhataReport("khata_report", [test_party_id], [
                            test_supplier_id], "2023-06-19", "2023-06-19")
    report_data = report.generate_table([register_entry], [])

    assert og_report == report_data

    # Find all the pending bills between supplier and party
    pending_bills = RegisterEntry.get_pending_bills(
        test_supplier_id, test_party_id)

    # # Get Total Pending Amount

    # # TODO: make this automated later
    total_pending_amount = bill_amount
    quarter_pending = total_pending_amount // 4
    # Create a part memo for half that amount

    # Create a Memo Entry
    part_input = {'memo_number': 49899,
                'register_date': '2023-08-04',
                'amount': quarter_pending,
                'party_id': test_party_id,
                'supplier_id': test_supplier_id,
                'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '234'}],
                'mode': 'Part'
                }

    part_memo = check_status_and_return_class(
        MemoEntry.insert(part_input, get_cls=True))
    
    part_memo_id = part_memo.get_id()

    del_part_memo = True

    gr_amount = 0
    deduction = 0
    part = quarter_pending

    amount = total_pending_amount - part - deduction - gr_amount

    full_input = {'memo_number': 994988,
                  'register_date': '2023-08-04',
                  'amount': amount,
                  'gr_amount': gr_amount,
                  'deduction': deduction,
                  'party_id': test_party_id,
                  'supplier_id': test_supplier_id,
                  'selected_bills': pending_bills,
                  'selected_part': [part_memo_id],
                  'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '34'}],
                  'mode': 'Full'}

    full_memo = check_status_and_return_class(MemoEntry.insert(full_input, get_cls=True))
    full_memo_id = full_memo.get_id()
    del_full_memo = True

    breakpoint()


    # check changes in register_entry
    # check change in part_payment and check memo_bills
    full_memo.delete()

    breakpoint()

    # check all the changes are not on uno
    part_memo.delete()

    breakpoint()
    register_entry.delete()
    test_supplier.delete()
    test_party.delete()

except Exception as e:
    if del_full_memo: 
        full_memo.delete()
    if del_part_memo:
        part_memo.delete()
    if del_register_entry:
        register_entry.delete()
    if del_supplier:
        test_supplier.delete()
    if del_party:
        test_party.delete()
    
