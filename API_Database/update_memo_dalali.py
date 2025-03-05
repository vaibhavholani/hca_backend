from __future__ import annotations
from typing import Dict, Optional, Union
from psql import db_connector, execute_query
from pypika import Query, Table
import sys
sys.path.append('../')

def create_or_update_dalali_payment(memo_id: int, is_paid: bool = False, paid_amount: Union[float, int] = 0, remark: str = '') -> Dict:
    """
    Create or update a dalali payment record for a memo entry
    
    Args:
        memo_id: The ID of the memo entry
        is_paid: Whether the dalali has been paid
        paid_amount: The amount paid
        remark: Any remarks about the payment
        
    Returns:
        Dictionary with status of the operation
    """
    # Check if a record already exists
    dalali_payments = Table('memo_dalali_payments')
    query = Query.from_(dalali_payments).select('id').where(dalali_payments.memo_id == memo_id)
    sql = query.get_sql()
    response = execute_query(sql)
    
    (db, cursor) = db_connector.cursor()
    
    try:
        if len(response['result']) == 0:
            # Create a new record
            query = """
                INSERT INTO memo_dalali_payments (memo_id, is_paid, paid_amount, remark, last_update)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            """
            cursor.execute(query, (memo_id, is_paid, paid_amount, remark))
            result = cursor.fetchone()
            db.commit()
            
            return {
                'status': 'success',
                'message': 'Dalali payment record created',
                'id': result['id']
            }
        else:
            # Update existing record
            payment_id = response['result'][0]['id']
            query = """
                UPDATE memo_dalali_payments
                SET is_paid = %s, paid_amount = %s, remark = %s, last_update = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id
            """
            cursor.execute(query, (is_paid, paid_amount, remark, payment_id))
            result = cursor.fetchone()
            db.commit()
            
            return {
                'status': 'success',
                'message': 'Dalali payment record updated',
                'id': result['id']
            }
    except Exception as e:
        db.rollback()
        return {
            'status': 'error',
            'message': f'Failed to update dalali payment: {str(e)}'
        }
    finally:
        db.close()

def update_dalali_payment_field(memo_id: int, field: str, value: Union[bool, float, int, str]) -> Dict:
    """
    Update a specific field of a dalali payment record
    
    Args:
        memo_id: The ID of the memo entry
        field: The field to update ('is_paid', 'paid_amount', or 'remark')
        value: The new value for the field
        
    Returns:
        Dictionary with status of the operation
    """
    if field not in ['is_paid', 'paid_amount', 'remark']:
        return {
            'status': 'error',
            'message': f'Invalid field: {field}'
        }
    
    # Check if a record already exists
    dalali_payments = Table('memo_dalali_payments')
    query = Query.from_(dalali_payments).select('*').where(dalali_payments.memo_id == memo_id)
    sql = query.get_sql()
    response = execute_query(sql)
    
    (db, cursor) = db_connector.cursor()
    
    try:
        if len(response['result']) == 0:
            # Create a new record with default values
            defaults = {
                'is_paid': False,
                'paid_amount': 0,
                'remark': ''
            }
            
            # Update with the provided value
            defaults[field] = value
            
            query = """
                INSERT INTO memo_dalali_payments (memo_id, is_paid, paid_amount, remark, last_update)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            """
            cursor.execute(query, (memo_id, defaults['is_paid'], defaults['paid_amount'], defaults['remark']))
            result = cursor.fetchone()
            db.commit()
            
            return {
                'status': 'success',
                'message': 'Dalali payment record created',
                'id': result['id']
            }
        else:
            # Update existing record
            payment_id = response['result'][0]['id']
            query = f"""
                UPDATE memo_dalali_payments
                SET {field} = %s, last_update = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id
            """
            cursor.execute(query, (value, payment_id))
            result = cursor.fetchone()
            db.commit()
            
            return {
                'status': 'success',
                'message': 'Dalali payment field updated',
                'id': result['id']
            }
    except Exception as e:
        db.rollback()
        return {
            'status': 'error',
            'message': f'Failed to update dalali payment field: {str(e)}'
        }
    finally:
        db.close()
