from psql import db_connector, execute_query
from .retrieve_register_entry import get_all_register_entries
from .retrieve_memo_entry import get_all_memo_entries
from .retrieve_order_form import get_all_order_forms
from .retrieve_item import get_all_items
from .retrieve_item_entry import get_all_item_entries

def get_all(table_name: str, **kwargs): 
    
    if table_name == "memo_entry":
        data = get_all_memo_entries(**kwargs)
    elif table_name == "register_entry":
        data = get_all_register_entries(**kwargs)
    elif table_name == "order_form":
        data = get_all_order_forms(**kwargs)
    elif table_name == "item":
        data = get_all_items(**kwargs)
    elif table_name == "item_entry":
        data = get_all_item_entries(**kwargs)
    else: 
        data = get_all_individual(table_name)
    
    return data

def get_all_individual(table_name: str): 
    
    sql = f"select * from {table_name}"
    data = execute_query(sql)
    return data["result"]
