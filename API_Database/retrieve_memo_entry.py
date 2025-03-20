from __future__ import annotations
from typing import Union, List, Optional
from datetime import datetime, timedelta
import datetime
from typing import Dict
from Exceptions import DataError
from psql import db_connector, execute_query
from API_Database.utils import parse_date, sql_date
from API_Database.retrieve_partial_payment import get_partial_payment
from API_Database.retrieve_partial_payment import get_partial_payment_bulk
from pypika import Query, Table, Field, functions as fn, Order
import sys
import math
sys.path.append('../')

def check_new_memo(memo_number: int, date: datetime, *args, **kwargs) -> bool:
    """
    Check if the memo already exists.
    """
    query = "select register_date, supplier_id, party_id from memo_entry where memo_number = '{}' order by 1 DESC".format(memo_number)
    response = execute_query(query)
    result = response['result']
    if len(result) == 0:
        return True
    return False

def check_add_memo(memo_number: int, memo_date: str) -> bool:
    """
    Check if the memo already exists.
    """
    (db, cursor) = db_connector.cursor()
    query = "select register_date from memo_entry where memo_number = '{}' order by 1 DESC".format(memo_number)
    cursor.execute(query)
    data = cursor.fetchall()
    db.close()
    if len(data) == 0:
        return True
    return False

def get_memo_entry_id(supplier_id: int, party_id: int, memo_number: int) -> int:
    """
    Get the memo_id using memo_number, supplier_id and party_id
    """
    query = 'select id from memo_entry where memo_number = {} AND supplier_id = {} AND party_id = {} order by register_date DESC;'.format(memo_number, supplier_id, party_id)
    response = execute_query(query)
    if len(response['result']) == 0:
        raise DataError(f'No memo entry found with memo_number: {memo_number}, supplier_id: {supplier_id}, party_id: {party_id}')
    elif len(response['result']) > 1:
        raise DataError(f'Multiple memo entries found with memo_number: {memo_number}, supplier_id: {supplier_id}, party_id: {party_id}')
    return int(response['result'][0]['id'])

def get_memo_bill_id(memo_id: int, bill_id: Optional[int], type: str, amount: int) -> int:
    """Constructs and executes a query to retrieve a memo bill ID based on memo details; raises DataError if no result is found."""
    memo_bills = Table('memo_bills')
    query = Query.from_(memo_bills).select(memo_bills.id).where((memo_bills.memo_id == memo_id) & (memo_bills.type == type) & (memo_bills.amount == amount))
    if bill_id is not None:
        query = query.where(memo_bills.bill_id == bill_id)
    sql = query.get_sql()
    response = execute_query(sql)
    if len(response['result']) == 0:
        raise DataError(f'No memo bill found with memo_id: {memo_id}, bill_id: {bill_id}, type: {type}, amount: {amount}')
    return response['result'][0]['id']

def get_memo_bills_by_id(memo_id: int) -> Dict:
    """Retrieves memo bills for a given memo ID and returns the results as a dictionary."""
    memo_bills = Table('memo_bills')
    query = Query.from_(memo_bills).select(memo_bills.id, memo_bills.bill_id, memo_bills.type, memo_bills.amount).where(memo_bills.memo_id == memo_id).orderby(memo_bills.bill_id)
    sql = query.get_sql()
    response = execute_query(sql)
    return response['result']

def get_memo_entry(memo_id: int) -> Dict:
    """Retrieves a memo entry along with its associated payments and bills for a given memo ID."""
    memo_entry_table = Table('memo_entry')
    memo_payments_table = Table('memo_payments')
    memo_bills_table = Table('memo_bills')
    bank_table = Table('bank')
    register_entry_table = Table('register_entry')
    part_payments_table = Table('part_payments')
    supplier_table = Table('supplier')
    party_table = Table('party')
    
    # Get memo entry data with supplier and party names
    select_query = Query.from_(memo_entry_table)\
        .left_join(supplier_table).on(memo_entry_table.supplier_id == supplier_table.id)\
        .left_join(party_table).on(memo_entry_table.party_id == party_table.id)\
        .select(
            memo_entry_table.star,
            supplier_table.name.as_('supplier_name'),
            party_table.name.as_('party_name')
        )\
        .where(memo_entry_table.id == memo_id)
    
    memo_data = execute_query(select_query.get_sql())['result'][0]
    
    # Get payment data
    select_query = Query.from_(memo_payments_table)\
        .join(bank_table).on(memo_payments_table.bank_id == bank_table.id)\
        .select(
            memo_payments_table.bank_id,
            bank_table.name.as_('bank_name'),
            memo_payments_table.cheque_number,
            memo_payments_table.amount
        )\
        .where(memo_payments_table.memo_id == memo_id)
    
    payments_data = execute_query(select_query.get_sql())['result']
    payments = [
        {
            'bank_id': p['bank_id'],
            'bank_name': p['bank_name'],
            'cheque_number': p['cheque_number'],
            'amount': p.get('amount', 0)
        }
        for p in payments_data
    ]
    
    # Get memo bills data
    select_query = Query.from_(memo_bills_table)\
        .left_join(register_entry_table).on(memo_bills_table.bill_id == register_entry_table.id)\
        .select(
            memo_bills_table.id,
            memo_bills_table.bill_id,
            register_entry_table.bill_number,
            memo_bills_table.type,
            memo_bills_table.amount
        )\
        .where(memo_bills_table.memo_id == memo_id)\
        .orderby(register_entry_table.bill_number)
    
    bills_data = execute_query(select_query.get_sql())['result']
    for bill in bills_data:
        if bill['bill_number'] is None:
            bill['bill_number'] = -1
    
    # Determine mode
    mode = 'Full'
    for bill in bills_data:
        if bill['type'] == 'PR':
            mode = 'Part'
            break
    
    # Get part payments if full mode
    part_payments = []
    if mode == 'Full':
        # Join with memo_entry to get memo_number and amount
        select_query = Query.from_(part_payments_table)\
            .join(memo_entry_table.as_('me')).on(part_payments_table.memo_id == memo_entry_table.as_('me').id)\
            .select(
                part_payments_table.id,
                part_payments_table.memo_id,
                memo_entry_table.as_('me').memo_number,
                memo_entry_table.as_('me').amount
            )\
            .where(part_payments_table.use_memo_id == memo_id)
        
        part_payments_data = execute_query(select_query.get_sql())['result']
        
        # Create a list of dictionaries with memo_id, memo_number, and amount
        part_details = [
            {
                'memo_id': p['memo_id'],
                'memo_number': p['memo_number'],
                'amount': p['amount']
            } for p in part_payments_data
        ]
        part_payments = [p['memo_id'] for p in part_details]
    
    # Parse JSON fields
    import json
    
    def parse_json_field(field_value, default=None):
        if not field_value:
            return default or []
        try:
            return json.loads(field_value)
        except:
            return default or []
    
    # Construct result
    result = {
        'id': memo_data['id'],
        'memo_number': memo_data['memo_number'],
        'supplier_id': memo_data['supplier_id'],
        'party_id': memo_data['party_id'],
        'supplier_name': memo_data['supplier_name'],
        'party_name': memo_data['party_name'],
        'amount': memo_data['amount'],
        'gr_amount': memo_data.get('gr_amount', 0),
        'deduction': memo_data.get('deduction', 0),
        'register_date': sql_date(memo_data['register_date']),
        'mode': mode,
        'memo_bills': bills_data,
        'payment': payments,
        # New fields
        'discount': memo_data.get('discount', 0),
        'other_deduction': memo_data.get('other_deduction', 0),
        'rate_difference': memo_data.get('rate_difference', 0),
        'less_details': {
            'gr_amount': parse_json_field(memo_data.get('gr_amount_details')),
            'discount': parse_json_field(memo_data.get('discount_details')),
            'other_deduction': parse_json_field(memo_data.get('other_deduction_details')),
            'rate_difference': parse_json_field(memo_data.get('rate_difference_details'))
        },
        'notes': parse_json_field(memo_data.get('notes'))
    }
    
    if part_payments:
        result['selected_part'] = part_payments
        result['part_details'] = part_details
    
    return result

def get_all_memo_entries(**kwargs):
    """
    Get all memo entries only from memo_entry table
    Designed to use for the view menu filtering
    """
    memo_entry_table = Table('memo_entry')
    select_query = Query.from_(memo_entry_table).select(memo_entry_table.id)
    if 'supplier_id' in kwargs:
        supplier_id = int(kwargs['supplier_id'])
        select_query = select_query.where(memo_entry_table.supplier_id == supplier_id)
    if 'party_id' in kwargs:
        party_id = int(kwargs['party_id'])
        select_query = select_query.where(memo_entry_table.party_id == party_id)
    sql = select_query.get_sql()
    response = execute_query(sql)
    memo_entries = response['result']
    memo_entries_json: List[Dict] = []
    for memo_entry in memo_entries:
        memo_id = memo_entry['id']
        memo_entries_json.append(get_memo_entry(memo_id))
    return memo_entries_json

def get_total_memo_entity_bulk(supplier_ids: List[int], party_ids: List[int], start_date: datetime.datetime, end_date: datetime.datetime, memo_type: str, supplier_all: bool=False, party_all: bool=False):
    """
    Get total memo amount for multiple suppliers and parties in one query.
    Optimized version that fetches data in bulk when all suppliers/parties are selected.
    """
    if memo_type == 'PR':
        result = get_partial_payment_bulk(supplier_ids, party_ids, supplier_all, party_all)
        return sum((row['memo_amt'] for row in result))
    where_clauses = []
    if not supplier_all and supplier_ids:
        supplier_ids_str = ','.join(map(str, supplier_ids))
        where_clauses.append(f'memo_entry.supplier_id IN ({supplier_ids_str})')
    if not party_all and party_ids:
        party_ids_str = ','.join(map(str, party_ids))
        where_clauses.append(f'memo_entry.party_id IN ({party_ids_str})')
    where_clauses.extend([f"memo_bills.type = '{memo_type}'", f"memo_entry.register_date >= '{start_date}'", f"memo_entry.register_date <= '{end_date}'"])
    where_clause = ' AND '.join(where_clauses)
    query = '\n        SELECT COALESCE(SUM(memo_bills.amount), 0) as total_amount\n        FROM memo_bills\n        JOIN memo_entry ON memo_bills.memo_id = memo_entry.id\n        WHERE {}\n    '.format(where_clause)
    result = execute_query(query)
    return int(result['result'][0]['total_amount'])

def generate_memo_total(supplier_ids: Union[int, List[int]], party_ids: Union[int, List[int]], start_date: datetime, end_date: datetime, memo_type: str, supplier_all: bool=False, party_all: bool=False):
    """
    Generates the total for the given supplier_ids and party_ids for memo_bills.
    Uses bulk query for better performance.
    """
    if isinstance(supplier_ids, int):
        supplier_ids = [supplier_ids]
    if isinstance(party_ids, int):
        party_ids = [party_ids]
    if isinstance(start_date, str):
        start_date = parse_date(start_date)
    if isinstance(end_date, str):
        end_date = parse_date(end_date)
    return get_total_memo_entity_bulk(supplier_ids, party_ids, start_date, end_date, memo_type, supplier_all=supplier_all, party_all=party_all)

def get_all_memo_entries_with_names(page=None, page_size=None, filters=None) -> Dict:
    """Retrieves all memo entries with supplier and party names.
    
    Args:
        page: Optional page number for pagination (1-indexed)
        page_size: Optional number of items per page
        filters: Optional dictionary of filters to apply
    
    Returns:
        Dictionary with status and result
    """
    try:
        # Create table references
        memo_entry_table = Table('memo_entry')
        supplier_table = Table('supplier')
        party_table = Table('party')
        
        # Build query with JOINs
        query = Query.from_(memo_entry_table)\
            .left_join(supplier_table).on(memo_entry_table.supplier_id == supplier_table.id)\
            .left_join(party_table).on(memo_entry_table.party_id == party_table.id)\
            .select(
                memo_entry_table.star,
                supplier_table.name.as_('supplier_name'),
                party_table.name.as_('party_name')
            )
        
        # Apply filters if provided
        if filters:
            if 'supplier_id' in filters and filters['supplier_id']:
                query = query.where(memo_entry_table.supplier_id == filters['supplier_id'])
            if 'party_id' in filters and filters['party_id']:
                query = query.where(memo_entry_table.party_id == filters['party_id'])
            if 'start_date' in filters and filters['start_date']:
                query = query.where(memo_entry_table.register_date >= filters['start_date'])
            if 'end_date' in filters and filters['end_date']:
                query = query.where(memo_entry_table.register_date <= filters['end_date'])
            if 'memo_number' in filters and filters['memo_number']:
                query = query.where(memo_entry_table.memo_number == filters['memo_number'])
        
        # Get total count for pagination
        count_query = Query.from_(memo_entry_table).select(fn.Count('*').as_('total'))
        
        # Apply the same filters to count query
        if filters:
            if 'supplier_id' in filters and filters['supplier_id']:
                count_query = count_query.where(memo_entry_table.supplier_id == filters['supplier_id'])
            if 'party_id' in filters and filters['party_id']:
                count_query = count_query.where(memo_entry_table.party_id == filters['party_id'])
            if 'start_date' in filters and filters['start_date']:
                count_query = count_query.where(memo_entry_table.register_date >= filters['start_date'])
            if 'end_date' in filters and filters['end_date']:
                count_query = count_query.where(memo_entry_table.register_date <= filters['end_date'])
            if 'memo_number' in filters and filters['memo_number']:
                count_query = count_query.where(memo_entry_table.memo_number == filters['memo_number'])
        
        count_result = execute_query(count_query.get_sql())
        total_count = count_result['result'][0]['total'] if count_result['status'] == 'okay' else 0
        
        # Apply pagination if requested
        if page is not None and page_size is not None:
            offset = (page - 1) * page_size
            query = query.limit(page_size).offset(offset)
            
        # Add order by to ensure consistent results
        query = query.orderby(memo_entry_table.register_date, order=Order.desc)
        
        sql = query.get_sql()
        result = execute_query(sql)
        
        if result['status'] == 'error':
            return {'status': 'error', 'message': 'Failed to fetch memo entries'}
            
        memo_entries = result['result']
        
        # Enhance each entry with memo bills and payment info
        for entry in memo_entries:
            # Get memo bills
            memo_bills_table = Table('memo_bills')
            bills_query = Query.from_(memo_bills_table)\
                .select('*')\
                .where(memo_bills_table.memo_id == entry['id'])
            
            bills_result = execute_query(bills_query.get_sql())
            entry['memo_bills'] = bills_result['result'] if bills_result['status'] == 'okay' else []
            
            # Get payment info
            memo_payments_table = Table('memo_payments')
            bank_table = Table('bank')
            payments_query = Query.from_(memo_payments_table)\
                .left_join(bank_table).on(memo_payments_table.bank_id == bank_table.id)\
                .select(
                    memo_payments_table.bank_id,
                    bank_table.name.as_('bank_name'),
                    memo_payments_table.cheque_number,
                    memo_payments_table.amount
                )\
                .where(memo_payments_table.memo_id == entry['id'])
            
            payments_result = execute_query(payments_query.get_sql())
            
            # Add amount to payment objects
            if payments_result['status'] == 'okay':
                entry['payment'] = [
                    {
                        'bank_id': p['bank_id'],
                        'bank_name': p['bank_name'],
                        'cheque_number': p['cheque_number'],
                        'amount': p.get('amount', 0)
                    }
                    for p in payments_result['result']
                ]
            else:
                entry['payment'] = []
                
            # Parse JSON fields
            import json
            
            def parse_json_field(field_value, default=None):
                if not field_value:
                    return default or []
                try:
                    return json.loads(field_value)
                except:
                    return default or []
            
            # Add new fields
            entry['discount'] = entry.get('discount', 0)
            entry['other_deduction'] = entry.get('other_deduction', 0)
            entry['rate_difference'] = entry.get('rate_difference', 0)
            entry['less_details'] = {
                'gr_amount': parse_json_field(entry.get('gr_amount_details')),
                'discount': parse_json_field(entry.get('discount_details')),
                'other_deduction': parse_json_field(entry.get('other_deduction_details')),
                'rate_difference': parse_json_field(entry.get('rate_difference_details'))
            }
            entry['notes'] = parse_json_field(entry.get('notes'))
        
        return {
            'status': 'okay', 
            'result': memo_entries,
            'pagination': {
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': math.ceil(total_count / page_size) if page_size else 1
            } if page is not None and page_size is not None else None
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
