from __future__ import annotations
from typing import List, Dict, Optional
from psql import execute_query
from pypika import Query, Table, Field, Order, functions as fn
import sys
sys.path.append('../')

def calculate_commission(amount: float, gst_percentage: float = 4.762) -> float:
    """
    Calculate commission amount based on memo amount.
    First removes GST from the amount, then calculates 2% of the remaining amount.
    
    Args:
        amount: The memo amount
        gst_percentage: The GST percentage to remove (default: 4.762%)
        
    Returns:
        The calculated commission amount
    """
    # Remove GST from amount
    amount_without_gst = amount / (1 + (gst_percentage / 100))
    # Calculate 2% commission
    commission = amount_without_gst * 0.02
    return round(commission, 2)

def get_memo_dalali_payment(memo_id: int) -> Optional[Dict]:
    """
    Get dalali payment information for a specific memo entry
    
    Args:
        memo_id: The ID of the memo entry
        
    Returns:
        Dictionary containing dalali payment information or None if not found
    """
    dalali_payments = Table('memo_dalali_payments')
    query = Query.from_(dalali_payments).select('*').where(dalali_payments.memo_id == memo_id)
    sql = query.get_sql()
    response = execute_query(sql)
    
    if len(response['result']) == 0:
        return None
    
    return response['result'][0]

def get_all_memo_entries_with_dalali() -> List[Dict]:
    """
    Get all memo entries with dalali payment information
    
    Returns:
        List of dictionaries containing memo entries with dalali payment information
    """
    memo_entry = Table('memo_entry')
    supplier = Table('supplier')
    party = Table('party')
    dalali_payments = Table('memo_dalali_payments')

    query = (
        Query.from_(memo_entry)
        .left_join(supplier).on(memo_entry.supplier_id == supplier.id)
        .left_join(party).on(memo_entry.party_id == party.id)
        .left_join(dalali_payments).on(memo_entry.id == dalali_payments.memo_id)
        .select(
            memo_entry.id,
            memo_entry.memo_number,
            memo_entry.supplier_id,
            supplier.name.as_('supplier_name'),
            memo_entry.party_id,
            party.name.as_('party_name'),
            memo_entry.amount,
            memo_entry.register_date,
            dalali_payments.id.as_('dalali_payment_id'),
            dalali_payments.is_paid,
            dalali_payments.paid_amount,
            dalali_payments.remark,
            dalali_payments.last_update.as_('dalali_last_update')
        )
        .orderby(memo_entry.register_date, order=Order.desc)
    )
    

    sql = query.get_sql()

    response = execute_query(sql)
    result = response['result']
    
    # Calculate commission amount for each memo entry
    for entry in result:
        if entry['amount'] is not None:
            entry['commission_amount'] = calculate_commission(float(entry['amount']))
        else:
            entry['commission_amount'] = 0
            
        # If no dalali payment record exists, set default values
        if entry['dalali_payment_id'] is None:
            entry['is_paid'] = False
            entry['paid_amount'] = 0
            entry['remark'] = ''
    
    return result
