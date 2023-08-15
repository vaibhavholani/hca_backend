from Entities import RegisterEntry, MemoEntry, OrderForm
from Individual import Supplier, Party, Bank, Transporter
from Exceptions import DataError

def table_class_mapper(table_name: str):
    entity_mapping = {
        "supplier": Supplier,
        "party": Party,
        "bank": Bank,
        "transport": Transporter,
        "register_entry": RegisterEntry,
        "memo_entry": MemoEntry, 
        "order_form": OrderForm
    }     
    if table_name not in entity_mapping:
        raise DataError("Table name not found in entity mapping")
    
    return entity_mapping[table_name]