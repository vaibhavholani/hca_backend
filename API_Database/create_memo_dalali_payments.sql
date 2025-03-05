-- Create table for tracking dalali payments
CREATE TABLE IF NOT EXISTS memo_dalali_payments (
    id SERIAL PRIMARY KEY,
    memo_id INTEGER NOT NULL REFERENCES memo_entry(id),
    is_paid BOOLEAN DEFAULT FALSE,
    paid_amount NUMERIC(10, 2) DEFAULT 0,
    remark TEXT,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(memo_id)
);
