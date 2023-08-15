CREATE SEQUENCE supplier_seq;

-- supplier table
CREATE TABLE supplier (
	id INT DEFAULT NEXTVAL ('supplier_seq') PRIMARY KEY,
	name VARCHAR(100),
	address VARCHAR(300),
	phone_number VARCHAR(20), -- Added column
	UNIQUE (name),
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP 
);

-- party table
CREATE SEQUENCE party_seq;

CREATE TABLE party (
	id INT DEFAULT NEXTVAL ('party_seq') PRIMARY KEY,
	name VARCHAR(100),
	address VARCHAR(300),
	phone_number VARCHAR(20), -- Added column
	UNIQUE (name),
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP 
);

-- bank table
CREATE SEQUENCE bank_seq;

CREATE TABLE bank (
	id INT DEFAULT NEXTVAL ('bank_seq') PRIMARY KEY,
	name VARCHAR(100),
	address VARCHAR(300),
	phone_number VARCHAR(20), -- Added column
	UNIQUE (name),
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP 
);

-- Transport table
CREATE SEQUENCE Transport_seq;

CREATE TABLE Transport (
	id INT DEFAULT NEXTVAL ('Transport_seq') PRIMARY KEY,
	name VARCHAR(100),
	address VARCHAR(300),
	phone_number VARCHAR(20), -- Added column
	UNIQUE (name),
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP 
);
CREATE SEQUENCE register_entry_seq;

CREATE TABLE register_entry (
	id INT DEFAULT NEXTVAL ('register_entry_seq') PRIMARY KEY,
	supplier_id INT,
	party_id INT, 
	register_date TIMESTAMP(0),
	amount INT,
	bill_number INT,
	gr_amount INT DEFAULT 0,
	deduction INT DEFAULT 0,
	status VARCHAR(2) DEFAULT 'N',
	partial_amount INT DEFAULT 0,
	UNIQUE (bill_number, supplier_id, party_id, register_date),
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (party_id) REFERENCES party(id),
	FOREIGN KEY (supplier_id) REFERENCES supplier(id)
	);

CREATE SEQUENCE memo_entry_seq;

CREATE TABLE memo_entry(
	id INT DEFAULT NEXTVAL ('memo_entry_seq') PRIMARY KEY,
	memo_number INT,
	supplier_id INT,
	party_id INT, 
	register_date TIMESTAMP(0),
	amount INT default 0,
	gr_amount INT default 0,
	deduction INT default 0,
	UNIQUE (memo_number, party_id, supplier_id, register_date),
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (party_id) REFERENCES party(id),
	FOREIGN KEY (supplier_id) REFERENCES supplier(id)
	);

CREATE SEQUENCE memo_payments_seq;

CREATE TABLE memo_payments(
    id INT DEFAULT NEXTVAL ('memo_payments_seq') PRIMARY KEY,
	memo_id INT, 
	bank_id INT,
	cheque_number INT,
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (memo_id) REFERENCES memo_entry(id),
	FOREIGN KEY (bank_id) REFERENCES bank(id)
	);

CREATE SEQUENCE memo_bills_seq;

CREATE TABLE memo_bills (
    id INT DEFAULT NEXTVAL ('memo_bills_seq') PRIMARY KEY,
	memo_id INT, 
	bill_number INT,
	type VARCHAR(2),
	amount INT,
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (memo_id) REFERENCES memo_entry(id)
);

CREATE SEQUENCE part_payment_seq;

CREATE TABLE part_payments(
    id INT DEFAULT nextval('part_payment_seq') PRIMARY KEY,
	supplier_id INT,
	party_id INT,
	memo_id INT,
	used boolean DEFAULT false,
	use_memo_id INT,
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (party_id) REFERENCES party(id),
	FOREIGN KEY (supplier_id) REFERENCES supplier(id),
	FOREIGN KEY (memo_id) REFERENCES memo_entry(id),
	FOREIGN KEY (use_memo_id) REFERENCES memo_entry(id)
	);

CREATE SEQUENCE order_form_seq;

CREATE TABLE order_form(
    id INT DEFAULT nextval('order_form_seq') PRIMARY KEY,
	supplier_id INT,
	party_id INT,
	order_form_number INT,
	register_date TIMESTAMP(0),
	status VARCHAR,
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (party_id) REFERENCES party(id),
	FOREIGN KEY (supplier_id) REFERENCES supplier(id)
	);


CREATE TABLE last_update(
	updated_at TIMESTAMP(0)
);

CREATE TABLE stack(
    query VARCHAR(500),
    val VARCHAR(500),
    updated_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
);