CREATE SEQUENCE item_seq;

CREATE TABLE item (
    id INT DEFAULT nextval('item_seq') PRIMARY KEY,
    supplier_id INT,
    name VARCHAR(255) NOT NULL,
    color VARCHAR(255) DEFAULT 'N/A',
    UNIQUE (supplier_id, name, color),
    FOREIGN KEY (supplier_id) REFERENCES supplier(id)
);

CREATE SEQUENCE item_entry_seq;

CREATE TABLE item_entry (
	id INT DEFAULT nextval('item_entry_seq') PRIMARY KEY,
    register_entry_id INT,
    item_id INT,
    quantity INT,
    rate INT,
    UNIQUE(register_entry_id, item_id),
    FOREIGN KEY (register_entry_id) REFERENCES register_entry(id),
    FOREIGN KEY (item_id) REFERENCES item(id)
);