from __future__ import annotations
from typing import Dict
from psql import db_connector
from Individual import Supplier, Party, Bank, Transporter

def add_individual(obj):
    entity_mapping = {
        "supplier": Supplier,
        "party": Party,
        "bank": Bank,
        "transport": Transporter,
    }
    table_name = obj["entity"]
    base_class = entity_mapping.get(table_name)
    if base_class:
        cls = base_class.create_individual(obj)
        table = table_name
        return insert_entity(cls, table)
    return {"status": "error", "message": f"{base_class} could not be added. Invalid entity type. Please contact Vaibhav"}


def insert_entity(entity, table):
    # Open a new connection
    db, cursor = db_connector.cursor()

    sql = f"INSERT INTO {table} (name, address) VALUES (%s, %s)"
    val = (entity.name, entity.address)
    try: 
        cursor.execute(sql, val)
        db_connector.add_stack_val(sql, val)
        db.commit()
        db.close()
        db_connector.update()
        return {"status": "okay", "message": f"{table} added successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error: {e}"}
