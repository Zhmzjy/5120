#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Melbourne Parking System - Complete Database Setup (Windows Git Bash)"
echo "========================================================================="

# ---- Env / encoding (avoid garbled CN messages) ----
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# ---- Config ----
DB_HOST="127.0.0.1"
DB_PORT="5432"
DB_NAME="melbourne_parking_system"
DB_USER="melbourne_parking"
DB_PASS="zjy0312!"
INIT_SQL="init_database.sql"

# Add PostgreSQL bin to PATH if present
if [ -d "/c/Program Files/PostgreSQL/17/bin" ]; then
  export PATH="$PATH:/c/Program Files/PostgreSQL/17/bin"
fi

# Check current dir
if [[ ! -f "$INIT_SQL" ]]; then
  echo "❌ Please run this script from the database directory (where $INIT_SQL is)."
  exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Check psql
if ! command -v psql >/dev/null 2>&1; then
  echo "❌ psql not found. Add PostgreSQL bin to PATH first:"
  echo '   export PATH="$PATH:/c/Program Files/PostgreSQL/17/bin"'
  exit 1
fi

echo "Step 1: PostgreSQL already installed → skipping installation step."
echo ""

# If PGPASSWORD not provided, ask once (hidden input)
if [[ -z "${PGPASSWORD:-}" ]]; then
  read -rsp "🔑 Enter postgres superuser password: " PGPASSWORD
  echo ""
fi
export PGPASSWORD

# ---- Step 2: Create DB & user (no transaction) ----
echo "Step 2: Ensure database and user exist..."

# 2.1 ensure database
if psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
  echo "   • Database $DB_NAME already exists."
else
  echo "   • Creating database $DB_NAME ..."
  psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE DATABASE $DB_NAME"
fi

# 2.2 ensure user
if psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
  echo "   • Role $DB_USER already exists."
else
  echo "   • Creating role $DB_USER ..."
  psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS'"
fi

# 2.3 grant privileges
psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER"
echo "✅ Database & user ensured."
echo ""

# ---- Step 3: Apply schema as application user ----
echo "Step 3: Creating database schema..."
PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$INIT_SQL"
echo "✅ Schema applied."
echo ""

# ---- Step 4: Python deps ----
echo "Step 4: Installing Python dependencies..."
py -m pip install --upgrade pip >/dev/null
py -m pip install psycopg2-binary pandas
echo "✅ Python deps installed."
echo ""

# ---- Step 5: Import CSV seeds (optional) ----
if [[ -d "seeds" && -f "seeds/import_csv_data.py" ]]; then
  echo "Step 5: Importing CSV data..."
  export DATABASE_URL="postgresql+psycopg2://$DB_USER:$(python - <<PY
import urllib.parse; print(urllib.parse.quote("$DB_PASS"))
PY
)@$DB_HOST:$DB_PORT/$DB_NAME"
  (cd seeds && py import_csv_data.py)
  echo "✅ CSV data imported."
else
  echo "Step 5: No seeds to import (skipped)."
fi
echo ""

# ---- Step 6: Test connection (optional) ----
if [[ -f "test_connection.py" ]]; then
  echo "Step 6: Testing database connection..."
  export DATABASE_URL="postgresql+psycopg2://$DB_USER:$(python - <<PY
import urllib.parse; print(urllib.parse.quote("$DB_PASS"))
PY
)@$DB_HOST:$DB_PORT/$DB_NAME"
  py test_connection.py
  echo "✅ DB connection test passed."
else
  echo "Step 6: No test_connection.py (skipped)."
fi

echo ""
echo "🎉 Setup completed!"
ENC_PASS=$(python - <<PY
import urllib.parse; print(urllib.parse.quote("$DB_PASS"))
PY
)
echo "🔗 Put this in your backend .env:"
echo "   DATABASE_URL=postgresql+psycopg2://$DB_USER:$ENC_PASS@$DB_HOST:$DB_PORT/$DB_NAME"