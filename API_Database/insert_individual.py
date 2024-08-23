from __future__ import annotations
from typing import Dict
from psql import execute_query
# from Individual import Supplier, Party, Bank, Transporter

# def add_individual(obj):
#     entity_mapping = {
#         "supplier": Supplier,
#         "party": Party,
#         "bank": Bank,
#         "transport": Transporter,
#     }
#     table_name = obj["entity"]
#     base_class = entity_mapping.get(table_name)
#     if base_class:
#         cls = base_class.create_individual(obj)
#         table = table_name
#         return insert_individual(cls, table)
#     return {"status": "error", "message": f"{base_class} could not be added. Invalid entity type. Please contact Vaibhav"}


def insert_individual(entity, table):
    # Open a new connection
    
    # Base columns and values
    columns = ['name', 'address']
    values = [f"'{entity.name}'", f"'{entity.address}'"]
    
    # Add phone_number column and value if it's not None
    if entity.phone_number is not None:
        columns.append('phone_number')
        values.append(f"'{entity.phone_number}'")
    
    columns_str = ', '.join(columns)
    values_str = ', '.join(values)

    sql = f"INSERT INTO {table} ({columns_str}) VALUES ({values_str})"
    return execute_query(sql)
