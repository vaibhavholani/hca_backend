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

def test_insert(supplier: Supplier, party: Party):
    """Tests insertion of a register entry and verifies that the retrieved data matches the inserted values."""
    supplier_id = supplier.get_id()
    party_id = party.get_id()
    sample_input = {'bill_number': '12345', 'amount': '500', 'supplier_id': supplier_id, 'party_id': party_id, 'register_date': '2023-06-19', 'gr_amount': '100', 'deduction': '50', 'status': 'P'}
    entry = RegisterEntry.insert(sample_input, get_cls=True)
    database_entry = RegisterEntry.retrieve(entry.supplier_id, entry.party_id, entry.bill_number)
    assert database_entry.supplier_id == entry.supplier_id
    assert database_entry.party_id == entry.party_id
    assert database_entry.register_date == '19/06/2023'
    assert database_entry.amount == entry.amount
    assert database_entry.bill_number == entry.bill_number
    assert database_entry.status == entry.status
    assert database_entry.gr_amount == entry.gr_amount
    assert database_entry.deduction == entry.deduction
    entry.delete()

def test_register_entry_report():
    """Tests generation and verification of the register entry report."""
    try:
        cleanup_list = []
        test_supplier_input = {'name': 'test_supplier4343', 'address': 'test_address'}
        test_party_input = {'name': 'test_party4333', 'address': 'test_address'}
        test_supplier = check_status_and_return_class(Supplier.insert(test_supplier_input, get_cls=True))
        cleanup_list.append(test_supplier)
        test_party = check_status_and_return_class(Party.insert(test_party_input, get_cls=True))
        cleanup_list.append(test_party)
        test_supplier_id = test_supplier.get_id()
        test_party_id = test_party.get_id()
        bill_amount = 5000
        bill_input = {'bill_number': '123456', 'amount': bill_amount, 'supplier_id': test_supplier_id, 'party_id': test_party_id, 'register_date': '2023-06-19'}
        register_entry = check_status_and_return_class(RegisterEntry.insert(bill_input, get_cls=True))
        cleanup_list.append(register_entry)
        og_report = make_report('khata_report', [test_supplier_id], [test_party_id], '2023-06-19', '2023-06-19')
        report = TestKhataReport('khata_report', [test_party_id], [test_supplier_id], '2023-06-19', '2023-06-19')
        report_data = report.generate_table([register_entry], [])
        assert og_report == report_data
        cleanup(cleanup_list)
    except Exception as e:
        cleanup(cleanup_list)
        raise e

def run():
    """Executes all register entry tests using pytest."""
    pytest.main()