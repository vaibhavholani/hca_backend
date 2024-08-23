from typing import Dict
from psql import execute_query

def update_individual(entity) -> Dict:
    # Check if the entity exists in the database
    entity_id = entity.get_id()

    # Construct the update SQL statement
    update_fields = [f"name='{entity.name}'", f"address='{entity.address}'"]
    if entity.phone_number:
        update_fields.append(f"phone_number='{entity.phone_number}'")

    update_str = ', '.join(update_fields)

    sql = f"UPDATE {entity.table_name} SET {update_str} WHERE id={entity_id}"
    return execute_query(sql)