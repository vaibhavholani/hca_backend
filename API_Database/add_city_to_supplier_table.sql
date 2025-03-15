ALTER TABLE supplier 
  ADD COLUMN city VARCHAR(20) 
  CHECK (city IN ('Bangalore', 'Jaipur', 'Kolkata', 'Surat', 'Varanasi', 'Belgaum', 'Mumbai', 'Delhi', 'Mau'));


