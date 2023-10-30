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


def get_all_khata_data_by_date(start_date: str, end_date: str):

    # Query 1: DROP VIEW IF EXISTS khata_data_view
    query_1 = "DROP VIEW IF EXISTS khata_data_view;"

    # Query 2: CREATE OR REPLACE VIEW khata_data_view
    query_2 = """
    CREATE OR REPLACE VIEW khata_data_view AS
    SELECT
        re.supplier_id,
        re.party_id,
        re.bill_number AS bill_no,
        TO_CHAR(re.register_date, 'DD/MM/YYYY') AS bill_date,
        re.amount::integer AS bill_amt,
        re.status AS bill_status
    FROM
        register_entry re
    JOIN
        supplier s ON re.supplier_id = s.id
    JOIN
        party p ON re.party_id = p.id
    WHERE
        re.register_date >= '{}' AND re.register_date <= '{}'
    ORDER BY
        s.name, p.name, re.register_date, re.bill_number;
    """.format(start_date, end_date)

    # Query 3: SELECT from khata_data_view with LEFT JOINs
    query_3 = """
    SELECT
        khata_data_view.supplier_id,
        khata_data_view.party_id,
        khata_data_view.bill_no,
        khata_data_view.bill_date,
        khata_data_view.bill_amt,
        khata_data_view.bill_status,
        memo_entry.memo_number AS memo_no,
        memo_bills.amount AS memo_amt,
        TO_CHAR(memo_entry.register_date, 'DD/MM/YYYY') AS memo_date,
        memo_entry.amount AS chk_amt,
        memo_bills.type AS memo_type
    FROM
        khata_data_view
    LEFT JOIN
        memo_bills ON khata_data_view.bill_no = memo_bills.bill_number
    LEFT JOIN
        memo_entry ON memo_bills.memo_id = memo_entry.id AND memo_entry.supplier_id = khata_data_view.supplier_id AND memo_entry.party_id = khata_data_view.party_id
    ORDER BY
        khata_data_view.party_id, khata_data_view.supplier_id, khata_data_view.bill_date, khata_data_view.bill_no, memo_entry.memo_number;
    """

    # Execute Query 1: DROP VIEW
    execute_query(query_1)
    # Execute Query 2: CREATE OR REPLACE VIEW
    execute_query(query_2)
    # Execute Query 3: SELECT with JOINs
    result = execute_query(query_3)
    
    result = result["result"]
    return result