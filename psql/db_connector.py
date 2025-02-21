import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Tuple
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

def execute_query(query: str, dictCursor: bool=True, exec_remote: bool=True, **kwargs):
    """
    Executes a query and returns the result.
    """
    query_type = query.strip().split()[0].upper()
    if query_type == 'WITH':
        query_type = 'SELECT'
    if query_type not in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']:
        raise DataError('Invalid query type')
    try:
        (db, cur) = cursor(dictCursor)
        cur.execute(query)
        if query_type != 'SELECT':
            if exec_remote and os.getenv('QUERY_REMOTE') == 'true':
                exec_in_available_thread(execute_remote_query, query)
            db.commit()
            result = []
        else:
            result = cur.fetchall()
        db.close()
        return {'result': result, 'status': 'okay', 'message': 'Query executed successfully!'}
    except Exception as e:
        print('Error executing query:', e)
        raise DataError({'status': 'error', 'message': f'Error with Query Execution: {e}'})

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