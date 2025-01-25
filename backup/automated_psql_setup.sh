#!/usr/bin/env bash
set -e

# ----------------------------------
# CONFIGURATION
# ----------------------------------
PG_PASSWORD="your_password_here"   # <--- Replace with a secure password
PG_VERSION="14"                    # <--- Adjust PostgreSQL version as desired
BACKUP_SCRIPT="./restore_backup.sh" # <--- Path to your backup restore script (optional)
HCA_DB="hca"                       # <--- Name of your default database
ZSHRC_FILE="${HOME}/.zshrc"
# ----------------------------------


# Check if the user has updated the default password
if [[ "${PG_PASSWORD}" == "your_password_here" ]]; then
  echo "ERROR: You must update the PG_PASSWORD variable with a secure password before running this script."
  exit 1
fi

echo "Starting automated PostgreSQL setup..."

# Detect OS (simple check for macOS vs. Debian/Ubuntu)
# Extend or modify for other distributions (e.g., Fedora, Arch).
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  echo "Detected macOS..."
  # Check if Homebrew is installed
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo "Please follow any on-screen instructions and then re-run this script."
    exit 1
  fi

  # Check if PostgreSQL is installed
  if ! command -v psql >/dev/null 2>&1; then
    echo "PostgreSQL not found. Installing via Homebrew..."
    brew update
    brew install postgresql@$PG_VERSION
    brew link postgresql@$PG_VERSION --force --overwrite
  else
    echo "PostgreSQL is already installed."
  fi

  echo "Starting/upgrading PostgreSQL service..."
  brew services start postgresql@$PG_VERSION

else
  # Assume Debian/Ubuntu
  echo "Detected Linux (Debian/Ubuntu)..."
  if ! command -v psql >/dev/null 2>&1; then
    echo "PostgreSQL not found. Installing via apt..."
    sudo apt-get update
    sudo apt-get install -y "postgresql-$PG_VERSION" "postgresql-client-$PG_VERSION"
  else
    echo "PostgreSQL is already installed."
  fi

  echo "Starting PostgreSQL service..."
  sudo systemctl enable postgresql
  sudo systemctl start postgresql
fi

# Wait a few seconds for PostgreSQL to be up
sleep 3

# ----------------------------------
# CREATE/ALTER THE POSTGRES ROLE
# ----------------------------------
echo "Configuring role 'postgres'..."

# We try to create the role if it doesn't exist, otherwise alter it
# (Wrap in an anonymous block to avoid errors if role already exists)
psql -d postgres -X -v ON_ERROR_STOP=1 <<EOF
DO \$\$
BEGIN
  IF NOT EXISTS (
    SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres'
  ) THEN
    CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD '$PG_PASSWORD';
  ELSE
    ALTER ROLE postgres WITH SUPERUSER LOGIN PASSWORD '$PG_PASSWORD';
  END IF;
  ALTER ROLE postgres WITH CREATEDB;
END
\$\$;
EOF

echo "Role 'postgres' is ready."

# ----------------------------------
# UPDATE ~/.zshrc WITH ENV VARIABLES
# ----------------------------------
echo "Updating ${ZSHRC_FILE} with PG environment variables..."

# Add or update lines for PGUSER, PGDATABASE
# (This ensures when you type `psql`, it defaults to your chosen user/db)

# 1. Ensure PGUSER is set to "postgres"
if grep -q "export PGUSER=" "$ZSHRC_FILE"; then
  # Update the existing line
  sed -i.bak "s|^export PGUSER=.*|export PGUSER=postgres|" "$ZSHRC_FILE"
else
  echo "export PGUSER=postgres" >> "$ZSHRC_FILE"
fi

# 2. Ensure PGDATABASE is set to "hca" (or your database)
if grep -q "export PGDATABASE=" "$ZSHRC_FILE"; then
  # Update the existing line
  sed -i.bak "s|^export PGDATABASE=.*|export PGDATABASE=${HCA_DB}|" "$ZSHRC_FILE"
else
  echo "export PGDATABASE=${HCA_DB}" >> "$ZSHRC_FILE"
fi

# 3. Optionally store password in .zshrc (INSECURE, consider alternatives)
# If you want to avoid manual password entry on each psql connection,
# you either need "trust" authentication or a .pgpass file.
# We'll demonstrate .pgpass approach (safer than environment variable).
PGPASS_FILE="${HOME}/.pgpass"
PGHOST="localhost"
PGPORT="5432"

echo "Updating ~/.pgpass file for password authentication (if needed)..."
touch "$PGPASS_FILE"
chmod 600 "$PGPASS_FILE"

# Remove existing lines for this host/port combo, then append
sed -i.bak "/^${PGHOST}:${PGPORT}:.*/d" "$PGPASS_FILE"
# Add a line: host:port:database:user:password
# Using wildcard for database to handle any DB on that host/port for user "postgres"
echo "${PGHOST}:${PGPORT}:*:${PGUSER}:${PG_PASSWORD}" >> "$PGPASS_FILE"

# Cleanup backup files from sed
rm -f "${ZSHRC_FILE}.bak" "${PGPASS_FILE}.bak"

echo "Sourcing ${ZSHRC_FILE} to apply changes..."
# shellcheck disable=SC1090
source "${ZSHRC_FILE}"

# ----------------------------------
# (OPTIONAL) RUN BACKUP RESTORE SCRIPT
# ----------------------------------
echo "PSQL is setup, now please restore the backup"
