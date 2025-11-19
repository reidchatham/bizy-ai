# SQLite to PostgreSQL Migration Guide

**Task:** Phase 3, Task 39 - Create database migration script
**Date:** November 18, 2025
**Status:** Complete

---

## Overview

This guide explains how to migrate your existing Bizy AI SQLite database (`~/.business-agent/tasks.db`) to PostgreSQL for the Phase 3 web interface.

**Migration Process:**
1. Export data from SQLite
2. Create default user in PostgreSQL
3. Transform data (add user_id, convert timestamps to UTC)
4. Import to PostgreSQL
5. Verify data integrity

**Time Required:** ~15 minutes
**Downtime Required:** Yes (CLI will be unavailable during migration)

---

## Prerequisites

### 1. PostgreSQL Installed

**macOS (Homebrew):**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-16
sudo systemctl start postgresql
```

**Docker:**
```bash
docker run -d \
  --name bizy-postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=bizy \
  -e POSTGRES_DB=bizy_dev \
  postgres:16-alpine

# Verify it's running
docker ps | grep bizy-postgres
```

### 2. Backend Dependencies Installed

```bash
cd backend
source venv/bin/activate
pip install -r requirements-dev.txt  # Includes psycopg2-binary
```

### 3. Environment Variables Configured

Edit `backend/.env`:
```bash
# PostgreSQL Configuration
POSTGRES_USER=bizy
POSTGRES_PASSWORD=bizy_dev_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bizy_dev

# Or use a single DATABASE_URL
DATABASE_URL=postgresql://bizy:bizy_dev_password@localhost:5432/bizy_dev

# Default migration user
DEFAULT_USER_EMAIL=admin@bizy.local
DEFAULT_USER_USERNAME=admin
```

---

## Migration Methods

### Method 1: Automated Migration Script (Recommended)

**One-command migration with backup:**

```bash
cd backend
source venv/bin/activate

# 1. Setup PostgreSQL database
./scripts/setup_postgres.sh

# 2. Run migration with automatic backup
python scripts/migrate_sqlite_to_postgres.py --backup

# 3. Verify migration
python scripts/verify_migration.py
```

**What it does:**
- ✅ Backs up your SQLite database
- ✅ Creates PostgreSQL tables
- ✅ Creates default admin user
- ✅ Migrates all tasks and goals
- ✅ Converts timestamps to UTC
- ✅ Verifies data integrity
- ✅ Provides rollback backup

**Output:**
```
=============================== ===============================
SQLite to PostgreSQL Migration
===============================================================

📂 SQLite database: /Users/you/.business-agent/tasks.db
🐘 PostgreSQL URL: localhost:5432/bizy_dev
📦 Creating backup: /Users/you/.business-agent/tasks_backup_20251118_143022.db
✓ Backup created successfully

📂 Connecting to SQLite...
✓ Connected to SQLite

🐘 Connecting to PostgreSQL...
✓ Connected to PostgreSQL

👤 Creating default user: admin (admin@bizy.local)
✓ Created user (ID: 1)
📝 IMPORTANT: Temporary password: xK9mQ3pL7wR2nV4s
   Please change this password after migration!

🎯 Migrating goals...
   Found 1 goals in SQLite
✓ Migrated 1 goals

📋 Migrating tasks...
   Found 67 tasks in SQLite
✓ Migrated 67 tasks

🔍 Verifying migration...
✓ Task count matches: 67
✓ Goal count matches: 1
✓ All task-goal relationships valid
✓ All records have user_id

============================================================
Migration Summary
============================================================
✓ Users created: 1
✓ Tasks migrated: 67
✓ Goals migrated: 1
============================================================

✅ Migration completed successfully!

📝 Next steps:
   1. Test the PostgreSQL database
   2. Update backend/.env to use PostgreSQL:
      DATABASE_URL=postgresql://bizy:bizy_dev_password@localhost:5432/bizy_dev
   3. Login with: admin@bizy.local
   4. Change your password immediately!
```

### Method 2: Manual Step-by-Step Migration

**Step 1: Backup SQLite Database**
```bash
cp ~/.business-agent/tasks.db ~/.business-agent/tasks_backup_$(date +%Y%m%d).db
```

**Step 2: Setup PostgreSQL**
```bash
cd backend
./scripts/setup_postgres.sh
```

**Step 3: Create Initial Migration**
```bash
source venv/bin/activate

# Create initial migration
alembic revision --autogenerate -m "Initial schema with users, tasks, goals"

# Review migration file (check it makes sense)
cat alembic/versions/*_initial_schema.py

# Apply migration
alembic upgrade head
```

**Step 4: Run Migration Script**
```bash
# Dry run first (doesn't commit changes)
python scripts/migrate_sqlite_to_postgres.py --dry-run

# If dry run looks good, run for real
python scripts/migrate_sqlite_to_postgres.py
```

**Step 5: Verify Migration**
```bash
# Check record counts
python scripts/verify_migration.py

# Manual verification via psql
psql -h localhost -U bizy -d bizy_dev -c "SELECT COUNT(*) FROM tasks;"
psql -h localhost -U bizy -d bizy_dev -c "SELECT COUNT(*) FROM goals;"
psql -h localhost -U bizy -d bizy_dev -c "SELECT * FROM users;"
```

**Step 6: Update Configuration**
```bash
# Edit backend/.env
nano backend/.env

# Change DATABASE_URL to point to PostgreSQL
DATABASE_URL=postgresql://bizy:bizy_dev_password@localhost:5432/bizy_dev

# Test backend connection
python -c "from models import Base; from sqlalchemy import create_engine; import os; engine = create_engine(os.getenv('DATABASE_URL')); print('✓ Connection successful')"
```

---

## Migration Script Options

### Command-Line Flags

```bash
python scripts/migrate_sqlite_to_postgres.py [OPTIONS]

Options:
  --dry-run              Run migration without committing (for testing)
  --backup               Create backup of SQLite database before migration
  --sqlite-path PATH     Custom path to SQLite database
  --postgres-url URL     Custom PostgreSQL connection URL

Examples:
  # Dry run to test
  python scripts/migrate_sqlite_to_postgres.py --dry-run

  # Production migration with backup
  python scripts/migrate_sqlite_to_postgres.py --backup

  # Custom database paths
  python scripts/migrate_sqlite_to_postgres.py \
    --sqlite-path ~/my_tasks.db \
    --postgres-url postgresql://user:pass@host:5432/db
```

### Environment Variables

```bash
# SQLite source
SQLITE_DB_PATH=~/.business-agent/tasks.db

# PostgreSQL target
DATABASE_URL=postgresql://bizy:password@localhost:5432/bizy_dev

# Or individual components
POSTGRES_USER=bizy
POSTGRES_PASSWORD=bizy_dev_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bizy_dev

# Default user creation
DEFAULT_USER_EMAIL=admin@bizy.local
DEFAULT_USER_USERNAME=admin
```

---

## Data Transformations

### What Changes During Migration

| Field | SQLite | PostgreSQL | Transformation |
|-------|--------|------------|----------------|
| **Tasks** | | | |
| `user_id` | ❌ None | ✅ Required | Assigned to default user |
| `created_at` | Local time | UTC | Converted to UTC |
| `updated_at` | ❌ None | ✅ Auto | Set to now() |
| `completed_at` | Local time | UTC | Converted to UTC |
| **Goals** | | | |
| `user_id` | ❌ None | ✅ Required | Assigned to default user |
| `created_at` | UTC | UTC | No change |
| `updated_at` | UTC | UTC | No change |
| `completed_at` | ❌ None | ✅ Optional | Set to NULL |

### Timestamp Conversion

**Issue:** SQLite database has mixed local/UTC timestamps

**Solution:** Migration script uses heuristic conversion:
```python
def convert_local_to_utc(dt: datetime) -> datetime:
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Naive datetime - assume UTC
        return dt.replace(tzinfo=timezone.utc)
    # Has timezone - convert to UTC
    return dt.astimezone(timezone.utc).replace(tzinfo=None)
```

**Result:** All timestamps in PostgreSQL are UTC (naive datetime objects)

---

## Verification Checklist

After migration, verify:

### 1. Record Counts Match

```sql
-- In psql
\c bizy_dev

SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL
SELECT 'goals', COUNT(*) FROM goals
UNION ALL
SELECT 'users', COUNT(*) FROM users;
```

Compare with SQLite:
```bash
sqlite3 ~/.business-agent/tasks.db "SELECT 'tasks', COUNT(*) FROM tasks UNION ALL SELECT 'goals', COUNT(*) FROM goals;"
```

### 2. All Records Have user_id

```sql
-- Should return 0
SELECT COUNT(*) FROM tasks WHERE user_id IS NULL;
SELECT COUNT(*) FROM goals WHERE user_id IS NULL;
```

### 3. Foreign Key Relationships Valid

```sql
-- Should return 0 (no orphaned tasks)
SELECT COUNT(*)
FROM tasks t
LEFT JOIN goals g ON t.parent_goal_id = g.id
WHERE t.parent_goal_id IS NOT NULL AND g.id IS NULL;
```

### 4. Timestamps Look Reasonable

```sql
-- Check timestamp ranges
SELECT
  MIN(created_at) as earliest,
  MAX(created_at) as latest
FROM tasks;

-- Should be roughly the same as SQLite
```

### 5. Sample Data Looks Correct

```sql
-- Compare a few tasks
SELECT id, title, status, created_at, user_id
FROM tasks
ORDER BY created_at DESC
LIMIT 10;
```

Compare with SQLite:
```bash
sqlite3 ~/.business-agent/tasks.db "SELECT id, title, status, created_at FROM tasks ORDER BY created_at DESC LIMIT 10;"
```

---

## Rollback Procedure

### If Migration Fails

**Option 1: Use Backup (if --backup was used)**
```bash
# Your original database is still at:
ls ~/.business-agent/tasks_backup_*.db

# The CLI still uses the original database
bizy task list  # Should still work

# PostgreSQL database can be dropped and recreated:
psql -U postgres -c "DROP DATABASE bizy_dev;"
psql -U postgres -c "CREATE DATABASE bizy_dev OWNER bizy;"
```

**Option 2: Revert .env Changes**
```bash
# Edit backend/.env
nano backend/.env

# Change back to SQLite
DATABASE_URL=sqlite:///~/.business-agent/tasks.db

# Restart backend
./run.sh
```

**Option 3: Drop PostgreSQL Database**
```bash
# Drop and recreate
psql -U postgres -c "DROP DATABASE bizy_dev;"
./scripts/setup_postgres.sh

# Try migration again
python scripts/migrate_sqlite_to_postgres.py --backup
```

---

## Troubleshooting

### Error: "psql: could not connect to server"

**Cause:** PostgreSQL not running

**Solution:**
```bash
# macOS
brew services start postgresql@16

# Ubuntu
sudo systemctl start postgresql

# Docker
docker start bizy-postgres
```

### Error: "FATAL: password authentication failed"

**Cause:** Wrong PostgreSQL password

**Solution:**
```bash
# Reset postgres user password
psql -U postgres -c "ALTER USER bizy WITH PASSWORD 'bizy_dev_password';"

# Or update your .env file to match actual password
nano backend/.env
```

### Error: "database bizy_dev does not exist"

**Cause:** Database not created yet

**Solution:**
```bash
cd backend
./scripts/setup_postgres.sh
```

### Error: "column user_id does not exist"

**Cause:** Alembic migrations not applied

**Solution:**
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### Warning: "Task count mismatch"

**Cause:** Some tasks failed to migrate

**Solution:**
```bash
# Check migration errors
python scripts/migrate_sqlite_to_postgres.py 2>&1 | grep ERROR

# Try again with --dry-run to see issues
python scripts/migrate_sqlite_to_postgres.py --dry-run
```

### Warning: "Orphaned tasks"

**Cause:** Tasks reference goals that don't exist

**Solution:**
```sql
-- Find orphaned tasks
SELECT t.id, t.title, t.parent_goal_id
FROM tasks t
LEFT JOIN goals g ON t.parent_goal_id = g.id
WHERE t.parent_goal_id IS NOT NULL AND g.id IS NULL;

-- Fix by unlinking from goal
UPDATE tasks SET parent_goal_id = NULL
WHERE id IN (SELECT t.id FROM tasks t LEFT JOIN goals g ON t.parent_goal_id = g.id WHERE t.parent_goal_id IS NOT NULL AND g.id IS NULL);
```

---

## Post-Migration Tasks

### 1. Change Default User Password

```bash
# Option A: Via FastAPI backend (after auth endpoints implemented)
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Content-Type: application/json" \
  -d '{"old_password": "TEMP_PASSWORD_FROM_MIGRATION", "new_password": "your_secure_password"}'

# Option B: Via psql (for now)
psql -h localhost -U bizy -d bizy_dev

-- At psql prompt:
UPDATE users SET hashed_password = crypt('your_new_password', gen_salt('bf', 12)) WHERE email = 'admin@bizy.local';
```

### 2. Verify CLI Still Works with SQLite

```bash
# CLI still uses SQLite at ~/.business-agent/tasks.db
bizy task list
bizy goal list
bizy stats

# Should all work normally
```

### 3. Test Backend with PostgreSQL

```bash
cd backend
source venv/bin/activate

# Update .env to use PostgreSQL
echo "DATABASE_URL=postgresql://bizy:bizy_dev_password@localhost:5432/bizy_dev" >> .env

# Start backend
./run.sh

# Test in another terminal
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"bizy-ai-api","version":"0.1.0"}
```

### 4. Create Additional Users (Optional)

```sql
-- Via psql
psql -h localhost -U bizy -d bizy_dev

-- Create new user
INSERT INTO users (email, username, hashed_password, full_name, is_active, is_verified, created_at, updated_at)
VALUES (
  'user@example.com',
  'user',
  crypt('password123', gen_salt('bf', 12)),
  'Regular User',
  true,
  false,
  NOW(),
  NOW()
);
```

---

## Performance After Migration

### Expected Query Times (PostgreSQL)

| Query | SQLite | PostgreSQL |
|-------|--------|------------|
| Dashboard load | 800ms | <100ms |
| Task list (user) | 200ms | <50ms |
| Goal breakdown | 500ms | <200ms |
| Analytics | 1-2s | <500ms |

### Index Usage

```sql
-- Verify indexes are being used
EXPLAIN ANALYZE SELECT * FROM tasks WHERE user_id = 1 AND status = 'pending';

-- Should show "Index Scan using ix_tasks_user_status"
```

---

## Next Steps After Migration

1. ✅ **Task 39 Complete** - Migration script created
2. 🔜 **Task 40** - Implement authentication endpoints
3. 🔜 **Task 41** - Implement task CRUD API
4. 🔜 **Task 42** - Implement goal CRUD API
5. 🔜 **Task 44** - Write backend API tests

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy PostgreSQL Dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)

---

**Document Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Status:** Complete ✅
