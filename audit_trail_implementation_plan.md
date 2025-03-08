# Execution Plan: Audit Trail and User Management Implementation

## 1. Database Schema Changes

### 1.1 Create Users and Permissions Tables

```sql
-- Users table
CREATE SEQUENCE users_seq;
CREATE TABLE users (
    id INT DEFAULT NEXTVAL ('users_seq') PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
    last_updated_by INT
);

-- Permissions table
CREATE SEQUENCE permissions_seq;
CREATE TABLE permissions (
    id INT DEFAULT NEXTVAL ('permissions_seq') PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    can_create BOOLEAN DEFAULT FALSE,
    can_read BOOLEAN DEFAULT TRUE,
    can_update BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    UNIQUE(role, resource)
);

-- Audit log table
CREATE SEQUENCE audit_log_seq;
CREATE TABLE audit_log (
    id INT DEFAULT NEXTVAL ('audit_log_seq') PRIMARY KEY,
    user_id INT,
    table_name VARCHAR(100) NOT NULL,
    record_id INT NOT NULL,
    action VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    timestamp TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
    changes JSONB,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 1.2 Modify Existing Tables

For each table in the database, execute:

```sql
-- Example for supplier table (repeat for all tables)
ALTER TABLE supplier 
  ADD COLUMN created_at TIMESTAMP(0),
  ADD COLUMN created_by INT,
  ADD COLUMN last_updated_by INT,
  ADD CONSTRAINT fk_supplier_created_by FOREIGN KEY (created_by) REFERENCES users(id),
  ADD CONSTRAINT fk_supplier_last_updated_by FOREIGN KEY (last_updated_by) REFERENCES users(id);
```

## 2. User Management Implementation

### 2.1 Create User Model

Create `hca_backend/Individual/User.py`:
- Implement User class with authentication methods
- Include password hashing using bcrypt
- Add role-based permission checking

### 2.2 Update Authentication System

Modify `app.py`:
- Replace hardcoded admin credentials with database authentication
- Include user role and permissions in JWT token payload
- Add token refresh functionality

### 2.3 Create User Management API Endpoints

Add to `app.py`:
- User registration (admin only)
- User login
- User profile management
- Role and permission management (admin only)

## 3. Audit Trail Implementation

### 3.1 Update Database Connector

Modify `psql/db_connector.py`:
- Add current_user_id parameter to execute_query function
- Modify SQL queries to include audit fields
- Implement audit log recording

### 3.2 Create Audit Log Functions

Create `API_Database/audit_log.py`:
- Implement functions to record changes to the audit_log table
- Create functions to retrieve audit history for records

## 4. Entity Class Modifications

### 4.1 Update Base Entity Classes

Modify `Entities/Entry.py` and `Individual/Individual.py`:
- Add audit trail fields
- Update CRUD methods to include current user information
- Implement methods to retrieve audit history

### 4.2 Update Entity-Specific Classes

Update all entity classes to:
- Pass current user ID to database operations
- Include audit fields in serialization/deserialization

## 5. API Endpoint Updates

### 5.1 Add Authentication to Endpoints

Modify all API endpoints to:
- Require authentication
- Extract current user from JWT token
- Pass current user ID to database operations

### 5.2 Add Permission Checking

Implement middleware to:
- Check user permissions before executing operations
- Return appropriate error messages for unauthorized actions

### 5.3 Add Audit Trail Endpoints

Create new endpoints to:
- Retrieve audit history for records
- Search and filter audit logs

## 6. Testing and Deployment

### 6.1 Create Test Cases

Write tests for:
- User authentication and authorization
- Audit trail recording
- Permission checking

### 6.2 Database Migration

Create a migration script to:
- Create new tables
- Modify existing tables
- Set up initial admin user and permissions

### 6.3 Deployment

- Update requirements.txt with new dependencies
- Deploy database changes
- Deploy application updates
