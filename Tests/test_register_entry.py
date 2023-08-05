import pytest
from datetime import datetime

from Entities import RegisterEntry
from API_Database import insert_register_entry, delete_entry
from psql import db_connector
from .util import insert_party, insert_supplier, delete_party, delete_supplier

# Define a test case for inserting a register entry into the database
def test_insert_register_entry():
    # Test data

    # Adding test data
    id = 2307
    insert_supplier(id)
    insert_party(id)

    sample_input = {"bill_number": "12345",
                    "amount": "500",
                    "supplier_id": "2307",
                    "party_id": "2307",
                    "register_date": "2023-06-19",
                    "gr_amount": "100",
                    "deduction": "50",
                    "status": "P",
                    "partial_amount": "50"}

    entry = RegisterEntry.create_instance(sample_input)

    # Perform the data entry operation
    insert_register_entry.insert_register_entry(entry)

    # Retrieve the inserted entry from the database
    db, db_cursor = db_connector.cursor(True)

    # Query the database for the inserted entry
    query = "select * from register_entry where " \
            "bill_number = '{}' AND supplier_id = '{}' AND party_id = '{}'". \
        format(entry.bill_number, entry.supplier_id, entry.party_id)
    
    db_cursor.execute(query)
    result = db_cursor.fetchone()

    # Assertions
    assert result  # Check if the entry exists
    assert result["supplier_id"] == entry.supplier_id
    assert result["party_id"] == entry.party_id
    assert result["register_date"] == entry.date
    assert result["amount"] == entry.amount
    assert result["bill_number"] == entry.bill_number
    assert result["status"] == entry.status
    assert result["deduction"] == entry.deduction

    # Delete the inserted entry
    delete_entry.delete_entry(result, "register_entry")
    
    # delete party and supplier
    delete_supplier(id)
    delete_party(id)

# Run the tests
def run():
    pytest.main()
