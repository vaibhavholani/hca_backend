import json
import signal
import sys
from typing import Dict, Union, List
from contextlib import contextmanager
from datetime import datetime, timedelta
from Individual import Supplier, Party
from Entities import RegisterEntry, MemoEntry
from Tests import TestKhataReport
from Reports import make_report
from Tests import check_status_and_return_class, cleanup, print_dict_diff
TEST_SUPPLIER1_NAME = 'test_supplier1_special2'
TEST_SUPPLIER2_NAME = 'test_supplier2_special'
TEST_PARTY1_NAME = 'test_party1_special'
TEST_PARTY2_NAME = 'test_party2_special'
BILL_NUMBERS = ['1001', '1002', '1003', '1004']
BILL_AMOUNT = 1000
PART_AMOUNT = 250
MEMO_NUMBERS = [102301, 10042, 100673, 100214]
TODAY = datetime.now().date()
BILL_DATE = (TODAY - timedelta(days=180)).strftime('%Y-%m-%d')
MEMO_DATE = (TODAY - timedelta(days=179)).strftime('%Y-%m-%d')
DAYS_SINCE_BILL = (TODAY - datetime.strptime(BILL_DATE, '%Y-%m-%d').date()).days

def format_date_for_display(date_str):
    """Convert YYYY-MM-DD to DD/MM/YYYY format"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d/%m/%Y')

@contextmanager
def cleanup_context(cleanup_list):
    """Context manager that yields a cleanup_list and ensures cleanup is performed on exit."""
    try:
        yield cleanup_list
    finally:
        cleanup(cleanup_list)

def signal_handler(signum, frame):
    """Handles OS signals by printing an interrupt message and exiting the process."""
    print('Received interrupt, cleaning up...')
    sys.exit(0)

def run_test():
    """Executes tests for report special rows, including creating entities, generating reports, and performing cleanup."""
    cleanup_list = []
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    with cleanup_context(cleanup_list):
        try:
            supplier1_input = {'name': TEST_SUPPLIER1_NAME, 'address': 'test_address1', 'phone_number': '1234567890'}
            supplier2_input = {'name': TEST_SUPPLIER2_NAME, 'address': 'test_address2', 'phone_number': '9876543210'}
            supplier1 = check_status_and_return_class(Supplier.insert(supplier1_input, get_cls=True))
            supplier2 = check_status_and_return_class(Supplier.insert(supplier2_input, get_cls=True))
            cleanup_list.extend([supplier1, supplier2])
            party1_input = {'name': TEST_PARTY1_NAME, 'address': 'test_address1', 'phone_number': '9350544808'}
            party2_input = {'name': TEST_PARTY2_NAME, 'address': 'test_address2', 'phone_number': '9350544808'}
            party1 = check_status_and_return_class(Party.insert(party1_input, get_cls=True))
            party2 = check_status_and_return_class(Party.insert(party2_input, get_cls=True))
            cleanup_list.extend([party1, party2])
            register_entries = []
            bill_inputs = [{'bill_number': BILL_NUMBERS[0], 'amount': BILL_AMOUNT, 'supplier_id': supplier1.get_id(), 'party_id': party1.get_id(), 'register_date': BILL_DATE}, {'bill_number': BILL_NUMBERS[1], 'amount': BILL_AMOUNT, 'supplier_id': supplier1.get_id(), 'party_id': party2.get_id(), 'register_date': BILL_DATE}, {'bill_number': BILL_NUMBERS[2], 'amount': BILL_AMOUNT, 'supplier_id': supplier2.get_id(), 'party_id': party1.get_id(), 'register_date': BILL_DATE}, {'bill_number': BILL_NUMBERS[3], 'amount': BILL_AMOUNT, 'supplier_id': supplier2.get_id(), 'party_id': party2.get_id(), 'register_date': BILL_DATE}]
            for bill_input in bill_inputs:
                register_entry = check_status_and_return_class(RegisterEntry.insert(bill_input, get_cls=True))
                register_entries.append(register_entry)
                cleanup_list.append(register_entry)
            memo_entries = []
            memo_inputs = [{'memo_number': MEMO_NUMBERS[0], 'register_date': MEMO_DATE, 'amount': PART_AMOUNT, 'party_id': party1.get_id(), 'supplier_id': supplier1.get_id(), 'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '1001'}], 'mode': 'Part'}, {'memo_number': MEMO_NUMBERS[1], 'register_date': MEMO_DATE, 'amount': PART_AMOUNT, 'party_id': party2.get_id(), 'supplier_id': supplier1.get_id(), 'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '1002'}], 'mode': 'Part'}, {'memo_number': MEMO_NUMBERS[2], 'register_date': MEMO_DATE, 'amount': PART_AMOUNT, 'party_id': party1.get_id(), 'supplier_id': supplier2.get_id(), 'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '1003'}], 'mode': 'Part'}, {'memo_number': MEMO_NUMBERS[3], 'register_date': MEMO_DATE, 'amount': PART_AMOUNT, 'party_id': party2.get_id(), 'supplier_id': supplier2.get_id(), 'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '1004'}], 'mode': 'Part'}]
            for memo_input in memo_inputs:
                memo_entry = check_status_and_return_class(MemoEntry.insert(memo_input, get_cls=True))
                memo_entries.append(memo_entry)
                cleanup_list.append(memo_entry)
            khata_report = make_report({'report': 'khata_report', 'suppliers': json.dumps([{'id': supplier1.get_id()}, {'id': supplier2.get_id()}]), 'parties': json.dumps([{'id': party1.get_id()}, {'id': party2.get_id()}]), 'from': BILL_DATE, 'to': MEMO_DATE})
            report_data = {'title': 'Khata Report', 'from': BILL_DATE, 'to': MEMO_DATE, 'headings': [{'title': f'Party Name: {TEST_PARTY1_NAME}', 'subheadings': [{'title': f'Supplier Name: {TEST_SUPPLIER1_NAME}', 'dataRows': [{'bill_no': int(BILL_NUMBERS[0]), 'bill_date': format_date_for_display(BILL_DATE), 'bill_amt': f'{BILL_AMOUNT:,}', 'bill_status': 'N', 'memo_no': '', 'memo_amt': '', 'memo_date': '', 'chk_amt': '', 'memo_type': ''}, {'memo_no': MEMO_NUMBERS[0], 'memo_date': format_date_for_display(MEMO_DATE), 'chk_amt': f'{PART_AMOUNT}', 'memo_amt': f'{PART_AMOUNT}', 'memo_type': 'PR'}], 'specialRows': [{'name': 'Subtotal', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Subtotal', 'value': f'{PART_AMOUNT}', 'column': 'memo_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': '0.00% GR (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': '0.00% Less (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Total Paid (=)', 'value': f'{PART_AMOUNT}', 'column': 'memo_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Paid+GR (-)', 'value': f'- {PART_AMOUNT}', 'column': 'bill_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Pending (=)', 'value': f'{BILL_AMOUNT - PART_AMOUNT}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT - PART_AMOUNT, 'beforeData': False}], 'displayOnIndex': True}, {'title': f'Supplier Name: {TEST_SUPPLIER2_NAME}', 'dataRows': [{'bill_no': int(BILL_NUMBERS[2]), 'bill_date': format_date_for_display(BILL_DATE), 'bill_amt': f'{BILL_AMOUNT:,}', 'bill_status': 'N', 'memo_no': '', 'memo_amt': '', 'memo_date': '', 'chk_amt': '', 'memo_type': ''}, {'memo_no': MEMO_NUMBERS[2], 'memo_date': format_date_for_display(MEMO_DATE), 'chk_amt': f'{PART_AMOUNT}', 'memo_amt': f'{PART_AMOUNT}', 'memo_type': 'PR'}], 'specialRows': [{'name': 'Subtotal', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Subtotal', 'value': f'{PART_AMOUNT}', 'column': 'memo_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': '0.00% GR (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': '0.00% Less (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Total Paid (=)', 'value': f'{PART_AMOUNT}', 'column': 'memo_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Paid+GR (-)', 'value': f'- {PART_AMOUNT}', 'column': 'bill_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Pending (=)', 'value': f'{BILL_AMOUNT - PART_AMOUNT}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT - PART_AMOUNT, 'beforeData': False}], 'displayOnIndex': True}]}, {'title': f'Party Name: {TEST_PARTY2_NAME}', 'subheadings': [{'title': f'Supplier Name: {TEST_SUPPLIER1_NAME}', 'dataRows': [{'bill_no': int(BILL_NUMBERS[1]), 'bill_date': format_date_for_display(BILL_DATE), 'bill_amt': f'{BILL_AMOUNT:,}', 'bill_status': 'N', 'memo_no': '', 'memo_amt': '', 'memo_date': '', 'chk_amt': '', 'memo_type': ''}, {'memo_no': MEMO_NUMBERS[1], 'memo_date': format_date_for_display(MEMO_DATE), 'chk_amt': f'{PART_AMOUNT}', 'memo_amt': f'{PART_AMOUNT}', 'memo_type': 'PR'}], 'specialRows': [{'name': 'Subtotal', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Subtotal', 'value': f'{PART_AMOUNT}', 'column': 'memo_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': '0.00% GR (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': '0.00% Less (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Total Paid (=)', 'value': f'{PART_AMOUNT}', 'column': 'memo_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Paid+GR (-)', 'value': f'- {PART_AMOUNT}', 'column': 'bill_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Pending (=)', 'value': f'{BILL_AMOUNT - PART_AMOUNT}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT - PART_AMOUNT, 'beforeData': False}], 'displayOnIndex': True}, {'title': f'Supplier Name: {TEST_SUPPLIER2_NAME}', 'dataRows': [{'bill_no': int(BILL_NUMBERS[3]), 'bill_date': format_date_for_display(BILL_DATE), 'bill_amt': f'{BILL_AMOUNT:,}', 'bill_status': 'N', 'memo_no': '', 'memo_amt': '', 'memo_date': '', 'chk_amt': '', 'memo_type': ''}, {'memo_no': MEMO_NUMBERS[3], 'memo_date': format_date_for_display(MEMO_DATE), 'chk_amt': f'{PART_AMOUNT}', 'memo_amt': f'{PART_AMOUNT}', 'memo_type': 'PR'}], 'specialRows': [{'name': 'Subtotal', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Subtotal', 'value': f'{PART_AMOUNT}', 'column': 'memo_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': '0.00% GR (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': '0.00% Less (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Total Paid (=)', 'value': f'{PART_AMOUNT}', 'column': 'memo_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Paid+GR (-)', 'value': f'- {PART_AMOUNT}', 'column': 'bill_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Pending (=)', 'value': f'{BILL_AMOUNT - PART_AMOUNT}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT - PART_AMOUNT, 'beforeData': False}], 'displayOnIndex': True}]}]}
            try:
                assert khata_report == report_data
            except AssertionError:
                print('\nDifference in khata report:')
                print_dict_diff(khata_report, report_data)
                raise
            payment_list = make_report({'report': 'payment_list', 'suppliers': json.dumps([{'id': supplier1.get_id()}, {'id': supplier2.get_id()}]), 'parties': json.dumps([{'id': party1.get_id()}, {'id': party2.get_id()}]), 'from': BILL_DATE, 'to': MEMO_DATE})
            payment_reference = {'title': 'Payment List', 'from': BILL_DATE, 'to': MEMO_DATE, 'headings': [{'title': f'Party Name: {TEST_PARTY1_NAME}', 'subheadings': [{'title': f'Supplier Name: {TEST_SUPPLIER1_NAME}', 'dataRows': [{'part_no': MEMO_NUMBERS[0], 'part_date': format_date_for_display(MEMO_DATE), 'part_amt': f'{PART_AMOUNT}', 'bill_no': int(BILL_NUMBERS[0]), 'bill_amt': f'{BILL_AMOUNT:,}', 'bill_date': format_date_for_display(BILL_DATE), 'pending_amt': BILL_AMOUNT, 'days': DAYS_SINCE_BILL, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': f'{PART_AMOUNT}', 'column': 'part_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Part (-)', 'value': f'- {PART_AMOUNT}', 'column': 'bill_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Pending (=)', 'value': f'{BILL_AMOUNT - PART_AMOUNT}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT - PART_AMOUNT, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': f'{BILL_AMOUNT - PART_AMOUNT}'}}, {'title': f'Supplier Name: {TEST_SUPPLIER2_NAME}', 'dataRows': [{'part_no': MEMO_NUMBERS[2], 'part_date': format_date_for_display(MEMO_DATE), 'part_amt': f'{PART_AMOUNT}', 'bill_no': int(BILL_NUMBERS[2]), 'bill_amt': f'{BILL_AMOUNT:,}', 'bill_date': format_date_for_display(BILL_DATE), 'pending_amt': BILL_AMOUNT, 'days': DAYS_SINCE_BILL, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': f'{PART_AMOUNT}', 'column': 'part_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Part (-)', 'value': f'- {PART_AMOUNT}', 'column': 'bill_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Pending (=)', 'value': f'{BILL_AMOUNT - PART_AMOUNT}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT - PART_AMOUNT, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': f'{BILL_AMOUNT - PART_AMOUNT}'}}], 'cumulative': {'name': 'Total Pending', 'value': f'{2 * (BILL_AMOUNT - PART_AMOUNT):,}'}}, {'title': f'Party Name: {TEST_PARTY2_NAME}', 'subheadings': [{'title': f'Supplier Name: {TEST_SUPPLIER1_NAME}', 'dataRows': [{'part_no': MEMO_NUMBERS[1], 'part_date': format_date_for_display(MEMO_DATE), 'part_amt': f'{PART_AMOUNT}', 'bill_no': int(BILL_NUMBERS[1]), 'bill_amt': f'{BILL_AMOUNT:,}', 'bill_date': format_date_for_display(BILL_DATE), 'pending_amt': BILL_AMOUNT, 'days': DAYS_SINCE_BILL, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': f'{PART_AMOUNT}', 'column': 'part_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Part (-)', 'value': f'- {PART_AMOUNT}', 'column': 'bill_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Pending (=)', 'value': f'{BILL_AMOUNT - PART_AMOUNT}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT - PART_AMOUNT, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': f'{BILL_AMOUNT - PART_AMOUNT}'}}, {'title': f'Supplier Name: {TEST_SUPPLIER2_NAME}', 'dataRows': [{'part_no': MEMO_NUMBERS[3], 'part_date': format_date_for_display(MEMO_DATE), 'part_amt': f'{PART_AMOUNT}', 'bill_no': int(BILL_NUMBERS[3]), 'bill_amt': f'{BILL_AMOUNT:,}', 'bill_date': format_date_for_display(BILL_DATE), 'pending_amt': BILL_AMOUNT, 'days': DAYS_SINCE_BILL, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': f'{PART_AMOUNT}', 'column': 'part_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': f'{BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT, 'beforeData': False}, {'name': 'Part (-)', 'value': f'- {PART_AMOUNT}', 'column': 'bill_amt', 'numeric': PART_AMOUNT, 'beforeData': False}, {'name': 'Pending (=)', 'value': f'{BILL_AMOUNT - PART_AMOUNT}', 'column': 'bill_amt', 'numeric': BILL_AMOUNT - PART_AMOUNT, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': f'{BILL_AMOUNT - PART_AMOUNT}'}}], 'cumulative': {'name': 'Total Pending', 'value': f'{2 * (BILL_AMOUNT - PART_AMOUNT):,}'}}]}
            try:
                assert payment_list == payment_reference
            except AssertionError:
                print('\nDifference in payment list report:')
                print_dict_diff(payment_list, payment_reference)
                raise
            supplier_register = make_report({'report': 'supplier_register', 'suppliers': json.dumps([{'id': supplier1.get_id()}, {'id': supplier2.get_id()}]), 'parties': json.dumps([{'id': party1.get_id()}, {'id': party2.get_id()}]), 'from': BILL_DATE, 'to': MEMO_DATE})
            supplier_reference = {'title': 'Supplier Register', 'from': BILL_DATE, 'to': MEMO_DATE, 'headings': [{'title': f'Supplier Name: {TEST_SUPPLIER1_NAME}', 'subheadings': [{'title': '', 'dataRows': [{'bill_date': format_date_for_display(BILL_DATE), 'party_name': TEST_PARTY1_NAME, 'bill_no': int(BILL_NUMBERS[0]), 'bill_amt': f'{BILL_AMOUNT:,}', 'pending_amt': f'{BILL_AMOUNT:,}', 'status': 'N'}, {'bill_date': format_date_for_display(BILL_DATE), 'party_name': TEST_PARTY2_NAME, 'bill_no': int(BILL_NUMBERS[1]), 'bill_amt': f'{BILL_AMOUNT:,}', 'pending_amt': f'{BILL_AMOUNT:,}', 'status': 'N'}], 'specialRows': [{'name': 'Total (=) ', 'value': f'{2 * BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': 2 * BILL_AMOUNT, 'beforeData': False}, {'name': 'Pending (=) ', 'value': f'{2 * BILL_AMOUNT:,}', 'column': 'pending_amt', 'numeric': 2 * BILL_AMOUNT, 'beforeData': False}], 'displayOnIndex': False}]}, {'title': f'Supplier Name: {TEST_SUPPLIER2_NAME}', 'subheadings': [{'title': '', 'dataRows': [{'bill_date': format_date_for_display(BILL_DATE), 'party_name': TEST_PARTY1_NAME, 'bill_no': int(BILL_NUMBERS[2]), 'bill_amt': f'{BILL_AMOUNT:,}', 'pending_amt': f'{BILL_AMOUNT:,}', 'status': 'N'}, {'bill_date': format_date_for_display(BILL_DATE), 'party_name': TEST_PARTY2_NAME, 'bill_no': int(BILL_NUMBERS[3]), 'bill_amt': f'{BILL_AMOUNT:,}', 'pending_amt': f'{BILL_AMOUNT:,}', 'status': 'N'}], 'specialRows': [{'name': 'Total (=) ', 'value': f'{2 * BILL_AMOUNT:,}', 'column': 'bill_amt', 'numeric': 2 * BILL_AMOUNT, 'beforeData': False}, {'name': 'Pending (=) ', 'value': f'{2 * BILL_AMOUNT:,}', 'column': 'pending_amt', 'numeric': 2 * BILL_AMOUNT, 'beforeData': False}], 'displayOnIndex': False}]}]}
            try:
                assert supplier_register == supplier_reference
            except AssertionError:
                print('\nDifference in supplier register report:')
                print_dict_diff(supplier_register, supplier_reference)
                raise
            print('All Tests Passed')
        except Exception as e:
            cleanup(cleanup_list)
            raise e
if __name__ == '__main__':
    run_test()