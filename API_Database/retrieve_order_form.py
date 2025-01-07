from typing import Dict
from psql import db_connector, execute_query
from pypika import Query, Table, Field, functions as fn
from Exceptions import DataError
from datetime import datetime


def get_order_form_id(supplier_id: int, party_id: int, order_form_number: int) -> int:
    """
    Returns primary key id of the order form entry.
    """

    query = "SELECT id FROM order_form WHERE order_form_number = '{}' AND supplier_id = '{}' AND party_id = '{}' " \
            "ORDER BY register_date DESC".format(
                order_form_number, supplier_id, party_id)

    result = db_connector.execute_query(query, False)
    data = result["result"]

    return data[0][0]


def get_order_form(supplier_id: int, party_id: int, order_form_number: int) -> Dict:
    """
    Return the order form associated with the given order_form_number.
    """

    # Define the table
    order_form_table = Table('order_form')

    # Build the SELECT query using Pypika
    select_query = Query.from_(order_form_table).select(
        order_form_table.id,
        order_form_table.supplier_id,
        order_form_table.party_id,
        order_form_table.order_form_number,
        order_form_table.register_date,
        order_form_table.status, 
        order_form_table.delivered,
    ).where(
        (order_form_table.order_form_number == order_form_number) &
        (order_form_table.supplier_id == supplier_id) &
        (order_form_table.party_id == party_id)
    )

    # Get the raw SQL query from the Pypika query
    sql = select_query.get_sql()

    # Execute the query and fetch data from the database
    data = execute_query(sql)

    # Convert the fetched data into a list of OrderForm objects
    result = data["result"]

    if len(result) == 0:
        raise DataError(
            f"No Order Form with order_form_number: {order_form_number}")

    if len(result) != 1:
        raise DataError(
            f"Multiple Order Forms with same order_form_number: {order_form_number}")

    return result[0]


def get_all_order_forms(**kwargs):
    """
    Get all order forms and also use 
    """
    # create query to get all data from order_form using pypika
    order_form_table = Table('order_form')
    select_query = Query.from_(order_form_table).select(
        order_form_table.id,
        order_form_table.supplier_id,
        order_form_table.party_id,
        order_form_table.order_form_number,
        fn.ToChar(order_form_table.register_date,
                  'YYYY-MM-DD').as_("register_date"),
        order_form_table.status,
        order_form_table.delivered,
    )

    if "supplier_id" in kwargs:
        supplier_id = int(kwargs["supplier_id"])
        select_query = select_query.where(
            (order_form_table.supplier_id == supplier_id)
        )

    if "party_id" in kwargs:
        party_id = int(kwargs["party_id"])
        select_query = select_query.where(
            (order_form_table.party_id == party_id)
        )

    # Get the raw SQL query from the Pypika query
    sql = select_query.get_sql()

    # Execute the query and fetch data from the database
    response = execute_query(sql)
    return response["result"]


def get_order_form_report_data(supplier_id: int, party_id: int, start_date: str, end_date: str, **kwargs) -> list:
    """
    Returns a list containing the Order Form Number, Register Date, Supplier Name,
    Supplier Address, Party Name, and Order Form Status for the given supplier and party.
    """

    # Define the tables
    order_form_table = Table('order_form')
    supplier_table = Table('supplier')
    party_table = Table('party')

    # Build the SELECT query using Pypika
    select_query = (Query.from_(order_form_table)
                    .join(supplier_table).on(supplier_table.id == order_form_table.supplier_id)
                    .join(party_table).on(party_table.id == order_form_table.party_id)
                    .select(
                        order_form_table.order_form_number.as_('order_no'),
                        fn.ToChar(order_form_table.register_date,
                                  "DD/MM/YYYY").as_('order_date'),
                        supplier_table.name.as_('supp_name'),
                        supplier_table.address.as_('supp_address'),
                        fn.Coalesce(supplier_table.phone_number,
                                    '').as_('supp_phno.'),
                        party_table.name.as_('party_name'),
                        order_form_table.status
    )
        .where((order_form_table.supplier_id == supplier_id) &
               (order_form_table.party_id == party_id) &
               (order_form_table.delivered == False)))

    select_query = select_query.where(
        order_form_table.register_date.between(start_date, end_date))

    # Get the raw SQL query from the Pypika query
    sql = select_query.get_sql()

    # Execute the query and fetch data from the database
    data = execute_query(sql)

    return data["result"]
