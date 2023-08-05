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

    sql = f"INSERT INTO {table} (name, address) VALUES ('{entity.name}', '{entity.address}')"
    return execute_query(sql)