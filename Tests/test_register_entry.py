import pytest
from datetime import datetime

from Entities import RegisterEntry
from API_Database import insert_register_entry, delete_entry
from Individual import Supplier, Party
from psql import db_connector
from .util import check_status_and_return_class, cleanup
from API_Database import parse_date, sql_date
from .test_report import TestKhataReport
from Reports import make_report

# Define a test case for inserting a register entry into the database
def test_insert(supplier: Supplier, party: Party):
    # Test data

    # Adding test data
    supplier_id = supplier.get_id()
    party_id = party.get_id()

    sample_input = {"bill_number": "12345",
                    "amount": "500",
                    "supplier_id": supplier_id,
                    "party_id": party_id,
                    "register_date": "2023-06-19",
                    "gr_amount": "100",
                    "deduction": "50",
                    "status": "P",}

    entry = RegisterEntry.insert(sample_input, get_cls=True)


    database_entry = RegisterEntry.retrieve(entry.supplier_id, entry.party_id, entry.bill_number)

    # Assertions
    assert database_entry.supplier_id == entry.supplier_id
    assert database_entry.party_id == entry.party_id
    assert database_entry.register_date == "19/06/2023"
    assert database_entry.amount == entry.amount
    assert database_entry.bill_number == entry.bill_number
    assert database_entry.status == entry.status
    assert database_entry.gr_amount == entry.gr_amount
    assert database_entry.deduction == entry.deduction
    
    # delete party and supplier
    entry.delete()

def test_register_entry_report():

    try: 
        # create cleanup list
        cleanup_list = []

        test_supplier_input = {"name": "test_supplier4343",
                        "address": "test_address"}


        test_party_input = {"name": "test_party4333",
                            "address": "test_address"}

        # Create a supplier and party instance
        test_supplier = check_status_and_return_class(
            Supplier.insert(test_supplier_input, get_cls=True))

        # Add to cleanup
        cleanup_list.append(test_supplier)

        test_party = check_status_and_return_class(
            Party.insert(test_party_input, get_cls=True))

        # Add to cleanup
        cleanup_list.append(test_party)

        # Find the supplier and party id
        test_supplier_id = test_supplier.get_id()
        test_party_id = test_party.get_id()
        
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

        # Create Khata Report
        og_report = make_report("khata_report", [test_supplier_id], [
                                test_party_id], "2023-06-19", "2023-06-19")

        # Want to create a khata report here and check the output
        report = TestKhataReport("khata_report", [test_party_id], [
                                test_supplier_id], "2023-06-19", "2023-06-19")
        report_data = report.generate_table([register_entry], [])
        
        assert og_report == report_data

        # Delete all the entries
        cleanup(cleanup_list)

    except Exception as e:
        # Delete all the entries
        cleanup(cleanup_list)
        raise e

# Run the tests
def run():
    pytest.main()
