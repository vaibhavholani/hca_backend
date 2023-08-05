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
            nested_diff = find_differences(dict1[key], dict2[key], parent_key + key + ".")
            diff.update(nested_diff)
        elif dict1[key] != dict2[key]:
            diff[parent_key + key] = dict1[key]
    return diff


test_supplier_input = {"name": "test_supplier",
                       "address": "test_address"}


test_party_input = {"name": "test_party",
                    "address": "test_address"}

# Create a supplier and party instance
test_supplier = check_status_and_return_class(
    Supplier.insert(test_supplier_input, get_cls=True))
test_party = check_status_and_return_class(
    Party.insert(test_party_input, get_cls=True))

# Find the supplier and party id
test_supplier_id = test_supplier.get_id()
test_party_id = test_party.get_id()

bill_input = {"bill_number": "12345",
              "amount": "500",
              "supplier_id": test_supplier_id,
              "party_id": test_party_id,
              "register_date": "2023-06-19"}

# Create a Register Entry
register_entry = check_status_and_return_class(
    RegisterEntry.insert(bill_input, get_cls=True))

# Create Khata Report
og_report = make_report("khata_report", [test_supplier_id], [test_party_id], "2023-06-19", "2023-06-19")

# Want to create a khata report here and check the output
report = TestKhataReport("khata_report", [test_party_id], [test_supplier_id], "19/06/2023", "19/06/2023")
report_data = report.generate_table([register_entry], [])


find_differences(report_data, og_report)

# create a memo entry


# delete everything
register_entry.delete()
test_supplier.delete()
test_party.delete()
