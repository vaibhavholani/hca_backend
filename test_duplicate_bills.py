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
from Exceptions.custom_exception import DataError


@contextmanager
def cleanup_context(cleanup_list):
    try:
        yield cleanup_list
    finally:
        cleanup(cleanup_list)


def signal_handler(signum, frame):
    print("Received interrupt, cleaning up...")
    sys.exit(0)


def run_duplicate_bills_test():
    cleanup_list = []

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    with cleanup_context(cleanup_list):
        try:
            # Create test supplier and party
            test_supplier_input = {"name": "test_supplier_dup",
                                   "address": "test_address",
                                   "phone_number": "9350544808"}

            test_party_input = {"name": "test_party_dup",
                                "address": "test_address",
                                "phone_number": "+1 647 901 4404"}

            # Create supplier instance
            test_supplier = check_status_and_return_class(
                Supplier.insert(test_supplier_input, get_cls=True))
            cleanup_list.append(test_supplier)
            test_supplier_id = test_supplier.get_id()

            # Create party instance
            test_party = check_status_and_return_class(
                Party.insert(test_party_input, get_cls=True))
            cleanup_list.append(test_party)
            test_party_id = test_party.get_id()

            bill_number = "123456"
            bill_amount = 5000

            # Test Case 1: Create first register entry
            register_date_1 = "2023-01-15"
            bill_input_1 = {
                "bill_number": bill_number,
                "amount": bill_amount,
                "supplier_id": test_supplier_id,
                "party_id": test_party_id,
                "register_date": register_date_1
            }

            register_entry_1 = check_status_and_return_class(
                RegisterEntry.insert(bill_input_1, get_cls=True))
            cleanup_list.append(register_entry_1)

            # Test Case 2: Try exact duplicate (should fail)
            try:
                RegisterEntry.insert(bill_input_1)
                assert False, "Should have raised DataError for exact duplicate"
            except DataError:
                pass  # Expected behavior

            # Test Case 3: Try duplicate less than 6 months apart (should fail)
            register_date_2 = "2023-03-15"  # 2 months later
            bill_input_2 = {
                "bill_number": bill_number,
                "amount": bill_amount + 1000,
                "supplier_id": test_supplier_id,
                "party_id": test_party_id,
                "register_date": register_date_2
            }

            try:
                RegisterEntry.insert(bill_input_2)
                assert False, "Should have raised DataError for bills less than 6 months apart"
            except DataError:
                pass  # Expected behavior

            # Test Case 4: Try duplicate exactly 6 months apart (should succeed)
            register_date_3 = "2023-07-15"  # 6 months later
            bill_input_3 = {
                "bill_number": bill_number,
                "amount": bill_amount + 2000,
                "supplier_id": test_supplier_id,
                "party_id": test_party_id,
                "register_date": register_date_3
            }

            register_entry_3 = check_status_and_return_class(
                RegisterEntry.insert(bill_input_3, get_cls=True))
            cleanup_list.append(register_entry_3)

            # Test Case 5: Try duplicate more than 6 months apart (should succeed)
            register_date_4 = "2024-01-15"  # 12 months after first entry
            bill_input_4 = {
                "bill_number": bill_number,
                "amount": bill_amount + 3000,
                "supplier_id": test_supplier_id,
                "party_id": test_party_id,
                "register_date": register_date_4
            }

            register_entry_4 = check_status_and_return_class(
                RegisterEntry.insert(bill_input_4, get_cls=True))
            cleanup_list.append(register_entry_4)

            # Test Case 6: Verify all valid entries can be retrieved correctly
            retrieved_entry_1 = RegisterEntry.retrieve(
                test_supplier_id, test_party_id, bill_number, register_date_1)
            retrieved_entry_3 = RegisterEntry.retrieve(
                test_supplier_id, test_party_id, bill_number, register_date_3)
            retrieved_entry_4 = RegisterEntry.retrieve(
                test_supplier_id, test_party_id, bill_number, register_date_4)

            assert retrieved_entry_1.amount == bill_amount
            assert retrieved_entry_3.amount == bill_amount + 2000
            assert retrieved_entry_4.amount == bill_amount + 3000

            # Test Case 7: Create khata report and verify initial state
            og_report = make_report({
                "report": "khata_report",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": register_date_1,
                "to": register_date_4
            })

            report = TestKhataReport("khata_report",
                                     [test_party_id],
                                     [test_supplier_id],
                                     register_date_1,
                                     register_date_4)
            report_data = report.generate_table(
                [retrieved_entry_1, retrieved_entry_3, retrieved_entry_4], [])

            try:
                assert og_report == report_data
            except AssertionError:
                print("\nDifference in initial khata report:")
                print_dict_diff(og_report, report_data)
                raise

            # Test Case 8: Create part memo
            memo_number = 551766
            memo_amount = 2000
            memo_input = {
                'memo_number': memo_number,
                'register_date': '2024-02-15',
                'amount': memo_amount,
                'party_id': test_party_id,
                'supplier_id': test_supplier_id,
                'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '234'}],
                'mode': 'Part'
            }

            part_memo = check_status_and_return_class(
                MemoEntry.insert(memo_input, get_cls=True))
            cleanup_list.append(part_memo)

            part_memo = MemoEntry.retrieve(
                test_supplier_id, test_party_id, memo_number)
            part_memo_id = part_memo.get_id()

            # Test Case 9: Verify khata report shows part memo
            og_report = make_report({
                "report": "khata_report",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": register_date_1,
                "to": register_date_4
            })

            report = TestKhataReport("khata_report",
                                     [test_party_id],
                                     [test_supplier_id],
                                     register_date_1,
                                     register_date_4)
            report_data = report.generate_table(
                [retrieved_entry_1, retrieved_entry_3, retrieved_entry_4], [part_memo])

            try:
                assert og_report == report_data
            except AssertionError:
                print("\nDifference in part memo khata report:")
                print_dict_diff(og_report, report_data)
                raise

            # Test Case 10: Create full memo using part memo
            pending_bills = RegisterEntry.get_pending_bills(
                test_supplier_id, test_party_id)
            gr_amount = 300
            deduction = 300

            # Calculate total amount for all pending bills
            total_pending = sum(bill["amount"] for bill in pending_bills)
            remaining_amount = total_pending - memo_amount - gr_amount - deduction

            full_memo_input = {
                'memo_number': 3970334,
                'register_date': '2024-02-15',
                'amount': remaining_amount,
                'gr_amount': gr_amount,
                'deduction': deduction,
                'party_id': test_party_id,
                'supplier_id': test_supplier_id,
                'selected_bills': pending_bills,
                'selected_part': [part_memo_id],
                'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '34'}],
                'mode': 'Full'
            }

            full_memo = check_status_and_return_class(
                MemoEntry.insert(full_memo_input, get_cls=True))
            cleanup_list.append(full_memo)

            full_memo = MemoEntry.retrieve(
                test_supplier_id, test_party_id, 3970334)
            
            # Get updated register entries
            retrieved_entry_1 = RegisterEntry.retrieve(
                test_supplier_id, test_party_id, bill_number, register_date_1)
            
            retrieved_entry_3 = RegisterEntry.retrieve(
                test_supplier_id, test_party_id, bill_number, register_date_3)
            
            retrieved_entry_4 = RegisterEntry.retrieve(
                test_supplier_id, test_party_id, bill_number, register_date_4)


            # Test Case 11: Verify final khata report
            og_report = make_report({
                "report": "khata_report",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": register_date_1,
                "to": register_date_4
            })


            report = TestKhataReport("khata_report",
                                     [test_party_id],
                                     [test_supplier_id],
                                     register_date_1,
                                     register_date_4)
            report_data = report.generate_table(
                [retrieved_entry_1, retrieved_entry_3, retrieved_entry_4], [full_memo])

            try:
                assert og_report == report_data
            except AssertionError:
                print("\nDifference in final khata report:")
                print_dict_diff(og_report, report_data)
                raise

            print("All Duplicate Bills Tests Passed")

            # cleanup
            cleanup(cleanup_list)

        except Exception as e:
            # Delete all the entries
            cleanup(cleanup_list)
            raise e


if __name__ == "__main__":
    run_duplicate_bills_test()
