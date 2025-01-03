#!/bin/bash

DB_USER="postgres"
DB_NAME="hca_backup"
BACKUP_FILE="/Users/vaibhavholani/development/business/holani_cloth_agency/backups/backup_24_Dec_2024.sql"

psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"
psql -U "$DB_USER" "$DB_NAME" < "$BACKUP_FILE"

echo "Database $DB_NAME restored successfully from $BACKUP_FILE."
