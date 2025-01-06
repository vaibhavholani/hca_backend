import json
import signal
import sys
from typing import Dict, Union, List
from contextlib import contextmanager
from Individual import Supplier, Party
from Entities import RegisterEntry, MemoEntry, OrderForm, Item, ItemEntry
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


def item_test(supplier_id: int, cleanup_list: List) -> Item:

    # Create an Item
    item_input = {"name": "Super Shiny Saree11",
                  "supplier_id": supplier_id}
    test_item = check_status_and_return_class(
        Item.insert(item_input, get_cls=True))
    cleanup_list.append(test_item)

    return test_item


def item_entry_test(register_entry_id: int, item_id: int) -> ItemEntry:

    # Create an Item Entry
    item_entry_input = {"register_entry_id": register_entry_id,
                        "item_id": item_id,
                        "quantity": 10,
                        "rate": 1000}

    test_item_entry = check_status_and_return_class(
        ItemEntry.insert(item_entry_input, get_cls=True))
    return test_item_entry


def run_basic_test():
    cleanup_list = []

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    with cleanup_context(cleanup_list):
        try:
            # create cleanup list
            cleanup_list = []

            test_supplier_input = {"name": "test_suppli42334",
                                   "address": "test_address",
                                   "phone_number": "9350544808"}

            test_party_input = {"name": "test_pa3r4343",
                                "address": "test_address",
                                "phone_number": "+1 647 901 4404"}

            # Create a supplier and party instance
            test_supplier = check_status_and_return_class(
                Supplier.insert(test_supplier_input, get_cls=True))

            # Add to cleanup
            cleanup_list.append(test_supplier)

            test_supplier_id = test_supplier.get_id()

            # Retrieve the supplier
            test_supplier = Supplier.retrieve(test_supplier_id)

            # Find the supplier and party id
            test_supplier_id = test_supplier.get_id()

            # Add Test Party
            test_party = check_status_and_return_class(
                Party.insert(test_party_input, get_cls=True))

            # Add to cleanup
            cleanup_list.append(test_party)

            test_party_id = test_party.get_id()

            # Retrieve the party
            test_party = Party.retrieve(test_party_id)

            # Create Item
            test_item = item_test(test_supplier_id, cleanup_list)
            test_item_id = test_item.get_id()

            # Create Order Form
            order_form_number = 1
            order_form_input = {
                "supplier_id": test_supplier_id,
                "party_id": test_party_id,
                "register_date": "2023-06-17",
                "order_form_number": order_form_number,
            }

            test_order_form = check_status_and_return_class(
                OrderForm.insert(order_form_input, get_cls=True))

            # Add to cleanup
            cleanup_list.append(test_order_form)

            # Retrieve the order form
            test_order_form = OrderForm.retrieve(
                test_supplier_id, test_party_id, order_form_number)

            # Create a Order Form Report
            og_report = make_report({
                "report": "order_form",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": "2023-06-16",
                "to": "2023-06-19"
            })

            # Checking Report for correct order form data
            order_form_data = og_report["headings"][0]["subheadings"][0]["dataRows"][0]
            try:
                assert int(order_form_data["order_no"]) == order_form_number
                assert order_form_data["order_date"] == "17/06/2023"
                assert order_form_data["supp_name"] == test_supplier_input["name"]
                assert order_form_data["party_name"] == test_party_input["name"]
                assert len(og_report["headings"][0]["subheadings"]) == 1
            except AssertionError:
                print("\nDifference in order form report:")
                print_dict_diff(
                    og_report, {"headings": [{"subheadings": [{"dataRows": [order_form_data]}]}]})
                raise

            # Set Bill basics
            bill_amount = 5000

            bill_input = {"bill_number": "123456",
                          "amount": bill_amount,
                          "supplier_id": test_supplier_id,
                          "party_id": test_party_id,
                          "register_date": "2023-06-19"}

            # Create a Register Entry
            register_entry = check_status_and_return_class(
                RegisterEntry.insert(bill_input, get_cls=True))

            # Add to cleanup
            cleanup_list.append(register_entry)

            # retrieve the register entry
            register_entry = RegisterEntry.retrieve(
                test_supplier_id, test_party_id, "123456", "2023-06-19")

            register_entry_id = register_entry.get_id()

            # Checking that there are no orderforms in the report
            og_report = make_report({
                "report": "order_form",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": "2023-06-16",
                "to": "2023-06-19"
            })
            try:
                assert len(og_report["headings"]) == 0
            except AssertionError:
                print("\nDifference in empty order form report:")
                print_dict_diff(og_report, {"headings": []})
                raise

            # Create Khata Report
            og_report = make_report({
                "report": "khata_report",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": "2023-06-19",
                "to": "2023-06-19"
            })

            # Want to create a khata report here and check the output
            report = TestKhataReport("khata_report", [test_party_id], [
                test_supplier_id], "2023-06-19", "2023-06-19")
            report_data = report.generate_table([register_entry], [])

            # Add Item and Item Entries asscoiated with register entry
            test_item_entry = item_entry_test(register_entry_id, test_item_id)

            try:
                assert og_report == report_data
            except AssertionError:
                print("\nDifference in initial khata report:")
                print_dict_diff(og_report, report_data)
                raise

            # Find all the pending bills between supplier and party
            pending_bills = RegisterEntry.get_pending_bills(
                test_supplier_id, test_party_id)
            # # Get Total Pending Amount

            # # TODO: make this automated later
            total_pending_amount = bill_amount
            quarter_pending = total_pending_amount // 4
            # Create a part memo for half that amount

            # Create a payment list report
            og_payment_report = make_report({
                "report": "payment_list",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": "2023-06-19",
                "to": "2023-06-19"
            })

            
            reference = {'title': 'Payment List', 'from': '2023-06-19', 'to': '2023-06-19', 'headings': [{'title': 'Party Name: test_pa3r4343', 'subheadings': [{'title': 'Supplier Name: test_suppli42334', 'dataRows': [{'part_no': '', 'part_date': '', 'part_amt': '', 'bill_no': 123456, 'bill_amt': '5,000', 'bill_date': '19/06/2023', 'pending_amt': 5000, 'days': 567, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': '0', 'column': 'part_amt', 'numeric': 0, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': '5,000', 'column': 'bill_amt', 'numeric': 5000, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': '5,000', 'column': 'bill_amt', 'numeric': 5000, 'beforeData': False}, {'name': 'Part (-)', 'value': '- 0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Pending (=)', 'value': '5,000', 'column': 'bill_amt', 'numeric': 5000, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': '5,000'}}], 'cumulative': {'name': 'Total Pending', 'value': '5,000'}}]}
            try: 
                assert og_payment_report == reference
            except AssertionError:
                print("Difference in Payment List Report")
                print_dict_diff(og_payment_report, reference)
                raise



            memo_number1 = 5517766
            # Create a Memo Entry
            part_input = {'memo_number': memo_number1,
                          'register_date': '2023-08-04',
                          'amount': quarter_pending,
                          'party_id': test_party_id,
                          'supplier_id': test_supplier_id,
                          'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '234'}],
                          'mode': 'Part'
                          }

            part_memo = check_status_and_return_class(
                MemoEntry.insert(part_input, get_cls=True))

            # Add to cleanup
            cleanup_list.append(part_memo)

            part_memo = MemoEntry.retrieve(
                test_supplier_id, test_party_id, memo_number1)

            part_memo_id = part_memo.get_id()

            # Create second report
            # Create Khata Report
            og_report = make_report({
                "report": "khata_report",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": "2023-06-19",
                "to": "2023-06-19"
            })

            # Want to create a khata report here and check the output
            report = TestKhataReport("khata_report", [test_party_id], [
                test_supplier_id], "2023-06-19", "2023-06-19")
            report_data = report.generate_table([register_entry], [part_memo])

            try:
                assert og_report == report_data
            except AssertionError:
                print("\nDifference in part memo khata report:")
                print_dict_diff(og_report, report_data)
                raise

            # Create Payment List Report
            og_payment_report = make_report({
                "report": "payment_list",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": "2023-06-19",
                "to": "2023-06-19"
            })


            reference = {'title': 'Payment List', 'from': '2023-06-19', 'to': '2023-06-19', 'headings': [{'title': 'Party Name: test_pa3r4343', 'subheadings': [{'title': 'Supplier Name: test_suppli42334', 'dataRows': [{'part_no': 5517766, 'part_date': '04/08/2023', 'part_amt': '1,250', 'bill_no': 123456, 'bill_amt': '5,000', 'bill_date': '19/06/2023', 'pending_amt': 5000, 'days': 567, 'status': 'N'}], 'specialRows': [{'name': 'Total (=)', 'value': '1,250', 'column': 'part_amt', 'numeric': 1250, 'beforeData': False}, {'name': '<60 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '60-120 days (+)', 'value': '0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': '>120 days (+)', 'value': '5,000', 'column': 'bill_amt', 'numeric': 5000, 'beforeData': False}, {'name': 'Subtotal (=)', 'value': '5,000', 'column': 'bill_amt', 'numeric': 5000, 'beforeData': False}, {'name': 'Part (-)', 'value': '- 1,250', 'column': 'bill_amt', 'numeric': 1250, 'beforeData': False}, {'name': 'Pending (=)', 'value': '3,750', 'column': 'bill_amt', 'numeric': 3750, 'beforeData': False}], 'displayOnIndex': True, 'cumulative': {'name': 'Total Pending', 'value': '3,750'}}], 'cumulative': {'name': 'Total Pending', 'value': '3,750'}}]}
            try:
                assert og_payment_report == reference
            except AssertionError:
                print("Difference in Payment List Report")
                print_dict_diff(og_payment_report, reference)
                raise

            gr_amount = 300
            deduction = 300
            part = quarter_pending

            amount = total_pending_amount - part - deduction - gr_amount

            memo_number2 = 394470334
            full_input = {'memo_number': memo_number2,
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

            full_memo = check_status_and_return_class(
                MemoEntry.insert(full_input, get_cls=True))

            # Add to cleanup
            cleanup_list.append(full_memo)

            # retrieve the memo entry
            full_memo = MemoEntry.retrieve(
                test_supplier_id, test_party_id, memo_number2)

            # Get Updated Register Entry
            # TODO: Here I should be manually setting the status. Do I need to set other stuff, yes.
            # Why should I not be pulling from the database, because then how I do make sure the state of register entry after memo_entry is correct?
            # But then if I have multiple register_entries, I would have to auto divide, well that helps you make sure the auto divide is working correctly
            # and I am going to write tests with at max 3 register_entries
            register_entry = RegisterEntry.retrieve(
                register_entry.supplier_id, register_entry.party_id, register_entry.bill_number, register_entry.register_date)

            # Test final khata report
            og_report = make_report({
                "report": "khata_report",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": "2023-06-19",
                "to": "2023-06-19"
            })

            # Create test khata report
            report = TestKhataReport("khata_report", [test_party_id], [
                test_supplier_id], "2023-06-19", "2023-06-19")
            report_data = report.generate_table([register_entry], [full_memo])

            try:
                assert og_report == report_data
            except AssertionError:
                print("\nDifference in final khata report:")
                print_dict_diff(og_report, report_data)
                raise

            # Create Supplier Register Report
            og_report = make_report({
                "report": "supplier_register",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": "2023-06-19",
                "to": "2023-06-19"
            })

            reference = {'title': 'Supplier Register', 'from': '2023-06-19', 'to': '2023-06-19', 'headings': [{'title': 'Supplier Name: test_suppli42334', 'subheadings': [{'title': '', 'dataRows': [{'bill_date': '19/06/2023', 'party_name': 'test_pa3r4343', 'bill_no': 123456, 'bill_amt': '5,000', 'pending_amt': '0', 'status': 'F'}], 'specialRows': [{'name': 'Total (=) ', 'value': '5,000', 'column': 'bill_amt', 'numeric': 5000, 'beforeData': False}, {'name': 'Pending (=) ', 'value': '0', 'column': 'pending_amt', 'numeric': 0, 'beforeData': False}], 'displayOnIndex': False}]}]}

            try:
                assert og_report == reference
            except AssertionError:
                print("Difference in Supplier Register Report")
                print_dict_diff(og_report, reference)
                raise


            # Create Payment List Report
            og_payment_report = make_report({
                "report": "payment_list",
                "suppliers": json.dumps([{"id": test_supplier_id}]),
                "parties": json.dumps([{"id": test_party_id}]),
                "from": "2023-06-19",
                "to": "2023-06-19"
            })

            # Assert that heading are empty
            try:
                assert len(og_payment_report["headings"]) == 0
            except AssertionError:
                print("\nDifference in empty payment list report:")
                print_dict_diff(og_payment_report['headings'], {"headings": []})
                raise

            print("All Tests Passed")

            # cleanup
            cleanup(cleanup_list)
        except Exception as e:
            # Delete all the entries
            cleanup(cleanup_list)
            raise e


if __name__ == "__main__":
    run_basic_test()
