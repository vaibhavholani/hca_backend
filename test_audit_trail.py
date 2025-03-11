#!/usr/bin/env python
"""
Comprehensive test script for the audit trail and user management system.
This test follows the structure of test_input.py but is specifically tailored
for testing the audit trail functionality.
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
TODAY = datetime.now().date()

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
    
    for item in cleanup_list:
        try:
            if isinstance(item, User):
                print(f"Deactivating user: {item.username}")
                item.is_active = False
                item.update()
            elif hasattr(item, 'delete'):
                print(f"Deleting item: {item}")
                item.delete()
            elif isinstance(item, tuple) and len(item) == 2 and item[0] == 'supplier':
                # Handle supplier records that don't have a delete method
                supplier_id = item[1]
                print(f"Deleting supplier with ID: {supplier_id}")
                delete_query = f"""
                DELETE FROM supplier
                WHERE id = {supplier_id}
                """
                execute_query(delete_query)
            elif isinstance(item, tuple) and len(item) == 2 and item[0] == 'audit_log':
                # Handle audit log records that don't have a delete method
                audit_id = item[1]
                print(f"Deleting audit log with ID: {audit_id}")
                delete_query = f"""
                DELETE FROM audit_log
                WHERE id = {audit_id}
                """
                execute_query(delete_query)
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
            existing_user.update()
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

def create_test_supplier(user_id: Optional[int] = None) -> Tuple[int, List]:
    """
    Create a test supplier for testing.
    
    Args:
        user_id: The ID of the user creating the supplier
    
    Returns:
        Tuple[int, List]: The supplier ID and a cleanup list
    """
    cleanup_list = []
    
    # Escape single quotes in values
    name = TEST_SUPPLIER_NAME.replace("'", "''")
    address = TEST_SUPPLIER_ADDRESS.replace("'", "''")
    phone = TEST_SUPPLIER_PHONE.replace("'", "''")
    
    # Check if supplier table exists
    check_query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'supplier'
    );
    """
    
    check_result = execute_query(check_query)
    if check_result['status'] == 'okay' and check_result['result']:
        table_exists = check_result['result'][0]['exists']
        if not table_exists:
            print("Supplier table does not exist, creating it...")
            create_table_query = """
            CREATE TABLE supplier (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                address TEXT,
                phone_number TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_by BIGINT REFERENCES users(id),
                last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_updated_by BIGINT REFERENCES users(id)
            );
            """
            execute_query(create_table_query)
            print("Supplier table created")
    
    # Check if supplier already exists
    check_supplier_query = f"""
    SELECT id FROM supplier WHERE name = '{name}'
    """
    
    check_supplier_result = execute_query(check_supplier_query)
    if check_supplier_result['status'] == 'okay' and check_supplier_result['result']:
        supplier_id = check_supplier_result['result'][0]['id']
        print(f"Test supplier already exists with ID: {supplier_id}")
        cleanup_list.append(('supplier', supplier_id))
        return supplier_id, cleanup_list
    
    # Create a test supplier
    query = f"""
    INSERT INTO supplier (name, address, phone_number, created_by, last_updated_by)
    VALUES ('{name}', '{address}', '{phone}', {user_id or 'NULL'}, {user_id or 'NULL'})
    RETURNING id
    """
    
    try:
        result = execute_query(query, current_user_id=user_id)
        if result['status'] == 'okay' and result['result']:
            supplier_id = result['result'][0]['id']
            print(f"Created test supplier with ID: {supplier_id}")
            cleanup_list.append(('supplier', supplier_id))
            return supplier_id, cleanup_list
        else:
            raise Exception(f"Failed to create test supplier: {result.get('message', 'Unknown error')}")
    except Exception as e:
        # If there's an error (like a unique constraint violation), try to get the existing supplier
        check_supplier_result = execute_query(check_supplier_query)
        if check_supplier_result['status'] == 'okay' and check_supplier_result['result']:
            supplier_id = check_supplier_result['result'][0]['id']
            print(f"Using existing test supplier with ID: {supplier_id}")
            cleanup_list.append(('supplier', supplier_id))
            return supplier_id, cleanup_list
        else:
            # If we can't get the existing supplier, re-raise the exception
            raise e

def update_test_supplier(supplier_id: int, user_id: Optional[int] = None) -> Dict:
    """
    Update a test supplier.
    
    Args:
        supplier_id: The ID of the supplier to update
        user_id: The ID of the user updating the supplier
    
    Returns:
        Dict: The result of the update operation
    """
    # Update the supplier
    update_query = f"""
    UPDATE supplier
    SET name = 'Updated {TEST_SUPPLIER_NAME}', 
        address = 'Updated {TEST_SUPPLIER_ADDRESS}'
    WHERE id = {supplier_id}
    """
    
    update_result = execute_query(update_query, current_user_id=user_id)
    print(f"Update result: {update_result['status']}")
    return update_result

def delete_test_supplier(supplier_id: int, user_id: Optional[int] = None) -> Dict:
    """
    Delete a test supplier.
    
    Args:
        supplier_id: The ID of the supplier to delete
        user_id: The ID of the user deleting the supplier
    
    Returns:
        Dict: The result of the delete operation
    """
    # Delete the supplier
    delete_query = f"""
    DELETE FROM supplier
    WHERE id = {supplier_id}
    """
    
    delete_result = execute_query(delete_query, current_user_id=user_id)
    print(f"Delete result: {delete_result['status']}")
    return delete_result

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

def test_user_management():
    """Test user management functionality with audit trail."""
    print("\n=== Testing User Management with Audit Trail ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        
        # Test authentication
        print("\nTesting authentication...")
        authenticated_user = User.authenticate(TEST_USERNAME, TEST_PASSWORD)
        assert authenticated_user is not None, "Authentication failed"
        print("Authentication successful")
        
        # Test permission checking
        print("\nTesting permission checking...")
        has_read_permission = authenticated_user.has_permission("supplier", "read")
        print(f"Has read permission for supplier: {has_read_permission}")
        
        # Update the user
        print("\nUpdating test user...")
        authenticated_user.full_name = "Updated Test User"
        update_result = authenticated_user.update()
        assert update_result['status'] == 'okay', f"User update failed: {update_result.get('message', 'Unknown error')}"
        print(f"Update result: {update_result}")
        
        # Get the updated user
        print("\nGetting updated user...")
        updated_user = User.get_by_username(TEST_USERNAME)
        assert updated_user is not None, "Failed to retrieve updated user"
        assert updated_user.full_name == "Updated Test User", f"User name was not updated correctly: {updated_user.full_name}"
        print(f"Updated user full name: {updated_user.full_name}")
        
        print("\nUser management tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in user management test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in user management test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_audit_trail_recording():
    """Test audit trail recording functionality."""
    print("\n=== Testing Audit Trail Recording ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test supplier with audit trail
        print("\nCreating a test supplier with audit trail...")
        supplier_id, supplier_cleanup = create_test_supplier(user_id)
        cleanup_list.extend(supplier_cleanup)
        
        # Verify INSERT audit log
        print("\nVerifying INSERT audit log...")
        assert verify_audit_history("supplier", supplier_id, ["INSERT"]), "INSERT audit log not found"
        print("INSERT audit log verified")
        
        # Update the test supplier with audit trail
        print("\nUpdating the test supplier with audit trail...")
        update_result = update_test_supplier(supplier_id, user_id)
        assert update_result['status'] == 'okay', f"Supplier update failed: {update_result.get('message', 'Unknown error')}"
        
        # Verify UPDATE audit log
        print("\nVerifying UPDATE audit log...")
        assert verify_audit_history("supplier", supplier_id, ["INSERT", "UPDATE"]), "UPDATE audit log not found"
        print("UPDATE audit log verified")
        
        # Delete the test supplier with audit trail
        print("\nDeleting the test supplier with audit trail...")
        delete_result = delete_test_supplier(supplier_id, user_id)
        assert delete_result['status'] == 'okay', f"Supplier delete failed: {delete_result.get('message', 'Unknown error')}"
        
        # Verify DELETE audit log
        print("\nVerifying DELETE audit log...")
        assert verify_audit_history("supplier", supplier_id, ["INSERT", "UPDATE", "DELETE"]), "DELETE audit log not found"
        print("DELETE audit log verified")
        
        print("\nAudit trail recording tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in audit trail recording test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in audit trail recording test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_audit_trail_retrieval():
    """Test audit trail retrieval functionality."""
    print("\n=== Testing Audit Trail Retrieval ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test supplier with audit trail
        print("\nCreating a test supplier with audit trail...")
        supplier_id, supplier_cleanup = create_test_supplier(user_id)
        cleanup_list.extend(supplier_cleanup)
        
        # Update the test supplier with audit trail
        print("\nUpdating the test supplier with audit trail...")
        update_result = update_test_supplier(supplier_id, user_id)
        
        # Test get_audit_history
        print("\nTesting get_audit_history...")
        history_result = get_audit_history("supplier", supplier_id)
        assert history_result['status'] == 'okay', f"Failed to get audit history: {history_result.get('message', 'Unknown error')}"
        assert len(history_result['history']) >= 2, f"Expected at least 2 audit log entries, got {len(history_result['history'])}"
        print(f"Found {len(history_result['history'])} audit log entries")
        
        # Test search_audit_logs by table name
        print("\nTesting search_audit_logs by table name...")
        search_result = search_audit_logs(table_name="supplier")
        assert search_result['status'] == 'okay', f"Failed to search audit logs: {search_result.get('message', 'Unknown error')}"
        assert len(search_result['logs']) > 0, "No audit logs found"
        print(f"Found {len(search_result['logs'])} audit log entries")
        
        # Test search_audit_logs by user ID
        print("\nTesting search_audit_logs by user ID...")
        search_result = search_audit_logs(user_id=user_id)
        assert search_result['status'] == 'okay', f"Failed to search audit logs: {search_result.get('message', 'Unknown error')}"
        assert len(search_result['logs']) > 0, "No audit logs found"
        print(f"Found {len(search_result['logs'])} audit log entries")
        
        # Test search_audit_logs by action
        print("\nTesting search_audit_logs by action...")
        search_result = search_audit_logs(action="UPDATE")
        assert search_result['status'] == 'okay', f"Failed to search audit logs: {search_result.get('message', 'Unknown error')}"
        assert len(search_result['logs']) > 0, "No audit logs found"
        print(f"Found {len(search_result['logs'])} audit log entries")
        
        print("\nAudit trail retrieval tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in audit trail retrieval test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in audit trail retrieval test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_audit_trail_changes():
    """Test audit trail changes functionality."""
    print("\n=== Testing Audit Trail Changes ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Create a test supplier with audit trail
        print("\nCreating a test supplier with audit trail...")
        supplier_id, supplier_cleanup = create_test_supplier(user_id)
        cleanup_list.extend(supplier_cleanup)
        
        # Update the test supplier with audit trail
        print("\nUpdating the test supplier with audit trail...")
        update_result = update_test_supplier(supplier_id, user_id)
        
        # Get the audit history
        history_result = get_audit_history("supplier", supplier_id)
        assert history_result['status'] == 'okay', f"Failed to get audit history: {history_result.get('message', 'Unknown error')}"
        
        # Find the UPDATE entry
        update_entry = None
        for entry in history_result['history']:
            if entry['action'] == 'UPDATE':
                update_entry = entry
                break
        
        assert update_entry is not None, "UPDATE entry not found in audit history"
        
        # Verify changes
        changes = update_entry.get('changes')
        assert changes is not None, "No changes found in UPDATE entry"
        
        # Parse the changes JSON if it's a string
        if isinstance(changes, str):
            changes = json.loads(changes)
        
        print("\nVerifying changes in UPDATE entry...")
        assert 'name' in changes, "Name change not found in changes"
        assert 'address' in changes, "Address change not found in changes"
        
        print(f"Changes: {json.dumps(changes, indent=2)}")
        
        # Test compare_changes function
        print("\nTesting compare_changes function...")
        old_data = {
            'name': TEST_SUPPLIER_NAME,
            'address': TEST_SUPPLIER_ADDRESS,
            'phone_number': TEST_SUPPLIER_PHONE
        }
        
        new_data = {
            'name': f'Updated {TEST_SUPPLIER_NAME}',
            'address': f'Updated {TEST_SUPPLIER_ADDRESS}',
            'phone_number': TEST_SUPPLIER_PHONE
        }
        
        comparison = compare_changes(old_data, new_data)
        assert 'name' in comparison, "Name change not found in comparison"
        assert 'address' in comparison, "Address change not found in comparison"
        assert 'phone_number' not in comparison, "Phone number should not be in comparison"
        
        print(f"Comparison: {json.dumps(comparison, indent=2)}")
        
        print("\nAudit trail changes tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in audit trail changes test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in audit trail changes test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def test_manual_audit_log():
    """Test manual audit log recording."""
    print("\n=== Testing Manual Audit Log Recording ===")
    
    cleanup_list = []
    
    try:
        # Create a test user
        test_user, user_cleanup = create_test_user()
        cleanup_list.extend(user_cleanup)
        user_id = test_user.id
        
        # Manually record an audit log
        print("\nManually recording an audit log...")
        changes = {
            'field1': 'value1',
            'field2': 'value2'
        }
        
        record_result = record_audit_log(
            user_id=user_id,
            table_name="test_table",
            record_id=12345,
            action="INSERT",
            changes=changes
        )
        
        assert record_result['status'] == 'okay', f"Failed to record audit log: {record_result.get('message', 'Unknown error')}"
        audit_log_id = record_result.get('id')
        assert audit_log_id is not None, "No audit log ID returned"
        cleanup_list.append(('audit_log', audit_log_id))
        print(f"Recorded audit log with ID: {audit_log_id}")
        
        # Search for the manually recorded audit log
        print("\nSearching for the manually recorded audit log...")
        search_result = search_audit_logs(table_name="test_table")
        assert search_result['status'] == 'okay', f"Failed to search audit logs: {search_result.get('message', 'Unknown error')}"
        assert len(search_result['logs']) > 0, "No audit logs found"
        
        # Verify the manually recorded audit log
        found = False
        for log in search_result['logs']:
            if log['id'] == audit_log_id:
                found = True
                assert log['table_name'] == "test_table", f"Expected table_name 'test_table', got '{log['table_name']}'"
                assert log['record_id'] == 12345, f"Expected record_id 12345, got {log['record_id']}"
                assert log['action'] == "INSERT", f"Expected action 'INSERT', got '{log['action']}'"
                
                # Parse the changes JSON if it's a string
                log_changes = log['changes']
                if isinstance(log_changes, str):
                    log_changes = json.loads(log_changes)
                
                assert log_changes.get('field1') == 'value1', f"Expected field1 'value1', got '{log_changes.get('field1')}'"
                assert log_changes.get('field2') == 'value2', f"Expected field2 'value2', got '{log_changes.get('field2')}'"
                break
        
        assert found, f"Manually recorded audit log with ID {audit_log_id} not found in search results"
        print("Manually recorded audit log verified")
        
        print("\nManual audit log tests passed")
        return True
    except AssertionError as e:
        print(f"Assertion error in manual audit log test: {str(e)}")
        return False
    except Exception as e:
        print(f"Error in manual audit log test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup(cleanup_list)

def run_all_tests():
    """Run all audit trail tests."""
    print("=== Running All Audit Trail Tests ===")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the tests
    tests = [
        ("User Management", test_user_management),
        ("Audit Trail Recording", test_audit_trail_recording),
        ("Audit Trail Retrieval", test_audit_trail_retrieval),
        ("Audit Trail Changes", test_audit_trail_changes),
        ("Manual Audit Log", test_manual_audit_log)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n\n=== Running {test_name} Test ===")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"Error running {test_name} test: {str(e)}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Print summary
    print("\n\n=== Test Summary ===")
    all_passed = True
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed. See above for details.")
    
    return all_passed

if __name__ == "__main__":
    print("Testing Audit Trail and User Management System")
    print("=============================================")
    
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
