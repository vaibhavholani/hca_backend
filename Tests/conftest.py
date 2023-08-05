import pytest


# Define a fixture that yields multiple class instances
@pytest.fixture
def sample_data():
    
    sample = {
        "supplier": {"name": "test_supplier", "address": "test_address"}, 
        "register_entry": {"bill_number": "12345",
                    "amount": "500",
                    "supplier_id": "2307",
                    "party_id": "2307",
                    "register_date": "2023-06-19",
                    "gr_amount": "100",
                    "deduction": "50",
                    "status": "P",
                    "partial_amount": "50"}
    }
    yield sample

def pytest_sessionstart(session): 
    """ Runs before whole test starts"""
    pass

def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """
