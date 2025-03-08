#!/usr/bin/env python
"""
Test script for the audit trail and user management system.
"""
import os
import json
from dotenv import load_dotenv
from Individual.User import User
from API_Database.audit_log import record_audit_log, get_audit_history, search_audit_logs
from psql import execute_query

load_dotenv()

def test_user_management():
    """Test user management functionality."""
    print("\n=== Testing User Management ===")
    
    # Create a test user
    print("\nCreating test user...")
    try:
        test_user = User.create(
            username="test_user",
            password="test_password",
            role="user",
            full_name="Test User",
            email="test@example.com"
        )
        print(f"Created test user with ID: {test_user.id}")
    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        # Check if user already exists
        test_user = User.get_by_username("test_user")
        if test_user:
            print(f"Test user already exists with ID: {test_user.id}")
        else:
            print("Failed to create or retrieve test user")
            return
    
    # Test authentication
    print("\nTesting authentication...")
    authenticated_user = User.authenticate("test_user", "test_password")
    if authenticated_user:
        print("Authentication successful")
    else:
        print("Authentication failed")
        return
    
    # Test permission checking
    print("\nTesting permission checking...")
    has_read_permission = authenticated_user.has_permission("supplier", "read")
    print(f"Has read permission for supplier: {has_read_permission}")
    
    has_create_permission = authenticated_user.has_permission("supplier", "create")
    print(f"Has create permission for supplier: {has_create_permission}")
    
    # Update the user
    print("\nUpdating test user...")
    authenticated_user.full_name = "Updated Test User"
    update_result = authenticated_user.update()
    print(f"Update result: {update_result}")
    
    # Get the updated user
    print("\nGetting updated user...")
    updated_user = User.get_by_username("test_user")
    print(f"Updated user full name: {updated_user.full_name}")
    
    # Clean up (deactivate the user instead of deleting)
    print("\nDeactivating test user...")
    updated_user.is_active = False
    deactivate_result = updated_user.update()
    print(f"Deactivation result: {deactivate_result}")

def test_audit_trail():
    """Test audit trail functionality."""
    print("\n=== Testing Audit Trail ===")
    
    # Get admin user for testing
    admin_user = User.get_by_username("admin")
    if not admin_user:
        print("Admin user not found, creating a test record without user ID")
        user_id = None
    else:
        user_id = admin_user.id
        print(f"Using admin user with ID: {user_id}")
    
    # Create a test record
    print("\nCreating a test record...")
    query = """
    INSERT INTO supplier (name, address, created_by, last_updated_by)
    VALUES ('Test Supplier', 'Test Address', 1, 1)
    RETURNING id
    """
    
    try:
        result = execute_query(query, current_user_id=user_id)
        if result['status'] == 'okay' and result['result']:
            record_id = result['result'][0]['id']
            print(f"Created test record with ID: {record_id}")
        else:
            print("Failed to create test record")
            return
    except Exception as e:
        print(f"Error creating test record: {str(e)}")
        return
    
    # Update the test record
    print("\nUpdating the test record...")
    update_query = f"""
    UPDATE supplier
    SET name = 'Updated Test Supplier', address = 'Updated Test Address'
    WHERE id = {record_id}
    """
    
    try:
        update_result = execute_query(update_query, current_user_id=user_id)
        print(f"Update result: {update_result['status']}")
    except Exception as e:
        print(f"Error updating test record: {str(e)}")
    
    # Get the audit history for the test record
    print("\nGetting audit history for the test record...")
    try:
        history_result = get_audit_history("supplier", record_id)
        print(f"Audit history status: {history_result['status']}")
        if history_result['status'] == 'okay' and history_result['history']:
            print(f"Found {len(history_result['history'])} audit log entries")
            for entry in history_result['history']:
                print(f"  - {entry['action']} at {entry['timestamp']} by {entry.get('username', 'Unknown')}")
                if entry.get('changes'):
                    print(f"    Changes: {json.dumps(entry['changes'], indent=2)}")
        else:
            print("No audit history found")
    except Exception as e:
        print(f"Error getting audit history: {str(e)}")
    
    # Search audit logs
    print("\nSearching audit logs...")
    try:
        search_result = search_audit_logs(table_name="supplier")
        print(f"Search result status: {search_result['status']}")
        if search_result['status'] == 'okay' and search_result['logs']:
            print(f"Found {len(search_result['logs'])} audit log entries")
            for entry in search_result['logs'][:3]:  # Show only the first 3 entries
                print(f"  - {entry['action']} on {entry['table_name']}/{entry['record_id']} at {entry['timestamp']} by {entry.get('username', 'Unknown')}")
        else:
            print("No audit logs found")
    except Exception as e:
        print(f"Error searching audit logs: {str(e)}")
    
    # Clean up (delete the test record)
    print("\nCleaning up (deleting the test record)...")
    delete_query = f"""
    DELETE FROM supplier
    WHERE id = {record_id}
    """
    
    try:
        delete_result = execute_query(delete_query, current_user_id=user_id)
        print(f"Delete result: {delete_result['status']}")
    except Exception as e:
        print(f"Error deleting test record: {str(e)}")

if __name__ == "__main__":
    print("Testing Audit Trail and User Management System")
    print("=============================================")
    
    # Run the tests
    test_user_management()
    test_audit_trail()
    
    print("\nTests completed!")
