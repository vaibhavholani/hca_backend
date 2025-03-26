-- Add new columns to memo_entry table
ALTER TABLE memo_entry 
ADD COLUMN discount INT DEFAULT 0,
ADD COLUMN other_deduction INT DEFAULT 0,
ADD COLUMN rate_difference INT DEFAULT 0,
ADD COLUMN gr_amount_details TEXT,
ADD COLUMN discount_details TEXT,
ADD COLUMN other_deduction_details TEXT,
ADD COLUMN rate_difference_details TEXT,
ADD COLUMN notes TEXT;

-- Add amount column to memo_payments table
ALTER TABLE memo_payments
ADD COLUMN amount INT DEFAULT 0;

-- Comment explaining the upgrade
COMMENT ON TABLE memo_entry IS 'Table upgraded on 2025-03-20 to include discount, other_deduction, rate_difference, and details fields';
COMMENT ON TABLE memo_payments IS 'Table upgraded on 2025-03-20 to include amount field';
