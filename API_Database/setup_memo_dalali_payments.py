"""
Script to create the memo_dalali_payments table in the database.
"""
from psql import db_connector, execute_query
import sys
sys.path.append('../')

def create_memo_dalali_payments_table():
    """
    Create the memo_dalali_payments table if it doesn't exist.
    """
    query = """
    CREATE TABLE IF NOT EXISTS memo_dalali_payments (
        id SERIAL PRIMARY KEY,
        memo_id INTEGER NOT NULL REFERENCES memo_entry(id),
        is_paid BOOLEAN DEFAULT FALSE,
        paid_amount NUMERIC(10, 2) DEFAULT 0,
        remark TEXT,
        last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(memo_id)
    );
    """
    
    try:
        (db, cursor) = db_connector.cursor()
        cursor.execute(query)
        db.commit()
        print("Successfully created memo_dalali_payments table.")
        return True
    except Exception as e:
        print(f"Error creating memo_dalali_payments table: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_memo_dalali_payments_table()
