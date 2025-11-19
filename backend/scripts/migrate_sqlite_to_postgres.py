#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script
Task 39: Migrate existing SQLite data to PostgreSQL with user support

Usage:
    python scripts/migrate_sqlite_to_postgres.py [--dry-run] [--backup]

Environment Variables:
    SQLITE_DB_PATH: Path to SQLite database (default: ~/.business-agent/tasks.db)
    DATABASE_URL: PostgreSQL connection string
    DEFAULT_USER_EMAIL: Email for default user (default: admin@bizy.local)
    DEFAULT_USER_USERNAME: Username for default user (default: admin)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Import old SQLite models
sys.path.insert(0, str(backend_dir.parent))
from agent.models import (
    Task as SQLiteTask,
    Goal as SQLiteGoal,
    DailyLog as SQLiteDailyLog,
    ResearchItem as SQLiteResearchItem,
    BusinessMetric as SQLiteBusinessMetric,
    BusinessPlan as SQLiteBusinessPlan,
    get_engine as get_sqlite_engine
)

# Import new PostgreSQL models
from models import Base, User, Task as PGTask, Goal as PGGoal


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MigrationStats:
    """Track migration statistics"""
    def __init__(self):
        self.users_created = 0
        self.tasks_migrated = 0
        self.goals_migrated = 0
        self.errors = []
        self.warnings = []

    def add_error(self, message: str):
        self.errors.append(message)
        print(f"❌ ERROR: {message}")

    def add_warning(self, message: str):
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")

    def print_summary(self):
        print("\n" + "="*60)
        print("Migration Summary")
        print("="*60)
        print(f"✓ Users created: {self.users_created}")
        print(f"✓ Tasks migrated: {self.tasks_migrated}")
        print(f"✓ Goals migrated: {self.goals_migrated}")
        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"   - {warning}")
        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for error in self.errors[:5]:  # Show first 5
                print(f"   - {error}")
        print("="*60)


def backup_sqlite_database(sqlite_path: Path) -> Path:
    """Create a backup of the SQLite database"""
    import shutil
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = sqlite_path.parent / f"{sqlite_path.stem}_backup_{timestamp}.db"

    print(f"📦 Creating backup: {backup_path}")
    shutil.copy2(sqlite_path, backup_path)
    print(f"✓ Backup created successfully")

    return backup_path


def convert_local_to_utc(dt: datetime) -> datetime:
    """Convert local datetime to UTC (best effort)"""
    if dt is None:
        return None

    # If datetime is naive (no timezone), assume it's local time
    if dt.tzinfo is None:
        # Assume it's already roughly UTC or local time
        # For safety, just use it as-is and mark as UTC
        return dt.replace(tzinfo=timezone.utc)

    # If it has timezone info, convert to UTC
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def create_default_user(pg_session, email: str, username: str, stats: MigrationStats) -> User:
    """Create the default user for migration"""
    print(f"\n👤 Creating default user: {username} ({email})")

    # Check if user already exists
    existing = pg_session.query(User).filter(User.email == email).first()
    if existing:
        print(f"✓ User already exists (ID: {existing.id})")
        return existing

    # Generate a random password (user should change it)
    import secrets
    temp_password = secrets.token_urlsafe(16)
    hashed_password = pwd_context.hash(temp_password)

    user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name="Default User (Migration)",
        is_active=True,
        is_verified=True,  # Auto-verify migration user
        is_superuser=True,  # Make them admin
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    pg_session.add(user)
    pg_session.commit()
    pg_session.refresh(user)

    stats.users_created += 1
    print(f"✓ Created user (ID: {user.id})")
    print(f"📝 IMPORTANT: Temporary password: {temp_password}")
    print(f"   Please change this password after migration!")

    return user


def migrate_tasks(sqlite_session, pg_session, user_id: int, stats: MigrationStats):
    """Migrate tasks from SQLite to PostgreSQL"""
    print(f"\n📋 Migrating tasks...")

    # Fetch all tasks from SQLite
    sqlite_tasks = sqlite_session.query(SQLiteTask).all()
    print(f"   Found {len(sqlite_tasks)} tasks in SQLite")

    for sqlite_task in sqlite_tasks:
        try:
            # Create PostgreSQL task
            pg_task = PGTask(
                id=sqlite_task.id,  # Preserve ID
                user_id=user_id,    # Assign to default user
                parent_goal_id=sqlite_task.parent_goal_id,
                title=sqlite_task.title,
                description=sqlite_task.description,
                priority=sqlite_task.priority,
                status=sqlite_task.status,
                category=sqlite_task.category,
                estimated_hours=sqlite_task.estimated_hours,
                actual_hours=sqlite_task.actual_hours,
                due_date=convert_local_to_utc(sqlite_task.due_date),
                created_at=convert_local_to_utc(sqlite_task.created_at) or datetime.utcnow(),
                updated_at=datetime.utcnow(),
                completed_at=convert_local_to_utc(sqlite_task.completed_at),
                dependencies=sqlite_task.dependencies,
                notes=sqlite_task.notes,
                tags=sqlite_task.tags
            )

            pg_session.add(pg_task)
            stats.tasks_migrated += 1

        except Exception as e:
            stats.add_error(f"Failed to migrate task {sqlite_task.id}: {e}")

    pg_session.commit()
    print(f"✓ Migrated {stats.tasks_migrated} tasks")


def migrate_goals(sqlite_session, pg_session, user_id: int, stats: MigrationStats):
    """Migrate goals from SQLite to PostgreSQL"""
    print(f"\n🎯 Migrating goals...")

    # Fetch all goals from SQLite
    sqlite_goals = sqlite_session.query(SQLiteGoal).all()
    print(f"   Found {len(sqlite_goals)} goals in SQLite")

    for sqlite_goal in sqlite_goals:
        try:
            # Create PostgreSQL goal
            pg_goal = PGGoal(
                id=sqlite_goal.id,  # Preserve ID
                user_id=user_id,    # Assign to default user
                parent_goal_id=sqlite_goal.parent_goal_id,
                title=sqlite_goal.title,
                description=sqlite_goal.description,
                horizon=sqlite_goal.horizon,
                target_date=convert_local_to_utc(sqlite_goal.target_date),
                status=sqlite_goal.status,
                progress_percentage=sqlite_goal.progress_percentage,
                success_criteria=sqlite_goal.success_criteria,
                created_at=convert_local_to_utc(sqlite_goal.created_at) or datetime.utcnow(),
                updated_at=convert_local_to_utc(sqlite_goal.updated_at) or datetime.utcnow(),
                completed_at=None,  # Not in old schema
                metrics=sqlite_goal.metrics
            )

            pg_session.add(pg_goal)
            stats.goals_migrated += 1

        except Exception as e:
            stats.add_error(f"Failed to migrate goal {sqlite_goal.id}: {e}")

    pg_session.commit()
    print(f"✓ Migrated {stats.goals_migrated} goals")


def verify_migration(sqlite_session, pg_session, user_id: int, stats: MigrationStats):
    """Verify that migration was successful"""
    print(f"\n🔍 Verifying migration...")

    # Count records
    sqlite_task_count = sqlite_session.query(SQLiteTask).count()
    sqlite_goal_count = sqlite_session.query(SQLiteGoal).count()

    pg_task_count = pg_session.query(PGTask).filter(PGTask.user_id == user_id).count()
    pg_goal_count = pg_session.query(PGGoal).filter(PGGoal.user_id == user_id).count()

    # Check counts match
    if sqlite_task_count != pg_task_count:
        stats.add_error(f"Task count mismatch: SQLite={sqlite_task_count}, PostgreSQL={pg_task_count}")
    else:
        print(f"✓ Task count matches: {pg_task_count}")

    if sqlite_goal_count != pg_goal_count:
        stats.add_error(f"Goal count mismatch: SQLite={sqlite_goal_count}, PostgreSQL={pg_goal_count}")
    else:
        print(f"✓ Goal count matches: {pg_goal_count}")

    # Verify foreign key relationships
    orphaned_tasks = pg_session.query(PGTask).filter(
        PGTask.parent_goal_id.isnot(None),
        ~PGTask.parent_goal_id.in_(pg_session.query(PGGoal.id))
    ).count()

    if orphaned_tasks > 0:
        stats.add_warning(f"{orphaned_tasks} tasks reference non-existent goals")
    else:
        print(f"✓ All task-goal relationships valid")

    # Check for null user_ids (should be impossible)
    null_user_tasks = pg_session.query(PGTask).filter(PGTask.user_id.is_(None)).count()
    null_user_goals = pg_session.query(PGGoal).filter(PGGoal.user_id.is_(None)).count()

    if null_user_tasks > 0 or null_user_goals > 0:
        stats.add_error(f"Found records with null user_id: tasks={null_user_tasks}, goals={null_user_goals}")
    else:
        print(f"✓ All records have user_id")


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite database to PostgreSQL")
    parser.add_argument("--dry-run", action="store_true", help="Run migration without committing changes")
    parser.add_argument("--backup", action="store_true", help="Create backup of SQLite database before migration")
    parser.add_argument("--sqlite-path", help="Path to SQLite database (default: ~/.business-agent/tasks.db)")
    parser.add_argument("--postgres-url", help="PostgreSQL connection URL (default: from env)")
    args = parser.parse_args()

    stats = MigrationStats()

    print("="*60)
    print("SQLite to PostgreSQL Migration")
    print("="*60)

    # Get database paths
    sqlite_path = Path(args.sqlite_path) if args.sqlite_path else Path.home() / ".business-agent" / "tasks.db"
    postgres_url = args.postgres_url or os.getenv("DATABASE_URL")

    if not postgres_url:
        print("❌ ERROR: DATABASE_URL not set")
        print("   Set DATABASE_URL environment variable or use --postgres-url")
        sys.exit(1)

    if not sqlite_path.exists():
        print(f"❌ ERROR: SQLite database not found: {sqlite_path}")
        sys.exit(1)

    print(f"📂 SQLite database: {sqlite_path}")
    print(f"🐘 PostgreSQL URL: {postgres_url.split('@')[1] if '@' in postgres_url else postgres_url}")

    if args.dry_run:
        print("🏃 DRY RUN MODE: No changes will be committed")

    # Create backup if requested
    if args.backup and not args.dry_run:
        backup_path = backup_sqlite_database(sqlite_path)

    try:
        # Connect to SQLite
        print(f"\n📂 Connecting to SQLite...")
        sqlite_engine = get_sqlite_engine(str(sqlite_path))
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        sqlite_session = SQLiteSession()
        print(f"✓ Connected to SQLite")

        # Connect to PostgreSQL
        print(f"\n🐘 Connecting to PostgreSQL...")
        pg_engine = create_engine(postgres_url)

        # Create tables
        print(f"📋 Creating PostgreSQL tables...")
        Base.metadata.create_all(pg_engine)
        print(f"✓ Tables created")

        PGSession = sessionmaker(bind=pg_engine)
        pg_session = PGSession()
        print(f"✓ Connected to PostgreSQL")

        # Create default user
        default_email = os.getenv("DEFAULT_USER_EMAIL", "admin@bizy.local")
        default_username = os.getenv("DEFAULT_USER_USERNAME", "admin")
        default_user = create_default_user(pg_session, default_email, default_username, stats)

        # Migrate data
        migrate_goals(sqlite_session, pg_session, default_user.id, stats)  # Goals first (tasks reference them)
        migrate_tasks(sqlite_session, pg_session, default_user.id, stats)

        # Verify migration
        verify_migration(sqlite_session, pg_session, default_user.id, stats)

        if args.dry_run:
            print("\n🏃 DRY RUN: Rolling back all changes")
            pg_session.rollback()
        else:
            print("\n💾 Committing changes...")
            pg_session.commit()
            print("✓ Migration committed successfully")

        # Print summary
        stats.print_summary()

        # Close connections
        sqlite_session.close()
        pg_session.close()

        if stats.errors:
            print("\n❌ Migration completed with errors")
            sys.exit(1)
        else:
            print("\n✅ Migration completed successfully!")
            if not args.dry_run:
                print(f"\n📝 Next steps:")
                print(f"   1. Test the PostgreSQL database")
                print(f"   2. Update backend/.env to use PostgreSQL:")
                print(f"      DATABASE_URL={postgres_url}")
                print(f"   3. Login with: {default_email}")
                print(f"   4. Change your password immediately!")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
