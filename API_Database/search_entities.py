from pypika import Query, Table, Criterion
from psql import execute_query

def search_entities(table_name: str, search_query: str, **kwargs):
    """
    Search for entities in the specified table that match the search query using PyPika.
    
    Args:
        table_name: The name of the table to search in
        search_query: The search query string
        **kwargs: Additional filters to apply
        
    Returns:
        List of entities that match the search criteria
    """
    # Define searchable fields based on entity type
    # Only including the five core entities: Supplier, Party, Bank, Register Entry, and Memo Entry
    searchable_fields = {
        'supplier': ['name', 'address', 'phone_number'],
        'party': ['name', 'address', 'phone_number'],
        'bank': ['name', 'address', 'phone_number'],
        # Register Entry and Memo Entry have limited functionality for now
        'register_entry': ['bill_number'],
        'memo_entry': ['memo_number'],
    }
    
    fields = searchable_fields.get(table_name, ['name'])
    
    # Create table reference
    entity_table = Table(table_name)
    
    # Start building the query
    query = Query.from_(entity_table).select('*')
    
    # Build search criteria
    search_criteria = None
    for field in fields:
        # Handle numeric fields differently
        if field in ['bill_number', 'memo_number', 'order_form_number', 'quantity', 'rate']:
            # Only apply numeric search if the search query is a number
            if search_query.isdigit():
                criterion = entity_table[field] == int(search_query)
                if search_criteria is None:
                    search_criteria = criterion
                else:
                    search_criteria = search_criteria | criterion
        else:
            # For text fields, use ILIKE for case-insensitive search
            criterion = entity_table[field].ilike(f'%{search_query}%')
            if search_criteria is None:
                search_criteria = criterion
            else:
                search_criteria = search_criteria | criterion
    
    # Add search criteria to query
    if search_criteria:
        query = query.where(search_criteria)
    
    # Add any additional filters from kwargs
    for key, value in kwargs.items():
        if key not in ['table_name', 'search'] and value is not None:
            query = query.where(entity_table[key] == value)
    
    # Get the SQL
    sql = query.get_sql()
    
    # Execute the query
    result = execute_query(sql)
    return result['result']
