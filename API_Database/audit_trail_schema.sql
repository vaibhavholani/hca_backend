-- Create Users table
CREATE SEQUENCE IF NOT EXISTS users_seq;
CREATE TABLE IF NOT EXISTS users (
    id BIGINT DEFAULT NEXTVAL('users_seq') PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    email TEXT,
    role TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated_by BIGINT
);

-- Create Permissions table
CREATE SEQUENCE IF NOT EXISTS permissions_seq;
CREATE TABLE IF NOT EXISTS permissions (
    id BIGINT DEFAULT NEXTVAL('permissions_seq') PRIMARY KEY,
    role TEXT NOT NULL,
    resource TEXT NOT NULL,
    can_create BOOLEAN DEFAULT FALSE,
    can_read BOOLEAN DEFAULT TRUE,
    can_update BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    UNIQUE(role, resource)
);

-- Create Audit log table
CREATE SEQUENCE IF NOT EXISTS audit_log_seq;
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGINT DEFAULT NEXTVAL('audit_log_seq') PRIMARY KEY,
    user_id BIGINT,
    table_name TEXT NOT NULL,
    record_id BIGINT NOT NULL,
    action TEXT NOT NULL, -- INSERT, UPDATE, DELETE
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changes JSONB,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Function to add audit fields to existing tables
DO $$
DECLARE
    table_rec RECORD;
BEGIN
    FOR table_rec IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_type = 'BASE TABLE'
          AND table_name NOT IN ('users', 'permissions', 'audit_log')
    LOOP
        -- Check if created_at column exists
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
              AND table_name = table_rec.table_name 
              AND column_name = 'created_at'
        ) THEN
            EXECUTE format('ALTER TABLE %I ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP', table_rec.table_name);
        END IF;
        
        -- Check if created_by column exists
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
              AND table_name = table_rec.table_name 
              AND column_name = 'created_by'
        ) THEN
            EXECUTE format('ALTER TABLE %I ADD COLUMN created_by BIGINT', table_rec.table_name);
        END IF;
        
        -- Check if last_updated column exists
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
              AND table_name = table_rec.table_name 
              AND column_name = 'last_updated'
        ) THEN
            EXECUTE format('ALTER TABLE %I ADD COLUMN last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP', table_rec.table_name);
        END IF;
        
        -- Check if last_updated_by column exists
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
              AND table_name = table_rec.table_name 
              AND column_name = 'last_updated_by'
        ) THEN
            EXECUTE format('ALTER TABLE %I ADD COLUMN last_updated_by BIGINT', table_rec.table_name);
        END IF;
        
        -- Add foreign key constraint for created_by with exception handling
        BEGIN
            EXECUTE format('ALTER TABLE %I ADD CONSTRAINT fk_%I_created_by FOREIGN KEY (created_by) REFERENCES users(id)', table_rec.table_name, table_rec.table_name);
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END;

        -- Add foreign key constraint for last_updated_by with exception handling
        BEGIN
            EXECUTE format('ALTER TABLE %I ADD CONSTRAINT fk_%I_last_updated_by FOREIGN KEY (last_updated_by) REFERENCES users(id)', table_rec.table_name, table_rec.table_name);
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END;
    END LOOP;
END $$;

-- Create default admin user
INSERT INTO users (username, password_hash, full_name, role, is_active)
SELECT 'admin', '$2b$12$1xxxxxxxxxxxxxxxxxxxxuZLbwxnpY0o58unSvIPxddLxGystU.', 'Administrator', 'admin', TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = 'admin'
);

-- Create default permissions
INSERT INTO permissions (role, resource, can_create, can_read, can_update, can_delete)
VALUES 
('admin', 'users', TRUE, TRUE, TRUE, TRUE),
('admin', 'supplier', TRUE, TRUE, TRUE, TRUE),
('admin', 'party', TRUE, TRUE, TRUE, TRUE),
('admin', 'bank', TRUE, TRUE, TRUE, TRUE),
('admin', 'transport', TRUE, TRUE, TRUE, TRUE),
('admin', 'register_entry', TRUE, TRUE, TRUE, TRUE),
('admin', 'memo_entry', TRUE, TRUE, TRUE, TRUE),
('admin', 'order_form', TRUE, TRUE, TRUE, TRUE),
('admin', 'item', TRUE, TRUE, TRUE, TRUE),
('admin', 'item_entry', TRUE, TRUE, TRUE, TRUE),
('admin', 'audit_log', FALSE, TRUE, FALSE, FALSE),
('user', 'supplier', FALSE, TRUE, FALSE, FALSE),
('user', 'party', FALSE, TRUE, FALSE, FALSE),
('user', 'bank', FALSE, TRUE, FALSE, FALSE),
('user', 'transport', FALSE, TRUE, FALSE, FALSE),
('user', 'register_entry', TRUE, TRUE, TRUE, FALSE),
('user', 'memo_entry', TRUE, TRUE, TRUE, FALSE),
('user', 'order_form', TRUE, TRUE, TRUE, FALSE),
('user', 'item', FALSE, TRUE, FALSE, FALSE),
('user', 'item_entry', TRUE, TRUE, TRUE, FALSE)
ON CONFLICT (role, resource) DO NOTHING;
