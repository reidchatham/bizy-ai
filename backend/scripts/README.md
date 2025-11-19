# Backend Migration Scripts

Scripts for migrating Bizy AI from SQLite to PostgreSQL and managing the database.

---

## Available Scripts

### 1. `setup_postgres.sh` - PostgreSQL Database Setup

Creates PostgreSQL database and user for Bizy AI.

**Usage:**
```bash
./scripts/setup_postgres.sh
```

**What it does:**
- Checks if PostgreSQL is installed and running
- Creates database user (from POSTGRES_USER env var)
- Creates database (from POSTGRES_DB env var)
- Grants all privileges
- Tests connection

**Requirements:**
- PostgreSQL 14+ installed
- PostgreSQL server running
- Access to `postgres` superuser account

**Environment Variables:**
```bash
POSTGRES_USER=bizy              # Database user to create
POSTGRES_PASSWORD=password      # Password for user
POSTGRES_HOST=localhost         # PostgreSQL host
POSTGRES_PORT=5432              # PostgreSQL port
POSTGRES_DB=bizy_dev            # Database name
POSTGRES_ADMIN_PASSWORD=postgres # Superuser password (if needed)
```

---

### 2. `migrate_sqlite_to_postgres.py` - Data Migration

Migrates all data from SQLite to PostgreSQL.

**Usage:**
```bash
# Dry run (test without committing)
python scripts/migrate_sqlite_to_postgres.py --dry-run

# Production migration with backup
python scripts/migrate_sqlite_to_postgres.py --backup

# Custom paths
python scripts/migrate_sqlite_to_postgres.py \
  --sqlite-path ~/custom/path.db \
  --postgres-url postgresql://user:pass@host/db
```

**What it does:**
- ✅ Creates backup of SQLite database (if --backup)
- ✅ Connects to both databases
- ✅ Creates default admin user in PostgreSQL
- ✅ Migrates all goals (first, since tasks reference them)
- ✅ Migrates all tasks
- ✅ Converts timestamps from local to UTC
- ✅ Assigns all data to default user
- ✅ Verifies migration integrity
- ✅ Provides detailed summary

**Options:**
- `--dry-run` - Test migration without committing changes
- `--backup` - Create timestamped backup before migration
- `--sqlite-path PATH` - Custom SQLite database path
- `--postgres-url URL` - Custom PostgreSQL connection URL

**Environment Variables:**
```bash
SQLITE_DB_PATH=~/.business-agent/tasks.db     # SQLite source
DATABASE_URL=postgresql://user:pass@host/db   # PostgreSQL target
DEFAULT_USER_EMAIL=admin@bizy.local           # Default user email
DEFAULT_USER_USERNAME=admin                    # Default username
```

**Output Example:**
```
============================================================
SQLite to PostgreSQL Migration
============================================================
📂 SQLite database: /Users/you/.business-agent/tasks.db
🐘 PostgreSQL URL: localhost:5432/bizy_dev
📦 Creating backup: tasks_backup_20251118_143022.db
✓ Backup created successfully

👤 Creating default user: admin (admin@bizy.local)
✓ Created user (ID: 1)
📝 IMPORTANT: Temporary password: xK9mQ3pL7wR2nV4s

🎯 Migrating goals...
✓ Migrated 1 goals

📋 Migrating tasks...
✓ Migrated 67 tasks

🔍 Verifying migration...
✓ Task count matches: 67
✓ Goal count matches: 1

============================================================
Migration Summary
============================================================
✓ Users created: 1
✓ Tasks migrated: 67
✓ Goals migrated: 1
============================================================

✅ Migration completed successfully!
```

---

### 3. `verify_migration.py` - Migration Verification

Verifies that migration was successful by comparing SQLite and PostgreSQL data.

**Usage:**
```bash
python scripts/verify_migration.py
```

**What it checks:**
- ✅ Record counts match (tasks, goals)
- ✅ All records have user_id
- ✅ Foreign key relationships valid
- ✅ Timestamps exist
- ✅ Sample data matches

**Output Example:**
```
============================================================
Migration Verification
============================================================
📂 SQLite: /Users/you/.business-agent/tasks.db
🐘 PostgreSQL: localhost:5432/bizy_dev
✓ Connected to SQLite
✓ Connected to PostgreSQL

📊 Checking record counts...
✓ Task count matches (67)
✓ Goal count matches (1)
✓ Users exist (1)

👤 Checking user relationships...
✓ All tasks have user_id
✓ All goals have user_id

🔗 Checking foreign key relationships...
✓ All task-goal relationships valid
✓ All task-user relationships valid
✓ All goal-user relationships valid

⏰ Checking timestamps...
✓ All tasks have created_at
✓ All goals have created_at

🔍 Comparing sample data...
✓ Sample task data matches

============================================================
✅ All verification checks passed!
============================================================
```

**Exit Codes:**
- `0` - All checks passed
- `1` - Some checks failed

---

## Complete Migration Workflow

### Step 1: Setup PostgreSQL

```bash
cd backend

# Make sure PostgreSQL is running
brew services start postgresql@16  # macOS
# OR
sudo systemctl start postgresql    # Linux

# Create database and user
./scripts/setup_postgres.sh
```

### Step 2: Run Migration

```bash
# Activate virtual environment
source venv/bin/activate

# Test migration (dry run)
python scripts/migrate_sqlite_to_postgres.py --dry-run

# Run actual migration with backup
python scripts/migrate_sqlite_to_postgres.py --backup
```

### Step 3: Verify Migration

```bash
# Automated verification
python scripts/verify_migration.py

# Manual verification (optional)
psql -h localhost -U bizy -d bizy_dev -c "SELECT COUNT(*) FROM tasks;"
psql -h localhost -U bizy -d bizy_dev -c "SELECT COUNT(*) FROM goals;"
psql -h localhost -U bizy -d bizy_dev -c "SELECT * FROM users;"
```

### Step 4: Update Configuration

```bash
# Edit .env to use PostgreSQL
nano .env

# Change DATABASE_URL
DATABASE_URL=postgresql://bizy:bizy_dev_password@localhost:5432/bizy_dev

# Test backend
./run.sh
curl http://localhost:8000/health
```

### Step 5: Change Default Password

```sql
-- Via psql
psql -h localhost -U bizy -d bizy_dev

UPDATE users
SET hashed_password = crypt('your_new_password', gen_salt('bf', 12))
WHERE email = 'admin@bizy.local';
```

---

## Rollback Procedure

### If Migration Fails

**Option 1: Use Backup**
```bash
# Your backup is at:
ls ~/.business-agent/tasks_backup_*.db

# CLI still works with original database
bizy task list  # Uses ~/.business-agent/tasks.db

# Drop PostgreSQL and retry:
psql -U postgres -c "DROP DATABASE bizy_dev;"
./scripts/setup_postgres.sh
python scripts/migrate_sqlite_to_postgres.py --backup
```

**Option 2: Keep Using SQLite**
```bash
# Just don't update .env to use PostgreSQL
# Backend can still use SQLite:
DATABASE_URL=sqlite:///~/.business-agent/tasks.db
```

---

## Troubleshooting

### PostgreSQL Connection Errors

**Error:** `psql: could not connect to server`
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start if not running
brew services start postgresql@16  # macOS
sudo systemctl start postgresql    # Linux
```

**Error:** `FATAL: password authentication failed`
```bash
# Reset password
psql -U postgres -c "ALTER USER bizy WITH PASSWORD 'new_password';"

# Update .env
echo "POSTGRES_PASSWORD=new_password" >> .env
```

### Migration Script Errors

**Error:** `No module named 'models'`
```bash
# Make sure you're in backend directory
cd /Users/reidchatham/Developer/business-agent/backend

# Make sure venv is activated
source venv/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"
```

**Error:** `Task count mismatch`
```bash
# Check migration logs for errors
python scripts/migrate_sqlite_to_postgres.py --dry-run 2>&1 | grep ERROR

# If specific tasks failed, check database constraints
psql -h localhost -U bizy -d bizy_dev
SELECT * FROM tasks WHERE id = <failed_id>;
```

### Verification Errors

**Warning:** `X tasks reference non-existent goals`
```sql
-- This is usually OK (orphaned tasks)
-- To fix, unlink tasks from goals:
UPDATE tasks SET parent_goal_id = NULL
WHERE parent_goal_id NOT IN (SELECT id FROM goals);
```

---

## Development Tips

### Test Migration Locally

```bash
# Create test SQLite database
cp ~/.business-agent/tasks.db /tmp/test_tasks.db

# Run migration on test database
python scripts/migrate_sqlite_to_postgres.py \
  --sqlite-path /tmp/test_tasks.db \
  --dry-run

# Check results without affecting production
```

### Multiple Migrations

```bash
# Create different PostgreSQL databases for testing
createdb -U postgres bizy_test_1
createdb -U postgres bizy_test_2

# Migrate to each
DATABASE_URL=postgresql://bizy:pass@localhost/bizy_test_1 \
  python scripts/migrate_sqlite_to_postgres.py

DATABASE_URL=postgresql://bizy:pass@localhost/bizy_test_2 \
  python scripts/migrate_sqlite_to_postgres.py
```

### Debugging

```python
# Add to migration script for debugging
import pdb; pdb.set_trace()

# Or add print statements
print(f"DEBUG: Migrating task {task.id}: {task.title}")
```

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Core](https://docs.sqlalchemy.org/en/20/core/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Migration Guide](../docs/MIGRATION_GUIDE.md)

---

**Last Updated:** November 18, 2025
**Status:** Complete ✅
