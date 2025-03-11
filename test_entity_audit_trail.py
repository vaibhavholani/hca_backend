#!/usr/bin/env python
"""
Comprehensive test script for the audit trail functionality across all entity types.
This test verifies that audit logs are properly created for all entity types in the system.
"""
import json
import signal
import sys
import os
import uuid
from typing import Dict, Union, List, Optional, Any, Tuple
from contextlib import contextmanager
from datetime import datetime, timedelta
from dotenv import load_dotenv
from Individual.User import User
from Individual.Supplier import Supplier
from Individual.Party import Party
from Individual.Bank import Bank
from Individual.Transporter import Transporter
from Entities.Item import Item
from Entities.ItemEntry import ItemEntry
from Entities.MemoEntry import MemoEntry
from Entities.OrderForm import OrderForm
from Entities.RegisterEntry import RegisterEntry
from API_Database.audit_log import record_audit_log, get_audit_history, search_audit_logs, compare_changes
from psql import execute_query

load_dotenv()

# Test constants
TEST_USERNAME = f"test_user_{uuid.uuid4().hex[:8]}"  # Generate unique username for each test run
TEST_PASSWORD = "test_password"
TEST_ROLE = "user"
TEST_FULL_NAME = "Test User"
TEST_EMAIL = "test@example.com"
TEST_SUPPLIER_NAME = f"test_supplier_{uuid.uuid4().hex[:8]}"
TEST_SUPPLIER_ADDRESS = "123 Test Street"
TEST_SUPPLIER_PHONE = "1234567890"
TEST_PARTY_NAME = f"test_party_{uuid.uuid4().hex[:8]}"
TEST_PARTY_ADDRESS = "456 Test Avenue"
TEST_PARTY_PHONE = "9876543210"
TEST_BANK_NAME = f"test_bank_{uuid.uuid4().hex[:8]}"
TEST_BANK_ADDRESS = "789 Test Boulevard"
TEST_TRANSPORTER_NAME = f"test_transporter_{uuid.uuid4().hex[:8]}"
TEST_TRANSPORTER_ADDRESS = "321 Test Road"
TEST_ITEM_NAME = f"test_item_{uuid.uuid4().hex[:8]}"
TEST_ITEM_COLOR = "Red"
TEST_BILL_NUMBER = f"BILL-{uuid.uuid4().hex[:8]}"
TEST_MEMO_NUMBER = int(uuid.uuid4().int % 10000000)
TEST_ORDER_FORM_NUMBER = int(uuid.uuid4().int % 1000)
TODAY = datetime.now().date()
YESTERDAY = (TODAY - timedelta(days=1)).strftime('%Y-%m-%d')

@contextmanager
def cleanup_context(cleanup_list):
    """Context manager that yields the cleanup_list and calls cleanup(cleanup_list) upon exit."""
    try:
        yield cleanup_list
    finally:
        cleanup(cleanup_list)

def signal_handler(signum, frame):
    """Handles OS signals by printing an interrupt message and gracefully exiting the program."""
    print('Received interrupt, cleaning up...')
    sys.exit(0)

def cleanup(cleanup_list):
    """
    Clean up test data by deactivating users and deleting test records.
    
    Args:
        cleanup_list: List of objects to clean up
    """
    print("\nCleaning up test data...")
    
    # Try to find a user ID to use for audit trail
    user_id = None
    for item in cleanup_list:
        if isinstance(item, User) and hasattr(item, 'id'):
            user_id = item.id
            break
    
    for item in cleanup_list:
        try:
            if isinstance(item, User):
                print(f"Deactivating user: {item.username}")
                item.is_active = False
                item.update(updated_by=user_id)
            elif hasattr(item, 'delete'):
                print(f"Deleting item: {item}")
                item.delete(current_user_id=user_id)
            elif isinstance(item, tuple) and len(item) == 2:
                # Handle records that don't have a delete method
                table_name, record_id = item
                print(f"Deleting {table_name} with ID: {record_id}")
                delete_query = f"""
                DELETE FROM {table_name}
                WHERE id = {record_id}
                """
                execute_query(delete_query, current_user_id=user_id)
        except Exception as e:
            print(f"Error cleaning up {item}: {str(e)}")

def create_test_user() -> Tuple[User, List]:
    """
    Create a test user for testing.
    
    Returns:
        Tuple[User, List]: The created user and a cleanup list
    """
    cleanup_list = []
    
    # Check if user already exists
    existing_user = User.get_by_username(TEST_USERNAME)
    if existing_user:
        print(f"Test user already exists with ID: {existing_user.id}")
        # Ensure the user is active for testing
        if not existing_user.is_active:
            print("Reactivating existing test user...")
            existing_user.is_active = True
            # Use the user's own ID for the update
            existing_user.update(updated_by=existing_user.id)
        test_user = existing_user
    else:
        # Create a new user
        print(f"Creating new test user: {TEST_USERNAME}")
        test_user = User.create(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            role=TEST_ROLE,
            full_name=TEST_FULL_NAME,
            email=TEST_EMAIL
        )
        print(f"Created test user with ID: {test_user.id}")
    
    cleanup_list.append(test_user)
    return test_user, cleanup_list

def verify_audit_history(table_name: str, record_id: int, expected_actions: List[str]) -> bool:
    """
    Verify that the audit history for a record contains the expected actions.
    
    Args:
        table_name: The name of the table
        record_id: The ID of the record
        expected_actions: The expected actions in the audit history
    
    Returns:
        bool: True if the audit history matches the expected actions, False otherwise
    """
    history_result = get_audit_history(table_name, record_id)
    
    if history_result['status'] != 'okay':
        print(f"Error getting audit history: {history_result.get('message', 'Unknown error')}")
        return False
    
    if not history_result.get('history'):
        print("No audit history found")
        return False
    
    # Check that all expected actions are present
    actual_actions = [entry['action'] for entry in history_result['history']]
    print(f"Expected actions: {expected_actions}")
    print(f"Actual actions: {actual_actions}")
    
    # Check if all expected actions are in the actual actions
    # Note: The order might be different due to timestamp ordering
    return all(action in actual_actions for action in expected_actions)

def test_user_audit_trail():
    """Test audit trail for User entity."""
    print("\n=== Testing User Audit Trail ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Verify INSERT audit log
        print("\nVerifying INSERT audit log for User...")
        assert verify_audit_history("users", user_id, ["INSERT"]), "INSERT audit log not found for User"
        print("INSERT audit log verified for User")
        
        # Update the user
        print("\nUpdating test user...")
        test_user.full_name = "Updated Test User"
        update_result = test_user.update(updated_by=user_id)
        assert update_result['status'] == 'okay', f"User update failed: {update_result.get('message', 'Unknown error')}"
        
        # Verify UPDATE audit log
        print("\nVerifying UPDATE audit log for User...")
        assert verify_audit_history("users", user_id, ["INSERT", "UPDATE"]), "UPDATE audit log not found for User"
        print("UPDATE audit log verified for User")
        
        # Deactivate the user (soft delete)
        print("\nDeactivating test user...")
        test_user.is_active = False
        deactivate_result = test_user.update(updated_by=user_id)
        assert deactivate_result['status'] == 'okay', f"User deactivation failed: {deactivate_result.get('message', 'Unknown error')}"
        
        # Verify another UPDATE audit log for deactivation
        print("\nVerifying UPDATE audit log for User deactivation...")
        assert verify_audit_history("users", user_id, ["INSERT", "UPDATE", "UPDATE"]), "UPDATE audit log not found for User deactivation"
        print("UPDATE audit log verified for User deactivation")
        
        print("\nUser audit trail tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in user audit trail test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in user audit trail test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_supplier_audit_trail():
    """Test audit trail for Supplier entity."""
    print("\n=== Testing Supplier Audit Trail ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test supplier
        print("\nCreating a test supplier...")
        supplier_input = {
            'name': TEST_SUPPLIER_NAME,
            'address': TEST_SUPPLIER_ADDRESS,
            'phone_number': TEST_SUPPLIER_PHONE
        }
        supplier_result = Supplier.insert(supplier_input, get_cls=True, current_user_id=user_id)
        assert supplier_result['status'] == 'okay', f"Supplier creation failed: {supplier_result.get('message', 'Unknown error')}"
        test_supplier = supplier_result['class']
        supplier_id = test_supplier.get_id()
        cleanup_list.append(test_supplier)
        print(f"Created test supplier with ID: {supplier_id}")
        
        # Verify INSERT audit log
        print("\nVerifying INSERT audit log for Supplier...")
        assert verify_audit_history("supplier", supplier_id, ["INSERT"]), "INSERT audit log not found for Supplier"
        print("INSERT audit log verified for Supplier")
        
        # Update the supplier
        print("\nUpdating test supplier...")
        test_supplier.address = "Updated Test Address"
        update_result = test_supplier.update(current_user_id=user_id)
        assert update_result['status'] == 'okay', f"Supplier update failed: {update_result.get('message', 'Unknown error')}"
        
        # Verify UPDATE audit log
        print("\nVerifying UPDATE audit log for Supplier...")
        assert verify_audit_history("supplier", supplier_id, ["INSERT", "UPDATE"]), "UPDATE audit log not found for Supplier"
        print("UPDATE audit log verified for Supplier")
        
        # Delete the supplier
        print("\nDeleting test supplier...")
        delete_result = test_supplier.delete(current_user_id=user_id)
        assert delete_result['status'] == 'okay', f"Supplier delete failed: {delete_result.get('message', 'Unknown error')}"
        
        # Verify DELETE audit log
        print("\nVerifying DELETE audit log for Supplier...")
        assert verify_audit_history("supplier", supplier_id, ["INSERT", "UPDATE", "DELETE"]), "DELETE audit log not found for Supplier"
        print("DELETE audit log verified for Supplier")
        
        print("\nSupplier audit trail tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in supplier audit trail test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in supplier audit trail test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_party_audit_trail():
    """Test audit trail for Party entity."""
    print("\n=== Testing Party Audit Trail ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test party
        print("\nCreating a test party...")
        party_input = {
            'name': TEST_PARTY_NAME,
            'address': TEST_PARTY_ADDRESS,
            'phone_number': TEST_PARTY_PHONE
        }
        party_result = Party.insert(party_input, get_cls=True, current_user_id=user_id)
        assert party_result['status'] == 'okay', f"Party creation failed: {party_result.get('message', 'Unknown error')}"
        test_party = party_result['class']
        party_id = test_party.get_id()
        cleanup_list.append(test_party)
        print(f"Created test party with ID: {party_id}")
        
        # Verify INSERT audit log
        print("\nVerifying INSERT audit log for Party...")
        assert verify_audit_history("party", party_id, ["INSERT"]), "INSERT audit log not found for Party"
        print("INSERT audit log verified for Party")
        
        # Update the party
        print("\nUpdating test party...")
        test_party.address = "Updated Party Address"
        update_result = test_party.update(current_user_id=user_id)
        assert update_result['status'] == 'okay', f"Party update failed: {update_result.get('message', 'Unknown error')}"
        
        # Verify UPDATE audit log
        print("\nVerifying UPDATE audit log for Party...")
        assert verify_audit_history("party", party_id, ["INSERT", "UPDATE"]), "UPDATE audit log not found for Party"
        print("UPDATE audit log verified for Party")
        
        # Delete the party
        print("\nDeleting test party...")
        delete_result = test_party.delete(current_user_id=user_id)
        assert delete_result['status'] == 'okay', f"Party delete failed: {delete_result.get('message', 'Unknown error')}"
        
        # Verify DELETE audit log
        print("\nVerifying DELETE audit log for Party...")
        assert verify_audit_history("party", party_id, ["INSERT", "UPDATE", "DELETE"]), "DELETE audit log not found for Party"
        print("DELETE audit log verified for Party")
        
        print("\nParty audit trail tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in party audit trail test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in party audit trail test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_bank_audit_trail():
    """Test audit trail for Bank entity."""
    print("\n=== Testing Bank Audit Trail ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test bank
        print("\nCreating a test bank...")
        bank_input = {
            'name': TEST_BANK_NAME,
            'address': TEST_BANK_ADDRESS
        }
        bank_result = Bank.insert(bank_input, get_cls=True, current_user_id=user_id)
        assert bank_result['status'] == 'okay', f"Bank creation failed: {bank_result.get('message', 'Unknown error')}"
        test_bank = bank_result['class']
        bank_id = test_bank.get_id()
        cleanup_list.append(test_bank)
        print(f"Created test bank with ID: {bank_id}")
        
        # Verify INSERT audit log
        print("\nVerifying INSERT audit log for Bank...")
        assert verify_audit_history("bank", bank_id, ["INSERT"]), "INSERT audit log not found for Bank"
        print("INSERT audit log verified for Bank")
        
        # Update the bank
        print("\nUpdating test bank...")
        test_bank.address = "Updated Bank Address"
        update_result = test_bank.update(current_user_id=user_id)
        assert update_result['status'] == 'okay', f"Bank update failed: {update_result.get('message', 'Unknown error')}"
        
        # Verify UPDATE audit log
        print("\nVerifying UPDATE audit log for Bank...")
        assert verify_audit_history("bank", bank_id, ["INSERT", "UPDATE"]), "UPDATE audit log not found for Bank"
        print("UPDATE audit log verified for Bank")
        
        # Delete the bank
        print("\nDeleting test bank...")
        delete_result = test_bank.delete(current_user_id=user_id)
        assert delete_result['status'] == 'okay', f"Bank delete failed: {delete_result.get('message', 'Unknown error')}"
        
        # Verify DELETE audit log
        print("\nVerifying DELETE audit log for Bank...")
        assert verify_audit_history("bank", bank_id, ["INSERT", "UPDATE", "DELETE"]), "DELETE audit log not found for Bank"
        print("DELETE audit log verified for Bank")
        
        print("\nBank audit trail tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in bank audit trail test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in bank audit trail test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_transporter_audit_trail():
    """Test audit trail for Transporter entity."""
    print("\n=== Testing Transporter Audit Trail ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test transporter
        print("\nCreating a test transporter...")
        transporter_input = {
            'name': TEST_TRANSPORTER_NAME,
            'address': TEST_TRANSPORTER_ADDRESS
        }
        transporter_result = Transporter.insert(transporter_input, get_cls=True, current_user_id=user_id)
        assert transporter_result['status'] == 'okay', f"Transporter creation failed: {transporter_result.get('message', 'Unknown error')}"
        test_transporter = transporter_result['class']
        transporter_id = test_transporter.get_id()
        cleanup_list.append(test_transporter)
        print(f"Created test transporter with ID: {transporter_id}")
        
        # Verify INSERT audit log
        print("\nVerifying INSERT audit log for Transporter...")
        assert verify_audit_history("transporter", transporter_id, ["INSERT"]), "INSERT audit log not found for Transporter"
        print("INSERT audit log verified for Transporter")
        
        # Update the transporter
        print("\nUpdating test transporter...")
        test_transporter.address = "Updated Transporter Address"
        update_result = test_transporter.update(current_user_id=user_id)
        assert update_result['status'] == 'okay', f"Transporter update failed: {update_result.get('message', 'Unknown error')}"
        
        # Verify UPDATE audit log
        print("\nVerifying UPDATE audit log for Transporter...")
        assert verify_audit_history("transporter", transporter_id, ["INSERT", "UPDATE"]), "UPDATE audit log not found for Transporter"
        print("UPDATE audit log verified for Transporter")
        
        # Delete the transporter
        print("\nDeleting test transporter...")
        delete_result = test_transporter.delete(current_user_id=user_id)
        assert delete_result['status'] == 'okay', f"Transporter delete failed: {delete_result.get('message', 'Unknown error')}"
        
        # Verify DELETE audit log
        print("\nVerifying DELETE audit log for Transporter...")
        assert verify_audit_history("transporter", transporter_id, ["INSERT", "UPDATE", "DELETE"]), "DELETE audit log not found for Transporter"
        print("DELETE audit log verified for Transporter")
        
        print("\nTransporter audit trail tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in transporter audit trail test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in transporter audit trail test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_item_audit_trail():
    """Test audit trail for Item entity."""
    print("\n=== Testing Item Audit Trail ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test supplier for the item
        print("\nCreating a test supplier for the item...")
        supplier_input = {
            'name': TEST_SUPPLIER_NAME,
            'address': TEST_SUPPLIER_ADDRESS,
            'phone_number': TEST_SUPPLIER_PHONE
        }
        supplier_result = Supplier.insert(supplier_input, get_cls=True, current_user_id=user_id)
        assert supplier_result['status'] == 'okay', f"Supplier creation failed: {supplier_result.get('message', 'Unknown error')}"
        test_supplier = supplier_result['class']
        supplier_id = test_supplier.get_id()
        cleanup_list.append(test_supplier)
        print(f"Created test supplier with ID: {supplier_id}")
        
        # Create a test item
        print("\nCreating a test item...")
        item_input = {
            'supplier_id': supplier_id,
            'name': TEST_ITEM_NAME,
            'color': TEST_ITEM_COLOR
        }
        item_result = Item.insert(item_input, get_cls=True)
        assert item_result['status'] == 'okay', f"Item creation failed: {item_result.get('message', 'Unknown error')}"
        test_item = item_result['class']
        item_id = test_item.get_id()
        cleanup_list.append(test_item)
        print(f"Created test item with ID: {item_id}")
        
        # Verify INSERT audit log
        print("\nVerifying INSERT audit log for Item...")
        assert verify_audit_history("item", item_id, ["INSERT"]), "INSERT audit log not found for Item"
        print("INSERT audit log verified for Item")
        
        # Update the item
        print("\nUpdating test item...")
        update_data = {'color': 'Blue'}
        update_result = test_item.update(update_data)
        assert update_result['status'] == 'okay', f"Item update failed: {update_result.get('message', 'Unknown error')}"
        
        # Verify UPDATE audit log
        print("\nVerifying UPDATE audit log for Item...")
        assert verify_audit_history("item", item_id, ["INSERT", "UPDATE"]), "UPDATE audit log not found for Item"
        print("UPDATE audit log verified for Item")
        
        # Delete the item
        print("\nDeleting test item...")
        delete_result = test_item.delete()
        assert delete_result['status'] == 'okay', f"Item delete failed: {delete_result.get('message', 'Unknown error')}"
        
        # Verify DELETE audit log
        print("\nVerifying DELETE audit log for Item...")
        assert verify_audit_history("item", item_id, ["INSERT", "UPDATE", "DELETE"]), "DELETE audit log not found for Item"
        print("DELETE audit log verified for Item")
        
        print("\nItem audit trail tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in item audit trail test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in item audit trail test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_register_entry_audit_trail():
    """Test audit trail for RegisterEntry entity."""
    print("\n=== Testing RegisterEntry Audit Trail ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test supplier
        print("\nCreating a test supplier...")
        supplier_input = {
            'name': TEST_SUPPLIER_NAME,
            'address': TEST_SUPPLIER_ADDRESS,
            'phone_number': TEST_SUPPLIER_PHONE
        }
        supplier_result = Supplier.insert(supplier_input, get_cls=True, current_user_id=user_id)
        assert supplier_result['status'] == 'okay', f"Supplier creation failed: {supplier_result.get('message', 'Unknown error')}"
        test_supplier = supplier_result['class']
        supplier_id = test_supplier.get_id()
        cleanup_list.append(test_supplier)
        print(f"Created test supplier with ID: {supplier_id}")
        
        # Create a test party
        print("\nCreating a test party...")
        party_input = {
            'name': TEST_PARTY_NAME,
            'address': TEST_PARTY_ADDRESS,
            'phone_number': TEST_PARTY_PHONE
        }
        party_result = Party.insert(party_input, get_cls=True, current_user_id=user_id)
        assert party_result['status'] == 'okay', f"Party creation failed: {party_result.get('message', 'Unknown error')}"
        test_party = party_result['class']
        party_id = test_party.get_id()
        cleanup_list.append(test_party)
        print(f"Created test party with ID: {party_id}")
        
        # Create a test register entry (bill)
        print("\nCreating a test register entry (bill)...")
        bill_input = {
            'bill_number': TEST_BILL_NUMBER,
            'amount': 5000,
            'supplier_id': supplier_id,
            'party_id': party_id,
            'register_date': YESTERDAY
        }
        register_entry_result = RegisterEntry.insert(bill_input, get_cls=True)
        assert register_entry_result['status'] == 'okay', f"RegisterEntry creation failed: {register_entry_result.get('message', 'Unknown error')}"
        test_register_entry = register_entry_result['class']
        register_entry_id = test_register_entry.get_id()
        cleanup_list.append(test_register_entry)
        print(f"Created test register entry with ID: {register_entry_id}")
        
        # Verify INSERT audit log
        print("\nVerifying INSERT audit log for RegisterEntry...")
        assert verify_audit_history("register_entry", register_entry_id, ["INSERT"]), "INSERT audit log not found for RegisterEntry"
        print("INSERT audit log verified for RegisterEntry")
        
        # Update the register entry
        print("\nUpdating test register entry...")
        update_data = {'amount': 6000}
        update_result = test_register_entry.update(update_data)
        assert update_result['status'] == 'okay', f"RegisterEntry update failed: {update_result.get('message', 'Unknown error')}"
        
        # Verify UPDATE audit log
        print("\nVerifying UPDATE audit log for RegisterEntry...")
        assert verify_audit_history("register_entry", register_entry_id, ["INSERT", "UPDATE"]), "UPDATE audit log not found for RegisterEntry"
        print("UPDATE audit log verified for RegisterEntry")
        
        # Delete the register entry
        print("\nDeleting test register entry...")
        delete_result = test_register_entry.delete()
        assert delete_result['status'] == 'okay', f"RegisterEntry delete failed: {delete_result.get('message', 'Unknown error')}"
        
        # Verify DELETE audit log
        print("\nVerifying DELETE audit log for RegisterEntry...")
        assert verify_audit_history("register_entry", register_entry_id, ["INSERT", "UPDATE", "DELETE"]), "DELETE audit log not found for RegisterEntry"
        print("DELETE audit log verified for RegisterEntry")
        
        print("\nRegisterEntry audit trail tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in register entry audit trail test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in register entry audit trail test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_memo_entry_audit_trail():
    """Test audit trail for MemoEntry entity."""
    print("\n=== Testing MemoEntry Audit Trail ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test supplier
        print("\nCreating a test supplier...")
        supplier_input = {
            'name': TEST_SUPPLIER_NAME,
            'address': TEST_SUPPLIER_ADDRESS,
            'phone_number': TEST_SUPPLIER_PHONE
        }
        supplier_result = Supplier.insert(supplier_input, get_cls=True, current_user_id=user_id)
        assert supplier_result['status'] == 'okay', f"Supplier creation failed: {supplier_result.get('message', 'Unknown error')}"
        test_supplier = supplier_result['class']
        supplier_id = test_supplier.get_id()
        cleanup_list.append(test_supplier)
        print(f"Created test supplier with ID: {supplier_id}")
        
        # Create a test party
        print("\nCreating a test party...")
        party_input = {
            'name': TEST_PARTY_NAME,
            'address': TEST_PARTY_ADDRESS,
            'phone_number': TEST_PARTY_PHONE
        }
        party_result = Party.insert(party_input, get_cls=True, current_user_id=user_id)
        assert party_result['status'] == 'okay', f"Party creation failed: {party_result.get('message', 'Unknown error')}"
        test_party = party_result['class']
        party_id = test_party.get_id()
        cleanup_list.append(test_party)
        print(f"Created test party with ID: {party_id}")
        
        # Create a test memo entry
        print("\nCreating a test memo entry...")
        memo_input = {
            'memo_number': TEST_MEMO_NUMBER,
            'register_date': YESTERDAY,
            'amount': 1000,
            'party_id': party_id,
            'supplier_id': supplier_id,
            'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '12345'}],
            'mode': 'Part'
        }
        memo_entry_result = MemoEntry.insert(memo_input, get_cls=True)
        assert memo_entry_result['status'] == 'okay', f"MemoEntry creation failed: {memo_entry_result.get('message', 'Unknown error')}"
        test_memo_entry = memo_entry_result['class']
        memo_entry_id = test_memo_entry.get_id()
        cleanup_list.append(test_memo_entry)
        print(f"Created test memo entry with ID: {memo_entry_id}")
        
        # Verify INSERT audit log
        print("\nVerifying INSERT audit log for MemoEntry...")
        assert verify_audit_history("memo_entry", memo_entry_id, ["INSERT"]), "INSERT audit log not found for MemoEntry"
        print("INSERT audit log verified for MemoEntry")
        
        # Update the memo entry
        print("\nUpdating test memo entry...")
        update_data = {'amount': 1100}
        update_result = test_memo_entry.update(update_data)
        assert update_result['status'] == 'okay', f"MemoEntry update failed: {update_result.get('message', 'Unknown error')}"

        # Verify UPDATE audit log
        print("\nVerifying UPDATE audit log for MemoEntry...")
        assert verify_audit_history("memo_entry", memo_entry_id, ["INSERT", "UPDATE"]), "UPDATE audit log not found for MemoEntry"
        print("UPDATE audit log verified for MemoEntry")
        
        # Delete the memo entry 
        print("\nDeleting test memo entry...")
        delete_result = test_memo_entry.delete()
        assert delete_result['status'] == 'okay', f"MemoEntry delete failed: {delete_result.get('message', 'Unknown error')}"
        
        # Verify DELETE audit log
        print("\nVerifying DELETE audit log for MemoEntry...")  
        assert verify_audit_history("memo_entry", memo_entry_id, ["INSERT", "UPDATE", "DELETE"]), "DELETE audit log not found for MemoEntry"
        print("DELETE audit log verified for MemoEntry")
        
        print("\nMemoEntry audit trail tests passed")
        return True
    except AssertionError as e: 
        print(f"Assertion error in memo entry audit trail test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in memo entry audit trail test: {str(e)}")
        import traceback
        traceback.print_exc()               
        return False
    finally:
        cleanup(cleanup_list)

def run_all_tests():
    """Run all test functions and print results."""
    test_functions = [
        test_user_audit_trail,
        # test_supplier_audit_trail,
        # test_party_audit_trail,
        # test_bank_audit_trail,
        # test_transporter_audit_trail,
        # test_item_audit_trail,
        # test_register_entry_audit_trail,
        # test_memo_entry_audit_trail,
    ]
    
    results = {}
    for test_func in test_functions:
        print(f"\nRunning {test_func.__name__}...")
        result = test_func()
        results[test_func.__name__] = result
    
    print("\nTest results:")
    for test_name, result in results.items():
        print(f"{test_name}: {'Passed' if result else 'Failed'}")
    
    print("\nAudit trail tests completed")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    run_all_tests() 

    