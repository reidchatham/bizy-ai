#!/bin/bash
# Setup PostgreSQL database for Bizy AI
# Creates database and user if they don't exist

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🐘 PostgreSQL Setup for Bizy AI${NC}"
echo "================================"
echo ""

# Load environment variables
if [ -f "../.env" ]; then
    echo "📂 Loading .env file..."
    export $(cat ../.env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found, using defaults${NC}"
fi

# Get database configuration
POSTGRES_USER=${POSTGRES_USER:-bizy}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-bizy_dev_password}
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_DB=${POSTGRES_DB:-bizy_dev}

echo "📋 Database Configuration:"
echo "   Host: $POSTGRES_HOST:$POSTGRES_PORT"
echo "   Database: $POSTGRES_DB"
echo "   User: $POSTGRES_USER"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL not found${NC}"
    echo ""
    echo "Install PostgreSQL first:"
    echo "  macOS:   brew install postgresql@16"
    echo "  Ubuntu:  sudo apt-get install postgresql-16"
    echo "  Docker:  docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16"
    exit 1
fi

echo -e "${GREEN}✓ PostgreSQL found${NC}"
echo ""

# Check if PostgreSQL is running
if ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL not running${NC}"
    echo ""
    echo "Start PostgreSQL:"
    echo "  macOS:   brew services start postgresql@16"
    echo "  Ubuntu:  sudo systemctl start postgresql"
    echo "  Docker:  docker start <container-id>"
    exit 1
fi

echo -e "${GREEN}✓ PostgreSQL is running${NC}"
echo ""

# Create database and user
echo "🔧 Setting up database..."

# Use postgres user for setup (may require password)
PGPASSWORD=${POSTGRES_ADMIN_PASSWORD:-postgres} psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$POSTGRES_USER') THEN
        CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
        RAISE NOTICE 'Created user: $POSTGRES_USER';
    ELSE
        RAISE NOTICE 'User already exists: $POSTGRES_USER';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;

\c $POSTGRES_DB

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO $POSTGRES_USER;

EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database setup complete${NC}"
else
    echo -e "${RED}❌ Database setup failed${NC}"
    echo ""
    echo "If you got a password error, set POSTGRES_ADMIN_PASSWORD:"
    echo "  export POSTGRES_ADMIN_PASSWORD=your_postgres_password"
    exit 1
fi

echo ""
echo "================================"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "================================"
echo ""
echo "Database URL:"
echo "  postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
echo ""
echo "Test connection:"
echo "  psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB"
echo ""
echo "Next steps:"
echo "  1. Run Alembic migrations:"
echo "     cd /Users/reidchatham/Developer/business-agent/backend"
echo "     source venv/bin/activate"
echo "     alembic upgrade head"
echo ""
echo "  2. Or migrate from SQLite:"
echo "     python scripts/migrate_sqlite_to_postgres.py --backup"
echo ""
