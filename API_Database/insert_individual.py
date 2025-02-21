from __future__ import annotations
from typing import Dict
from psql import execute_query

def insert_individual(entity, table):
    """Inserts an individual entity into the specified table and returns the insertion status."""

    def remove_single_quotes(value):
        """Removes single quotes from a string to avoid SQL injection issues."""
        return value.replace("'", '')
    columns = ['name', 'address']
    values = [f"'{remove_single_quotes(entity.name)}'", f"'{remove_single_quotes(entity.address)}'"]
    if entity.phone_number is not None:
        columns.append('phone_number')
        values.append(f"'{entity.phone_number}'")
    columns_str = ', '.join(columns)
    values_str = ', '.join(values)
    sql = f'INSERT INTO {table} ({columns_str}) VALUES ({values_str})'
    return execute_query(sql)