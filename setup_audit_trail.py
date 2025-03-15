#!/usr/bin/env python
"""
Script to set up the audit trail and user management database schema.
"""
from API_Database.setup_audit_trail import setup_audit_trail

if __name__ == "__main__":
    print("Setting up audit trail and user management system...")
    setup_audit_trail()
    print("Setup complete!")
