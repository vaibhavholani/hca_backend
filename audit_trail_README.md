# Audit Trail and User Management System

This document provides information on the audit trail and user management system implemented in the HCA backend application.

## Overview

The audit trail and user management system provides the following features:

1. **User Authentication**: Secure authentication using JWT tokens
2. **Role-Based Access Control**: Different permissions for different user roles
3. **Audit Trail**: Tracking of all database changes with user information
4. **API Endpoints**: Endpoints for user management and audit trail retrieval

## Setup

To set up the audit trail and user management system, follow these steps:

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the setup script:
   ```bash
   python setup_audit_trail.py
   ```

This will create the necessary database tables and set up the initial admin user.

## User Management

### User Roles

The system supports the following user roles:

- **admin**: Full access to all resources and operations
- **user**: Limited access based on permissions

### Default Admin User

The setup script creates a default admin user with the following credentials:

- Username: `admin`
- Password: `admin5555`

**Important**: Change the default admin password after setup!

### User Management API Endpoints

The following API endpoints are available for user management:

- `POST /api/login`: Authenticate a user and get JWT tokens
- `POST /api/token/refresh`: Refresh the JWT access token
- `GET /api/users`: Get all users (admin only)
- `GET /api/users/{user_id}`: Get a user by ID (admin only)
- `POST /api/users`: Create a new user (admin only)
- `PUT /api/users/{user_id}`: Update a user (admin only)
- `DELETE /api/users/{user_id}`: Delete a user (admin only)
- `GET /api/profile`: Get the current user's profile
- `PUT /api/profile`: Update the current user's profile

### Authentication

To authenticate, send a POST request to `/api/login` with the following JSON body:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

The response will include an access token and a refresh token:

```json
{
  "status": "okay",
  "access_token": "your_access_token",
  "refresh_token": "your_refresh_token",
  "user": {
    "id": 1,
    "username": "your_username",
    "full_name": "Your Name",
    "role": "admin"
  }
}
```

To authenticate API requests, include the access token in the Authorization header:

```
Authorization: Bearer your_access_token
```

## Audit Trail

The audit trail system tracks all changes to the database, including:

- Who made the change (user ID)
- When the change was made (timestamp)
- What was changed (table name, record ID, action)
- Details of the change (old and new values)

### Audit Trail API Endpoints

The following API endpoints are available for retrieving audit logs:

- `GET /api/audit/history/{table_name}/{record_id}`: Get the audit history for a specific record
- `GET /api/audit/search`: Search audit logs with various filters

### Audit History Example

To get the audit history for a specific record, send a GET request to `/api/audit/history/{table_name}/{record_id}`:

```
GET /api/audit/history/supplier/123
```

The response will include a list of audit log entries:

```json
{
  "status": "okay",
  "history": [
    {
      "id": 1,
      "action": "UPDATE",
      "timestamp": "2025-03-08T12:34:56",
      "changes": {
        "name": {
          "old": "Old Name",
          "new": "New Name"
        },
        "address": {
          "old": "Old Address",
          "new": "New Address"
        }
      },
      "username": "admin",
      "full_name": "Administrator"
    },
    {
      "id": 2,
      "action": "INSERT",
      "timestamp": "2025-03-07T10:11:12",
      "changes": {
        "name": "Initial Name",
        "address": "Initial Address"
      },
      "username": "admin",
      "full_name": "Administrator"
    }
  ]
}
```

### Search Audit Logs Example

To search audit logs, send a GET request to `/api/audit/search` with query parameters:

```
GET /api/audit/search?user_id=1&table_name=supplier&action=UPDATE&start_date=2025-03-01&end_date=2025-03-08
```

The response will include a list of matching audit log entries:

```json
{
  "status": "okay",
  "logs": [
    {
      "id": 1,
      "table_name": "supplier",
      "record_id": 123,
      "action": "UPDATE",
      "timestamp": "2025-03-08T12:34:56",
      "changes": {
        "name": {
          "old": "Old Name",
          "new": "New Name"
        },
        "address": {
          "old": "Old Address",
          "new": "New Address"
        }
      },
      "username": "admin",
      "full_name": "Administrator"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

## Implementation Details

### Database Schema

The system uses the following database tables:

- `users`: Stores user information
- `permissions`: Stores role-based permissions
- `audit_log`: Stores audit trail entries

All existing tables have been modified to include the following audit fields:

- `created_at`: When the record was created
- `created_by`: Who created the record
- `last_updated`: When the record was last updated
- `last_updated_by`: Who last updated the record

### Code Structure

The audit trail and user management system is implemented in the following files:

- `API_Database/audit_trail_schema.sql`: SQL schema for the audit trail and user management tables
- `API_Database/setup_audit_trail.py`: Script to set up the database schema
- `API_Database/audit_log.py`: Functions for recording and retrieving audit logs
- `Individual/User.py`: User model with authentication and permission checking
- `psql/db_connector.py`: Database connector with audit trail functionality
- `Entities/Entry.py`: Base entity class with audit trail fields
- `Individual/Individual.py`: Base individual class with audit trail fields
- `app.py`: API endpoints for user management and audit trail retrieval

## Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens expire after 1 hour (access token) or 30 days (refresh token)
- Role-based access control restricts access to sensitive operations
- Audit trail provides accountability for all database changes
