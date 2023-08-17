ALTER TABLE supplier
ADD COLUMN phone_number VARCHAR(20);


ALTER TABLE party
ADD COLUMN phone_number VARCHAR(20);

ALTER TABLE bank
ADD COLUMN phone_number VARCHAR(20);

ALTER TABLE transport
ADD COLUMN phone_number VARCHAR(20);


CREATE SEQUENCE order_form_seq;

CREATE TABLE order_form(
    id INT DEFAULT nextval('order_form_seq') PRIMARY KEY,
	supplier_id INT,
	party_id INT,
	order_form_number INT,
	register_date TIMESTAMP(0),
	status VARCHAR,
	delivered boolean DEFAULT false,
	last_update TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (party_id) REFERENCES party(id),
	FOREIGN KEY (supplier_id) REFERENCES supplier(id)
	);
