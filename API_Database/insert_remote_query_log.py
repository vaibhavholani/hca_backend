from typing import Dict
from psql import execute_query
from pypika import Query, Table


def insert_remote_query_log(query_text: str, http_response_status: str, query_status: str, message: str) -> Dict:
    """Insert a remote query log into the database."""

    # Define the table
    remote_query_logs_table = Table('remote_query_logs')

    # Build the INSERT query using Pypika
    insert_query = Query.into(remote_query_logs_table).columns(
        'query_text',
        'http_response_status',
        'query_status',
        'message'
    ).insert(
        query_text,
        http_response_status,
        query_status,
        message
    ).get_sql()

    # Execute the query
    response = execute_query(insert_query, exec_remote=False)
    return response
