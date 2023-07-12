from psql import db_connector

def get_all(table_name: str): 

    if table_name == "memo_entry":
        data = get_all_memo_entry()
    elif table_name == "register_entry":
        data = get_all_register_entry()
    else: 
        data = get_all_individual(table_name)
    
    return data

def get_all_individual(table_name: str): 
    
    db, cursor = db_connector.cursor(True)

    sql = f"select id, name, address from {table_name}"

    cursor.execute(sql)
    return cursor.fetchall()

def get_all_memo_entry():
    
    db, cursor = db_connector.cursor(True)

    sql = f"select id, memo_number, supplier_id, party_id, to_char(register_date, 'DD/MM/YYYY') as register_date,floor(amount)::integer as amount from memo_entry"

    cursor.execute(sql)
    return cursor.fetchall()

def get_all_register_entry():
    
    db, cursor = db_connector.cursor(True)

    sql = f"select id, supplier_id, party_id, to_char(register_date, 'DD/MM/YYYY') as register_date,floor(amount)::integer as amount, floor(partial_amount)::integer as partial_amount, gr_amount, bill_number, status, deduction from register_entry"

    cursor.execute(sql)
    return cursor.fetchall()