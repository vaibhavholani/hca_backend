from __future__ import annotations
from typing import Dict
from psql import db_connector
from Individual import Supplier, Party, Bank, Transporter

def add_individual(entity_type, obj):
    entity_mapping = {
        "supplier": Supplier.create_supplier,
        "party": Party.create_party,
        "bank": Bank.create_bank,
        "transporter": Transporter.create_transporter,
    }

    create_entity = entity_mapping.get(entity_type)
    if create_entity:
        entity = create_entity(obj)
        table = entity_type
        return insert_entity(entity, table)
    return {"status": "error", "error": f"{table} could not be added. Invalid entity type. Please contact Vaibhav"}


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
        return {"status": "okay"}
    except Exception as e:
        return {"status": "error", "error": f"{table} could not be added. Please contact Vaibhav."}
