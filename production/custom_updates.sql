-- Add a new column to memo_bills
ALTER TABLE memo_bills
ADD COLUMN bill_id INT;

-- Create the unique_register_entries view
CREATE OR REPLACE VIEW unique_register_entries AS
SELECT DISTINCT ON (supplier_id, party_id, bill_number) 
        id, 
        supplier_id, 
        party_id, 
        register_date, 
        amount, 
        bill_number, 
        gr_amount, 
        deduction, 
        status, 
        partial_amount, 
        last_update
FROM register_entry
ORDER BY supplier_id, party_id, bill_number, register_date ASC;

-- Update memo_bills with bill_id using earliest register entries
WITH earliest_register_entries AS (
    SELECT
           re.id AS register_id, 
           re.bill_number AS bill_number,
           re.register_date AS register_date,
           mb.id AS memo_bill_id
    FROM memo_bills mb
    JOIN memo_entry me 
      ON mb.memo_id = me.id
    JOIN unique_register_entries re
      ON re.supplier_id = me.supplier_id
     AND re.party_id   = me.party_id
     AND re.bill_number = mb.bill_number
    WHERE mb.bill_number != -1
    ORDER BY re.supplier_id, re.party_id, re.bill_number, re.register_date
)
UPDATE memo_bills mb
SET bill_id = e.register_id
FROM earliest_register_entries e
WHERE mb.id = e.memo_bill_id;

-- Check for null bill_id entries
SELECT COUNT(*) AS null_bill_ids
FROM memo_bills
WHERE bill_id IS NULL;

-- Drop the temporary view
DROP VIEW IF EXISTS unique_register_entries;

-- Remove the bill_number column from memo_bills
ALTER TABLE memo_bills
DROP COLUMN bill_number;

-- Add a foreign key constraint to bill_id
ALTER TABLE memo_bills
ADD CONSTRAINT fk_memo_bills_bill_id
FOREIGN KEY (bill_id) REFERENCES register_entry(id);
