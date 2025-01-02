ALTER TABLE memo_bills
ADD COLUMN bill_id INT;


WITH earliest_register_entries AS (
    SELECT DISTINCT ON (re.supplier_id, re.party_id, re.bill_number) re.id AS register_id, 
           mb.id AS memo_bill_id
    FROM memo_bills mb
    JOIN memo_entry me ON mb.memo_id = me.id
    JOIN register_entry re
      ON re.supplier_id = me.supplier_id
      AND re.party_id = me.party_id
      AND re.bill_number = mb.bill_number
    WHERE mb.bill_number != -1
    ORDER BY re.supplier_id, re.party_id, re.bill_number, re.register_date
)
UPDATE memo_bills mb
SET bill_id = e.register_id
FROM earliest_register_entries e
WHERE mb.id = e.memo_bill_id;



SELECT COUNT(*) AS null_bill_ids
FROM memo_bills
WHERE bill_id IS NULL;

ALTER TABLE memo_bills
DROP COLUMN bill_number;


ALTER TABLE memo_bills
ADD CONSTRAINT fk_memo_bills_bill_id
FOREIGN KEY (bill_id) REFERENCES register_entry(id);