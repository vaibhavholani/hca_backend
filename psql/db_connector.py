import psycopg2
from psycopg2.extras import RealDictCursor
import os
import re
from typing import Tuple, Dict, Optional, Any
from dotenv import load_dotenv
from Exceptions import DataError
from .remote_connector import execute_remote_query
from Multiprocessing import exec_in_available_thread
load_dotenv()

def connect():
    """
    Provides a reference to the database and its cursor
    """
    mydb = psycopg2.connect(dbname=os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'))
    return mydb

def cursor(dict=False) -> Tuple:
    """
    return the cursor and db connection
    """
    database = connect()
    if dict:
        db_cursor = database.cursor(cursor_factory=RealDictCursor)
    else:
        db_cursor = database.cursor()
    return (database, db_cursor)

def execute_query(query: str, dictCursor: bool=True, exec_remote: bool=True, current_user_id: Optional[int]=None, **kwargs):
    """
    Executes a query and returns the result.
    
    Args:
        query: The SQL query to execute
        dictCursor: Whether to use a dictionary cursor
        exec_remote: Whether to execute the query remotely
        current_user_id: The ID of the current user (for audit trail)
        **kwargs: Additional keyword arguments
        
    Returns:
        Dict: The result of the query execution
    """
    query_type = query.strip().split()[0].upper()
    if query_type == 'WITH':
        query_type = 'SELECT'
    if query_type not in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']:
        raise DataError('Invalid query type')
    
    try:
        (db, cur) = cursor(dictCursor)
        
        # Execute the query
        cur.execute(query)
        
        # Handle non-SELECT queries
        if query_type != 'SELECT':
            if exec_remote and os.getenv('QUERY_REMOTE') == 'true':
                exec_in_available_thread(execute_remote_query, query)
            
            # Record audit log for INSERT, UPDATE, DELETE
            if query_type in ['INSERT', 'UPDATE', 'DELETE'] and current_user_id is not None:
                try:
                    # Only import here to avoid circular imports
                    from API_Database.audit_log import record_audit_log
                    
                    # Extract table name and record ID
                    table_name, record_id, changes = extract_audit_info(query_type, query, cur)
                    
                    if table_name and record_id:
                        # Record the audit log
                        record_audit_log(
                            user_id=current_user_id,
                            table_name=table_name,
                            record_id=record_id,
                            action=query_type,
                            changes=changes
                        )
                except Exception as audit_error:
                    # Log the error but don't fail the transaction
                    print(f"Error recording audit log: {audit_error}")
            
            db.commit()
            result = []
        else:
            result = cur.fetchall()
        
        db.close()
        return {'result': result, 'status': 'okay', 'message': 'Query executed successfully!'}
    except Exception as e:
        print('Error executing query:', e)
        raise DataError({'status': 'error', 'message': f'Error with Query Execution: {e}'})

def extract_audit_info(query_type: str, query: str, cursor) -> Tuple[Optional[str], Optional[int], Optional[Dict[str, Any]]]:
    """
    Extract audit information from a query.
    
    Args:
        query_type: The type of query (INSERT, UPDATE, DELETE)
        query: The SQL query
        cursor: The database cursor
        
    Returns:
        Tuple: (table_name, record_id, changes)
    """
    table_name = None
    record_id = None
    changes = None
    
    try:
        if query_type == 'INSERT':
            # Extract table name from INSERT query
            match = re.search(r'INSERT\s+INTO\s+([^\s\(]+)', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                
                # Get the ID of the inserted record
                if cursor.rowcount > 0:
                    # Try to get the ID from RETURNING clause
                    returning_match = re.search(r'RETURNING\s+id', query, re.IGNORECASE)
                    if returning_match and cursor.description:
                        for i, col in enumerate(cursor.description):
                            if col.name == 'id':
                                record_id = cursor.fetchone()[i]
                                break
                    
                    # If we couldn't get the ID, use currval
                    if record_id is None:
                        # Get the sequence name for this table
                        seq_query = f"SELECT pg_get_serial_sequence('{table_name}', 'id')"
                        cursor.execute(seq_query)
                        seq_name = cursor.fetchone()[0]
                        
                        if seq_name:
                            # Get the last value from the sequence
                            cursor.execute(f"SELECT currval('{seq_name}')")
                            record_id = cursor.fetchone()[0]
                
                # Extract values from INSERT query for changes
                # This is a simplified approach and might not work for all INSERT queries
                values_match = re.search(r'VALUES\s*\((.+)\)', query, re.IGNORECASE)
                if values_match:
                    values = values_match.group(1).split(',')
                    columns_match = re.search(r'INSERT\s+INTO\s+[^\s\(]+\s*\((.+)\)', query, re.IGNORECASE)
                    
                    if columns_match:
                        columns = [c.strip() for c in columns_match.group(1).split(',')]
                        changes = {}
                        
                        for i, col in enumerate(columns):
                            if i < len(values):
                                changes[col] = values[i].strip()
        
        elif query_type == 'UPDATE':
            # Extract table name from UPDATE query
            match = re.search(r'UPDATE\s+([^\s]+)', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                
                # Extract record ID from WHERE clause
                id_match = re.search(r'WHERE\s+.*\bid\s*=\s*(\d+)', query, re.IGNORECASE)
                if id_match:
                    record_id = int(id_match.group(1))
                
                # Extract SET clause for changes
                set_match = re.search(r'SET\s+(.+?)\s+WHERE', query, re.IGNORECASE)
                if set_match:
                    set_clause = set_match.group(1)
                    changes = {}
                    
                    # Split by commas, but handle quoted values
                    assignments = []
                    current = ""
                    in_quotes = False
                    
                    for char in set_clause:
                        if char == "'" and (len(current) == 0 or current[-1] != '\\'):
                            in_quotes = not in_quotes
                        
                        if char == ',' and not in_quotes:
                            assignments.append(current.strip())
                            current = ""
                        else:
                            current += char
                    
                    if current:
                        assignments.append(current.strip())
                    
                    for assignment in assignments:
                        parts = assignment.split('=', 1)
                        if len(parts) == 2:
                            col = parts[0].strip()
                            val = parts[1].strip()
                            changes[col] = val
        
        elif query_type == 'DELETE':
            # Extract table name from DELETE query
            match = re.search(r'DELETE\s+FROM\s+([^\s]+)', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                
                # Extract record ID from WHERE clause
                id_match = re.search(r'WHERE\s+.*\bid\s*=\s*(\d+)', query, re.IGNORECASE)
                if id_match:
                    record_id = int(id_match.group(1))
    
    except Exception as e:
        print(f"Error extracting audit info: {e}")
    
    return table_name, record_id, changes

def update():
    """Performs an update operation on the database; placeholder implementation."""
    pass

def add_stack_val(a, b):
    """Returns the sum of two values; placeholder implementation."""
    pass

def add_stack_val_multiple(a, b):
    """Returns the sum of two values; placeholder implementation."""
    pass

def add_stack(dfas):
    """Adds a stack of values; placeholder implementation."""
    pass
