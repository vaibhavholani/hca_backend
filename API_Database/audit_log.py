"""
Functions for recording and retrieving audit logs.
"""
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime
from psql import execute_query

def record_audit_log(
    user_id: Optional[int],
    table_name: str,
    record_id: int,
    action: str,
    changes: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Record an audit log entry.
    
    Args:
        user_id: The ID of the user performing the action (can be None for system actions)
        table_name: The name of the table being modified
        record_id: The ID of the record being modified
        action: The action being performed (INSERT, UPDATE, DELETE)
        changes: A dictionary of changes (for UPDATE) or the full record (for INSERT/DELETE)
        
    Returns:
        Dict: The result of the operation
    """
    # Safety check: prevent audit logging for the audit_log table itself to avoid infinite loops
    if table_name.lower() == 'audit_log':
        return {
            'status': 'skipped',
            'message': 'Skipped audit logging for audit_log table to prevent infinite loops'
        }
    # Validate action
    if action not in ['INSERT', 'UPDATE', 'DELETE']:
        return {
            'status': 'error',
            'message': f'Invalid action: {action}'
        }
    
    # Convert changes to JSON
    changes_json = 'NULL'
    if changes:
        # Convert any datetime objects to strings
        changes_str = {}
        for key, value in changes.items():
            if isinstance(value, datetime):
                changes_str[key] = value.isoformat()
            else:
                changes_str[key] = value
        
        # Escape single quotes in JSON string
        json_string = json.dumps(changes_str)
        json_string_escaped = json_string.replace("'", "''")
        changes_json = f"'{json_string_escaped}'"
    
    # Escape table name and action to prevent SQL injection
    table_name_escaped = table_name.replace("'", "''")
    action_escaped = action.replace("'", "''")
    
    # Build the query
    user_id_str = 'NULL' if user_id is None else str(user_id)
    
    query = f"""
    INSERT INTO audit_log (
        user_id, table_name, record_id, action, changes
    )
    VALUES (
        {user_id_str}, '{table_name_escaped}', {record_id}, '{action_escaped}', {changes_json}
    )
    RETURNING id
    """
    
    try:
        result = execute_query(query, exec_remote=False)
        if result['status'] == 'okay' and result['result']:
            return {
                'status': 'okay',
                'message': 'Audit log recorded successfully',
                'id': result['result'][0]['id']
            }
        return {
            'status': 'error',
            'message': 'Failed to record audit log'
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'status': 'error',
            'message': f'Error recording audit log: {str(e)}'
        }

def get_audit_history(
    table_name: str,
    record_id: int,
    limit: int = 100,
    offset: int = 0
) -> Dict:
    """
    Get the audit history for a record.
    
    Args:
        table_name: The name of the table
        record_id: The ID of the record
        limit: The maximum number of records to return
        offset: The number of records to skip
        
    Returns:
        Dict: The audit history
    """
    query = f"""
    SELECT a.id, a.action, a.timestamp, a.changes,
           u.username, u.full_name
    FROM audit_log a
    LEFT JOIN users u ON a.user_id = u.id
    WHERE a.table_name = '{table_name}' AND a.record_id = {record_id}
    ORDER BY a.timestamp DESC
    LIMIT {limit} OFFSET {offset}
    """
    
    try:
        result = execute_query(query)
        if result['status'] == 'okay':
            return {
                'status': 'okay',
                'history': result['result']
            }
        return {
            'status': 'error',
            'message': 'Failed to retrieve audit history'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error retrieving audit history: {str(e)}'
        }

def search_audit_logs(
    user_id: Optional[int] = None,
    table_name: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict:
    """
    Search audit logs with various filters.
    
    Args:
        user_id: Filter by user ID
        table_name: Filter by table name
        action: Filter by action (INSERT, UPDATE, DELETE)
        start_date: Filter by start date (YYYY-MM-DD)
        end_date: Filter by end date (YYYY-MM-DD)
        limit: The maximum number of records to return
        offset: The number of records to skip
        
    Returns:
        Dict: The search results
    """
    # Build the WHERE clause
    where_clauses = []
    
    if user_id is not None:
        where_clauses.append(f"a.user_id = {user_id}")
    
    if table_name:
        where_clauses.append(f"a.table_name = '{table_name}'")
    
    if action:
        if action not in ['INSERT', 'UPDATE', 'DELETE']:
            return {
                'status': 'error',
                'message': f'Invalid action: {action}'
            }
        where_clauses.append(f"a.action = '{action}'")
    
    if start_date:
        where_clauses.append(f"a.timestamp >= '{start_date} 00:00:00'")
    
    if end_date:
        where_clauses.append(f"a.timestamp <= '{end_date} 23:59:59'")
    
    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Build the query
    query = f"""
    SELECT a.id, a.table_name, a.record_id, a.action, a.timestamp, a.changes,
           u.username, u.full_name
    FROM audit_log a
    LEFT JOIN users u ON a.user_id = u.id
    WHERE {where_clause}
    ORDER BY a.timestamp DESC
    LIMIT {limit} OFFSET {offset}
    """
    
    # Get the total count
    count_query = f"""
    SELECT COUNT(*) as total
    FROM audit_log a
    WHERE {where_clause}
    """
    
    try:
        result = execute_query(query)
        count_result = execute_query(count_query)
        
        if result['status'] == 'okay' and count_result['status'] == 'okay':
            return {
                'status': 'okay',
                'logs': result['result'],
                'total': count_result['result'][0]['total'],
                'limit': limit,
                'offset': offset
            }
        return {
            'status': 'error',
            'message': 'Failed to search audit logs'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error searching audit logs: {str(e)}'
        }

def compare_changes(old_data: Dict, new_data: Dict) -> Dict:
    """
    Compare old and new data to generate a changes dictionary.
    
    Args:
        old_data: The old data
        new_data: The new data
        
    Returns:
        Dict: A dictionary of changes with old and new values
    """
    changes = {}
    
    # Find all keys in either dictionary
    all_keys = set(old_data.keys()) | set(new_data.keys())
    
    for key in all_keys:
        old_value = old_data.get(key)
        new_value = new_data.get(key)
        
        # Skip if the values are the same
        if old_value == new_value:
            continue
        
        # Add to changes
        changes[key] = {
            'old': old_value,
            'new': new_value
        }
    
    return changes
