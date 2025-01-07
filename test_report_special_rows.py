import json
import signal
import sys
from typing import Dict, Union, List
from contextlib import contextmanager
from Individual import Supplier, Party
from Entities import RegisterEntry, MemoEntry
from Tests import TestKhataReport
from Reports import make_report
from Tests import check_status_and_return_class, cleanup, print_dict_diff


@contextmanager
def cleanup_context(cleanup_list):
    try:
        yield cleanup_list
    finally:
        cleanup(cleanup_list)


def signal_handler(signum, frame):
    print("Received interrupt, cleaning up...")
    sys.exit(0)


def run_test():
    cleanup_list = []

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    with cleanup_context(cleanup_list):
        try:
            # Create suppliers
            supplier1_input = {
                "name": "test_supplier1_special2",
                "address": "test_address1",
                "phone_number": "1234567890"
            }
            supplier2_input = {
                "name": "test_supplier2_special",
                "address": "test_address2",
                "phone_number": "9876543210"
            }

            supplier1 = check_status_and_return_class(
                Supplier.insert(supplier1_input, get_cls=True))
            supplier2 = check_status_and_return_class(
                Supplier.insert(supplier2_input, get_cls=True))
            cleanup_list.extend([supplier1, supplier2])

            # Create parties
            party1_input = {
                "name": "test_party1_special",
                "address": "test_address1",
                "phone_number": "9350544808"
            }
            party2_input = {
                "name": "test_party2_special",
                "address": "test_address2",
                "phone_number": "9350544808"
            }

            party1 = check_status_and_return_class(
                Party.insert(party1_input, get_cls=True))
            party2 = check_status_and_return_class(
                Party.insert(party2_input, get_cls=True))
            cleanup_list.extend([party1, party2])

            # Create register entries (1000 each)
            register_entries = []
            bill_inputs = [
                {"bill_number": "1001", "amount": 1000, "supplier_id": supplier1.get_id(
                ), "party_id": party1.get_id(), "register_date": "2024-01-01"},
                {"bill_number": "1002", "amount": 1000, "supplier_id": supplier1.get_id(
                ), "party_id": party2.get_id(), "register_date": "2024-01-01"},
                {"bill_number": "1003", "amount": 1000, "supplier_id": supplier2.get_id(
                ), "party_id": party1.get_id(), "register_date": "2024-01-01"},
                {"bill_number": "1004", "amount": 1000, "supplier_id": supplier2.get_id(
                ), "party_id": party2.get_id(), "register_date": "2024-01-01"}
            ]

            for bill_input in bill_inputs:
                register_entry = check_status_and_return_class(
                    RegisterEntry.insert(bill_input, get_cls=True))
                register_entries.append(register_entry)
                cleanup_list.append(register_entry)

            # Create part memo entries (250 each)
            memo_entries = []
            memo_inputs = [
                {
                    'memo_number': 102301,
                    'register_date': '2024-01-02',
                    'amount': 250,
                    'party_id': party1.get_id(),
                    'supplier_id': supplier1.get_id(),
                    'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '1001'}],
                    'mode': 'Part'
                },
                {
                    'memo_number': 10042,
                    'register_date': '2024-01-02',
                    'amount': 250,
                    'party_id': party2.get_id(),
                    'supplier_id': supplier1.get_id(),
                    'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '1002'}],
                    'mode': 'Part'
                },
                {
                    'memo_number': 100673,
                    'register_date': '2024-01-02',
                    'amount': 250,
                    'party_id': party1.get_id(),
                    'supplier_id': supplier2.get_id(),
                    'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '1003'}],
                    'mode': 'Part'
                },
                {
                    'memo_number': 100214,
                    'register_date': '2024-01-02',
                    'amount': 250,
                    'party_id': party2.get_id(),
                    'supplier_id': supplier2.get_id(),
                    'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '1004'}],
                    'mode': 'Part'
                }
            ]

            for memo_input in memo_inputs:
                memo_entry = check_status_and_return_class(
                    MemoEntry.insert(memo_input, get_cls=True))
                memo_entries.append(memo_entry)
                cleanup_list.append(memo_entry)

            # Generate and verify Khata Report
            khata_report = make_report({
                "report": "khata_report",
                "suppliers": json.dumps([{"id": supplier1.get_id()}, {"id": supplier2.get_id()}]),
                "parties": json.dumps([{"id": party1.get_id()}, {"id": party2.get_id()}]),
                "from": "2024-01-01",
                "to": "2024-01-02"
            })

              # Want to create a khata report here and check the output
            # report = TestKhataReport("khata_report", [party1.get_id(), party2.get_id()], [
            #     supplier1.get_id(), supplier2.get_id()], "2024-01-01", "2024-01-02")
            # report_data = report.generate_table(register_entries, memo_entries)

            report_data = {'title': 'Khata Report', 'from': '2024-01-01', 'to': '2024-01-02', 'headings': [{'title': 'Party Name: test_party1_special', 'subheadings': [{'title': 'Supplier Name: test_supplier1_special2', 'dataRows': [{'bill_no': 1001, 'bill_date': '01/01/2024', 'bill_amt': '1,000', 'bill_status': 'N', 'memo_no': '', 'memo_amt': '', 'memo_date': '', 'chk_amt': '', 'memo_type': ''}, {'memo_no': 102301, 'memo_date': '02/01/2024', 'chk_amt': '250', 'memo_amt': '250', 'memo_type': 'PR'}], 'specialRows': [{'name': 'Subtotal', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Subtotal', 'value': '250', 'column': 'memo_amt', 'numeric': 250, 'beforeData': False}, {'name': '0.00% GR (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': '0.00% Less (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Total Paid (=)', 'value': '250', 'column': 'memo_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Paid+GR (-)', 'value': '- 250', 'column': 'bill_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Pending (=)', 'value': '750', 'column': 'bill_amt', 'numeric': 750, 'beforeData': False}], 'displayOnIndex': True}, {'title': 'Supplier Name: test_supplier2_special', 'dataRows': [{'bill_no': 1003, 'bill_date': '01/01/2024', 'bill_amt': '1,000', 'bill_status': 'N', 'memo_no': '', 'memo_amt': '', 'memo_date': '', 'chk_amt': '', 'memo_type': ''}, {'memo_no': 100673, 'memo_date': '02/01/2024', 'chk_amt': '250', 'memo_amt': '250', 'memo_type': 'PR'}], 'specialRows': [{'name': 'Subtotal', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Subtotal', 'value': '250', 'column': 'memo_amt', 'numeric': 250, 'beforeData': False}, {'name': '0.00% GR (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': '0.00% Less (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Total Paid (=)', 'value': '250', 'column': 'memo_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Paid+GR (-)', 'value': '- 250', 'column': 'bill_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Pending (=)', 'value': '750', 'column': 'bill_amt', 'numeric': 750, 'beforeData': False}], 'displayOnIndex': True}]}, {'title': 'Party Name: test_party2_special', 'subheadings': [{'title': 'Supplier Name: test_supplier1_special2', 'dataRows': [{'bill_no': 1002, 'bill_date': '01/01/2024', 'bill_amt': '1,000', 'bill_status': 'N', 'memo_no': '', 'memo_amt': '', 'memo_date': '', 'chk_amt': '', 'memo_type': ''}, {'memo_no': 10042, 'memo_date': '02/01/2024', 'chk_amt': '250', 'memo_amt': '250', 'memo_type': 'PR'}], 'specialRows': [{'name': 'Subtotal', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Subtotal', 'value': '250', 'column': 'memo_amt', 'numeric': 250, 'beforeData': False}, {'name': '0.00% GR (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': '0.00% Less (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Total Paid (=)', 'value': '250', 'column': 'memo_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Paid+GR (-)', 'value': '- 250', 'column': 'bill_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Pending (=)', 'value': '750', 'column': 'bill_amt', 'numeric': 750, 'beforeData': False}], 'displayOnIndex': True}, {'title': 'Supplier Name: test_supplier2_special', 'dataRows': [{'bill_no': 1004, 'bill_date': '01/01/2024', 'bill_amt': '1,000', 'bill_status': 'N', 'memo_no': '', 'memo_amt': '', 'memo_date': '', 'chk_amt': '', 'memo_type': ''}, {'memo_no': 100214, 'memo_date': '02/01/2024', 'chk_amt': '250', 'memo_amt': '250', 'memo_type': 'PR'}], 'specialRows': [{'name': 'Subtotal', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Subtotal', 'value': '250', 'column': 'memo_amt', 'numeric': 250, 'beforeData': False}, {'name': '0.00% GR (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': '0.00% Less (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Total Paid (=)', 'value': '250', 'column': 'memo_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Paid+GR (-)', 'value': '- 250', 'column': 'bill_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Pending (=)', 'value': '750', 'column': 'bill_amt', 'numeric': 750, 'beforeData': False}], 'displayOnIndex': True}]}]}
            try:
                assert khata_report == report_data
            except AssertionError:
                print("\nDifference in khata report:")
                print_dict_diff(khata_report, report_data)
                raise

            # Generate and verify Payment List Report
            payment_list = make_report({
                "report": "payment_list",
                "suppliers": json.dumps([{"id": supplier1.get_id()}, {"id": supplier2.get_id()}]),
                "parties": json.dumps([{"id": party1.get_id()}, {"id": party2.get_id()}]),
                "from": "2024-01-01",
                "to": "2024-01-02"
            })
            payment_reference = {'title': 'Payment List', 'from': '2024-01-01', 'to': '2024-01-02', 'headings': [{'title': 'Party Name: test_party1_special', 'subheadings': [{'title': 'Supplier Name: test_supplier1_special2', 'dataRows': [{'part_no': 102301, 'part_date': '02/01/2024', 'part_amt': '250', 'bill_no': 1001, 'bill_amt': '1,000', 'bill_date': '01/01/2024', 'pending_amt': 1000, 'days': 372, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': '250', 'column': 'part_amt', 'numeric': 250, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Part (-)', 'value': '- 250', 'column': 'bill_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Pending (=)', 'value': '750', 'column': 'bill_amt', 'numeric': 750, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': '750'}}, {'title': 'Supplier Name: test_supplier2_special', 'dataRows': [{'part_no': 100673, 'part_date': '02/01/2024', 'part_amt': '250', 'bill_no': 1003, 'bill_amt': '1,000', 'bill_date': '01/01/2024', 'pending_amt': 1000, 'days': 372, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': '250', 'column': 'part_amt', 'numeric': 250, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Part (-)', 'value': '- 250', 'column': 'bill_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Pending (=)', 'value': '750', 'column': 'bill_amt', 'numeric': 750, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': '750'}}], 'cumulative': {'name': 'Total Pending', 'value': '1,500'}}, {'title': 'Party Name: test_party2_special', 'subheadings': [{'title': 'Supplier Name: test_supplier1_special2', 'dataRows': [{'part_no': 10042, 'part_date': '02/01/2024', 'part_amt': '250', 'bill_no': 1002, 'bill_amt': '1,000', 'bill_date': '01/01/2024', 'pending_amt': 1000, 'days': 372, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': '250', 'column': 'part_amt', 'numeric': 250, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Part (-)', 'value': '- 250', 'column': 'bill_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Pending (=)', 'value': '750', 'column': 'bill_amt', 'numeric': 750, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': '750'}}, {'title': 'Supplier Name: test_supplier2_special', 'dataRows': [{'part_no': 100214, 'part_date': '02/01/2024', 'part_amt': '250', 'bill_no': 1004, 'bill_amt': '1,000', 'bill_date': '01/01/2024', 'pending_amt': 1000, 'days': 372, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': '250', 'column': 'part_amt', 'numeric': 250, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': '1,000', 'column': 'bill_amt', 'numeric': 1000, 'beforeData': False}, {'name': 'Part (-)', 'value': '- 250', 'column': 'bill_amt', 'numeric': 250, 'beforeData': False}, {'name': 'Pending (=)', 'value': '750', 'column': 'bill_amt', 'numeric': 750, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': '750'}}], 'cumulative': {'name': 'Total Pending', 'value': '1,500'}}]}
            try:
                assert payment_list == payment_reference
            except AssertionError:
                print("\nDifference in payment list report:")
                print_dict_diff(payment_list, payment_reference)
                raise


            # Generate and verify Supplier Register Report
            supplier_register = make_report({
                "report": "supplier_register",
                "suppliers": json.dumps([{"id": supplier1.get_id()}, {"id": supplier2.get_id()}]),
                "parties": json.dumps([{"id": party1.get_id()}, {"id": party2.get_id()}]),
                "from": "2024-01-01",
                "to": "2024-01-02"
            })
            supplier_reference = {'title': 'Supplier Register', 'from': '2024-01-01', 'to': '2024-01-02', 'headings': [{'title': 'Supplier Name: test_supplier1_special2', 'subheadings': [{'title': '', 'dataRows': [{'bill_date': '01/01/2024', 'party_name': 'test_party1_special', 'bill_no': 1001, 'bill_amt': '1,000', 'pending_amt': '1,000', 'status': 'N'}, {'bill_date': '01/01/2024', 'party_name': 'test_party2_special', 'bill_no': 1002, 'bill_amt': '1,000', 'pending_amt': '1,000', 'status': 'N'}], 'specialRows': [{'name': 'Total (=) ', 'value': '2,000', 'column': 'bill_amt', 'numeric': 2000, 'beforeData': False}, {'name': 'Pending (=) ', 'value': '2,000', 'column': 'pending_amt', 'numeric': 2000, 'beforeData': False}], 'displayOnIndex': False}]}, {'title': 'Supplier Name: test_supplier2_special', 'subheadings': [{'title': '', 'dataRows': [{'bill_date': '01/01/2024', 'party_name': 'test_party1_special', 'bill_no': 1003, 'bill_amt': '1,000', 'pending_amt': '1,000', 'status': 'N'}, {'bill_date': '01/01/2024', 'party_name': 'test_party2_special', 'bill_no': 1004, 'bill_amt': '1,000', 'pending_amt': '1,000', 'status': 'N'}], 'specialRows': [{'name': 'Total (=) ', 'value': '2,000', 'column': 'bill_amt', 'numeric': 2000, 'beforeData': False}, {'name': 'Pending (=) ', 'value': '2,000', 'column': 'pending_amt', 'numeric': 2000, 'beforeData': False}], 'displayOnIndex': False}]}]}
            try:
                assert supplier_register == supplier_reference
            except AssertionError:
                print("\nDifference in supplier register report:")
                print_dict_diff(supplier_register, supplier_reference)
                raise


            print("All Tests Passed")

        except Exception as e:
            cleanup(cleanup_list)
            raise e


if __name__ == "__main__":
    run_test()
