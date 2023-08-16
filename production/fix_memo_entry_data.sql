
-- Distinct data query
SELECT DISTINCT
    s.name AS supplier_name,
    p.name AS party_name,
    s.id AS supplier_id, 
    p.id AS party_id,
    me.memo_number
FROM 
    memo_entry AS me
JOIN
    memo_bills AS mb ON me.id = mb.memo_id
JOIN 
    supplier AS s ON me.supplier_id = s.id
JOIN 
    party AS p ON me.party_id = p.id
WHERE 
    mb.memo_id IN (
        SELECT memo_id
        FROM memo_bills 
        WHERE bill_number IN (
            SELECT bill_number 
            FROM register_entry 
            WHERE (gr_amount + deduction) > amount
        )
    );