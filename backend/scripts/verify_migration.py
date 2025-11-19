#!/usr/bin/env python3
"""
Verify SQLite to PostgreSQL migration integrity

Usage:
    python scripts/verify_migration.py
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))

# Import models
from agent.models import get_engine as get_sqlite_engine, Task as SQLiteTask, Goal as SQLiteGoal
from models import User, Task as PGTask, Goal as PGGoal

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'


def print_pass(message):
    print(f"{GREEN}✓{NC} {message}")


def print_fail(message):
    print(f"{RED}✗{NC} {message}")


def print_warn(message):
    print(f"{YELLOW}⚠{NC}  {message}")


def verify_migration():
    """Verify migration integrity"""
    print("="*60)
    print("Migration Verification")
    print("="*60)
    print()

    # Get database paths
    sqlite_path = Path.home() / ".business-agent" / "tasks.db"
    postgres_url = os.getenv("DATABASE_URL")

    if not postgres_url:
        print_fail("DATABASE_URL not set in environment")
        return False

    if not sqlite_path.exists():
        print_fail(f"SQLite database not found: {sqlite_path}")
        return False

    print(f"📂 SQLite: {sqlite_path}")
    print(f"🐘 PostgreSQL: {postgres_url.split('@')[1] if '@' in postgres_url else postgres_url}")
    print()

    # Connect to databases
    try:
        sqlite_engine = get_sqlite_engine(str(sqlite_path))
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        sqlite_session = SQLiteSession()
        print_pass("Connected to SQLite")

        pg_engine = create_engine(postgres_url)
        PGSession = sessionmaker(bind=pg_engine)
        pg_session = PGSession()
        print_pass("Connected to PostgreSQL")
        print()

    except Exception as e:
        print_fail(f"Database connection failed: {e}")
        return False

    # Run verification checks
    all_passed = True

    # Check 1: Record counts
    print("📊 Checking record counts...")
    sqlite_task_count = sqlite_session.query(SQLiteTask).count()
    sqlite_goal_count = sqlite_session.query(SQLiteGoal).count()
    pg_task_count = pg_session.query(PGTask).count()
    pg_goal_count = pg_session.query(PGGoal).count()
    pg_user_count = pg_session.query(User).count()

    print(f"   SQLite: {sqlite_task_count} tasks, {sqlite_goal_count} goals")
    print(f"   PostgreSQL: {pg_task_count} tasks, {pg_goal_count} goals, {pg_user_count} users")

    if sqlite_task_count == pg_task_count:
        print_pass(f"Task count matches ({pg_task_count})")
    else:
        print_fail(f"Task count mismatch: SQLite={sqlite_task_count}, PostgreSQL={pg_task_count}")
        all_passed = False

    if sqlite_goal_count == pg_goal_count:
        print_pass(f"Goal count matches ({pg_goal_count})")
    else:
        print_fail(f"Goal count mismatch: SQLite={sqlite_goal_count}, PostgreSQL={pg_goal_count}")
        all_passed = False

    if pg_user_count >= 1:
        print_pass(f"Users exist ({pg_user_count})")
    else:
        print_fail("No users found in PostgreSQL")
        all_passed = False

    print()

    # Check 2: All records have user_id
    print("👤 Checking user relationships...")
    null_user_tasks = pg_session.query(PGTask).filter(PGTask.user_id.is_(None)).count()
    null_user_goals = pg_session.query(PGGoal).filter(PGGoal.user_id.is_(None)).count()

    if null_user_tasks == 0:
        print_pass("All tasks have user_id")
    else:
        print_fail(f"{null_user_tasks} tasks missing user_id")
        all_passed = False

    if null_user_goals == 0:
        print_pass("All goals have user_id")
    else:
        print_fail(f"{null_user_goals} goals missing user_id")
        all_passed = False

    print()

    # Check 3: Foreign key integrity
    print("🔗 Checking foreign key relationships...")

    # Check task-goal relationships
    orphaned_tasks = pg_session.execute(text("""
        SELECT COUNT(*)
        FROM tasks t
        LEFT JOIN goals g ON t.parent_goal_id = g.id
        WHERE t.parent_goal_id IS NOT NULL AND g.id IS NULL
    """)).scalar()

    if orphaned_tasks == 0:
        print_pass("All task-goal relationships valid")
    else:
        print_warn(f"{orphaned_tasks} tasks reference non-existent goals")
        # This is a warning, not a failure (tasks can be orphaned)

    # Check user-task relationships
    invalid_user_tasks = pg_session.execute(text("""
        SELECT COUNT(*)
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE u.id IS NULL
    """)).scalar()

    if invalid_user_tasks == 0:
        print_pass("All task-user relationships valid")
    else:
        print_fail(f"{invalid_user_tasks} tasks reference non-existent users")
        all_passed = False

    # Check user-goal relationships
    invalid_user_goals = pg_session.execute(text("""
        SELECT COUNT(*)
        FROM goals g
        LEFT JOIN users u ON g.user_id = u.id
        WHERE u.id IS NULL
    """)).scalar()

    if invalid_user_goals == 0:
        print_pass("All goal-user relationships valid")
    else:
        print_fail(f"{invalid_user_goals} goals reference non-existent users")
        all_passed = False

    print()

    # Check 4: Timestamps
    print("⏰ Checking timestamps...")

    # Check for NULL timestamps (should not exist)
    null_created_tasks = pg_session.query(PGTask).filter(PGTask.created_at.is_(None)).count()
    null_created_goals = pg_session.query(PGGoal).filter(PGGoal.created_at.is_(None)).count()

    if null_created_tasks == 0:
        print_pass("All tasks have created_at")
    else:
        print_fail(f"{null_created_tasks} tasks missing created_at")
        all_passed = False

    if null_created_goals == 0:
        print_pass("All goals have created_at")
    else:
        print_fail(f"{null_created_goals} goals missing created_at")
        all_passed = False

    print()

    # Check 5: Sample data comparison
    print("🔍 Comparing sample data...")

    # Get first task from each database
    sqlite_first_task = sqlite_session.query(SQLiteTask).order_by(SQLiteTask.id).first()
    pg_first_task = pg_session.query(PGTask).order_by(PGTask.id).first()

    if sqlite_first_task and pg_first_task:
        if (sqlite_first_task.id == pg_first_task.id and
            sqlite_first_task.title == pg_first_task.title and
            sqlite_first_task.status == pg_first_task.status):
            print_pass("Sample task data matches")
        else:
            print_fail("Sample task data mismatch")
            print(f"   SQLite: ID={sqlite_first_task.id}, title='{sqlite_first_task.title}'")
            print(f"   PostgreSQL: ID={pg_first_task.id}, title='{pg_first_task.title}'")
            all_passed = False
    else:
        print_warn("No tasks to compare")

    print()

    # Summary
    print("="*60)
    if all_passed:
        print(f"{GREEN}✅ All verification checks passed!{NC}")
        print("="*60)
        return True
    else:
        print(f"{RED}❌ Some verification checks failed{NC}")
        print("="*60)
        print("\nRecommendations:")
        print("  1. Review migration logs for errors")
        print("  2. Re-run migration: python scripts/migrate_sqlite_to_postgres.py")
        print("  3. Check database constraints")
        return False


if __name__ == "__main__":
    success = verify_migration()
    sys.exit(0 if success else 1)
