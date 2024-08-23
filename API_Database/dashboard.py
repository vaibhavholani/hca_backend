from __future__ import annotations
import sys
sys.path.append("../")
from psql import db_connector
import datetime
import pandas as pd
from typing import List, Tuple



def get_sales(start_date: datetime, end_date: datetime):

    db, cursor = db_connector.cursor(True)

    sql = f"select SUM(amount) as sales from memo_entry where register_date >= '{start_date}' AND register_date <= '{end_date}';"

    cursor.execute(sql)
    data = cursor.fetchall()

    return data


def get_top_individuals(start_date: datetime, end_date: datetime, table_name: str, n: int, property: str):

    table_names = {"supplier": "supplier_id", "party": "party_id"}

    db, cursor = db_connector.cursor(True)

    entity = table_names[table_name]

    sql = f"select {entity}, SUM({property}) as {property} from register_entry where \
    register_date >= '{start_date}' AND register_date <= '{end_date}' \
    group by {entity} ORDER BY {property} DESC LIMIT {n}; "
    
    cursor.execute(sql)
    data = cursor.fetchall()
    return data


def get_avg_payment_days(start_date: datetime, end_date: datetime, party_id: int):

    db, cursor = db_connector.cursor(True)

    sql = "drop view if exists party_bills cascade"
    cursor.execute(sql)
    db.commit()
    
    sql = f"create view party_bills as select party_id, register_date \
            from memo_entry join memo_bills on memo_entry.id = memo_bills.memo_id \
            where type = 'F' and party_id = {party_id}"
    
    cursor.execute(sql)
    db.commit()
    
    sql = f"create view avg_payment_date as select register_entry.party_id, \
            avg(date_part('day', register_entry.register_date - party_bills.register_date))::integer as avg  \
            from register_entry join party_bills on  \
            register_entry.party_id = party_bills.party_id  \
            where register_entry.register_date >= '{start_date}' AND register_entry.register_date <= '{end_date}' \
            group by register_entry.party_id; "
    
    cursor.execute(sql)
    db.commit()

    sql = f"select * from avg_payment_date;"

    cursor.execute(sql)

    data = cursor.fetchall()

    return data




 



start_date = "01/01/2020"
end_date = "31/12/2021"
start_date = str(datetime.datetime.strptime(start_date, "%d/%m/%Y"))
end_date = str(datetime.datetime.strptime(end_date, "%d/%m/%Y"))









































#
# SANNAT WAS HERE!
#














































# get_sales(start_date, end_date)
# top_individuals(start_date, end_date, "supplier", 50, amount)
# get_top_individuals(start_date, end_date, "supplier", 50, "amount")
print(get_avg_payment_days(start_date, end_date, 1))