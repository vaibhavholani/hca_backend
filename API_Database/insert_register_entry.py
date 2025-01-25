from __future__ import annotations
from psql import execute_query
from API_Database import sql_date
from pypika import Query, Table
from Exceptions.custom_exception import DataError

def check_new_register(entry) -> bool:
    """
    Check if the register_entry is valid to insert.
    Rules:
    1. No exact duplicate (same bill number, supplier, party, and date)
    2. If bill number exists for same supplier and party, dates must be at least 6 months apart
    """
    
    # First check for exact duplicate
    exact_duplicate_query = """
        SELECT id, register_date 
        FROM register_entry 
        WHERE bill_number = '{}' 
        AND supplier_id = '{}' 
        AND party_id = '{}' 
        AND register_date = '{}'
    """.format(entry.bill_number, entry.supplier_id, entry.party_id, entry.register_date)
    
    response = execute_query(exact_duplicate_query)
    if len(response["result"]) > 0:
        return False

    # Then check for bills with same number but different dates
    similar_bills_query = """
        SELECT register_date 
        FROM register_entry 
        WHERE bill_number = '{}' 
        AND supplier_id = '{}' 
        AND party_id = '{}' 
        AND register_date != '{}'
        ORDER BY register_date
    """.format(entry.bill_number, entry.supplier_id, entry.party_id, entry.register_date)
    
    response = execute_query(similar_bills_query)
    existing_dates = [row["register_date"] for row in response["result"]]
    
    if existing_dates:
        new_date = entry.register_date
        for existing_date in existing_dates:
            # Calculate months between dates using PostgreSQL
            months_diff_query = """
                SELECT ABS(
                    EXTRACT(year FROM AGE('{}', '{}')) * 12 +
                    EXTRACT(month FROM AGE('{}', '{}'))
                ) as months_between
            """.format(new_date, existing_date, new_date, existing_date)
            
            response = execute_query(months_diff_query)
            months_between = response["result"][0]["months_between"]
            
            if months_between < 6:
                raise DataError({
                    "status": "error",
                    "message": "Duplicate Bill Number too close in time",
                    "input_errors": {
                        "bill_number": {
                            "status": "error",
                            "message": f"Bill number {entry.bill_number} already exists with date {existing_date}. Duplicate bill numbers must be at least 6 months apart."
                        }
                    }
                })
    
    return True

def insert_register_entry(entry) -> None:
    """
    Insert a register_entry into the database.
    """
    
    # Define the table
    register_entry_table = Table('register_entry')

    # Build the INSERT query using Pypika
    insert_query = Query.into(register_entry_table).columns(
        'supplier_id',
        'party_id',
        'register_date',
        'amount',
        'bill_number',
        'status',
        'gr_amount',
        'deduction'
    ).insert(
        entry.supplier_id,
        entry.party_id,
        entry.register_date,
        entry.amount,
        entry.bill_number,
        entry.status,
        entry.gr_amount,
        entry.deduction
    )

    # Get the raw SQL query and parameters from the Pypika query
    sql = insert_query.get_sql()
    # Execute the query
    return execute_query(sql)
