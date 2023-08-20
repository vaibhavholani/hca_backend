from typing import Dict, Union
from Individual import Supplier, Party
from Entities import RegisterEntry, MemoEntry, OrderForm
from Tests import TestKhataReport
from Reports import make_report
from Tests import check_status_and_return_class, cleanup


def run_basic_test():
    try:
        # create cleanup list
        cleanup_list = []

        test_supplier_input = {"name": "test_supplier15",
                               "address": "test_address"}

        test_party_input = {"name": "test_party15",
                            "address": "test_address"}

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

        
        # Create Order Form
        order_form_number = 1
        order_form_input = {
            "supplier_id": test_supplier_id,
            "party_id": test_party_id,
            "register_date": "2023-06-17", 
            "order_form_number": order_form_number,
        }

        test_order_form = check_status_and_return_class(OrderForm.insert(order_form_input, get_cls=True))

        # Add to cleanup
        cleanup_list.append(test_order_form)

        # Retrieve the order form
        test_order_form = OrderForm.retrieve(test_supplier_id, test_party_id, order_form_number)

        # Create a Order Form Report
        og_report = make_report("order_form", [test_supplier_id], [
                                test_party_id], "2023-06-16", "2023-06-19")
        
        # Checking Report for correct order form data
        order_form_data = og_report["headings"][0]["subheadings"][0]["dataRows"][0]
        assert int(order_form_data["order_no"]) == order_form_number
        assert order_form_data["order_date"] == "17/06/2023"
        assert order_form_data["supp_name"] == test_supplier_input["name"]
        assert order_form_data["party_name"] == test_party_input["name"]
        assert len(og_report["headings"][0]["subheadings"]) == 1

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
            test_supplier_id, test_party_id, "123456")
        
        # Checking that there are no orderforms in the report
        og_report = make_report("order_form", [test_supplier_id], [
                                test_party_id], "2023-06-16", "2023-06-19")
        assert len(og_report["headings"]) == 0

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
        part_input = {'memo_number': 38439,
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

        part_memo = MemoEntry.retrieve(test_supplier_id, test_party_id, 38439)

        part_memo_id = part_memo.get_id()

        # Create second report
        # Create Khata Report
        og_report = make_report("khata_report", [test_supplier_id], [
                                test_party_id], "2023-06-19", "2023-06-19")

        # Want to create a khata report here and check the output
        report = TestKhataReport("khata_report", [test_party_id], [
            test_supplier_id], "2023-06-19", "2023-06-19")
        report_data = report.generate_table([register_entry], [part_memo])

        assert og_report == report_data

        gr_amount = 300
        deduction = 300
        part = quarter_pending

        amount = total_pending_amount - part - deduction - gr_amount

        full_input = {'memo_number': 3970,
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
        full_memo = MemoEntry.retrieve(test_supplier_id, test_party_id, 3970)

        # Get Updated Register Entry
        # TODO: Here I should be manually setting the status. Do I need to set other stuff, yes.
        # Why should I not be pulling from the database, because then how I do make sure the state of register entry after memo_entry is correct?
        # But then if I have multiple register_entries, I would have to auto divide, well that helps you make sure the auto divide is working correctly
        # and I am going to write tests with at max 3 register_entries
        register_entry = RegisterEntry.retrieve(
            register_entry.supplier_id, register_entry.party_id, register_entry.bill_number)

        # Create third report
        og_report = make_report("khata_report", [test_supplier_id], [
                                test_party_id], "2023-06-19", "2023-06-19")

        # Want to create a khata report here and check the output
        report = TestKhataReport("khata_report", [test_party_id], [
            test_supplier_id], "2023-06-19", "2023-06-19")
        report_data = report.generate_table([register_entry], [full_memo])

        assert og_report == report_data

        # cleanup
        cleanup(cleanup_list)

    except Exception as e:
        # Delete all the entries
        cleanup(cleanup_list)
        raise e


if __name__ == "__main__":
    run_basic_test()
