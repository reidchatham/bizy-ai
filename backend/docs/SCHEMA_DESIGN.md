# PostgreSQL Schema Design with User Support

**Task:** Phase 3, Task 38 - Design and implement PostgreSQL schema with user support
**Date:** November 18, 2025
**Status:** Complete

---

## Overview

This document describes the PostgreSQL database schema for Bizy AI's Phase 3 web interface, which adds multi-user support and migrates from SQLite to PostgreSQL.

## Design Goals

1. **Multi-User Support**: Enable multiple users to use the platform simultaneously
2. **Data Isolation**: Users can only access their own tasks/goals
3. **Scalability**: Prepare for production-scale traffic
4. **Performance**: Add indexes for common query patterns
5. **Consistency**: Use UTC timestamps throughout

---

## Core Models

### 1. User Model (`users` table)

**Purpose:** Authentication and user management

**Fields:**
- `id` (Integer, PK) - Auto-incrementing user ID
- `email` (String 255, Unique, Indexed) - User's email address
- `username` (String 100, Unique, Indexed) - Username for display
- `hashed_password` (String 255) - bcrypt hashed password
- `full_name` (String 200) - User's full name
- `is_active` (Boolean) - Account status (default: True)
- `is_verified` (Boolean) - Email verification status (default: False)
- `is_superuser` (Boolean) - Admin flag (default: False)
- `created_at` (DateTime, UTC) - Account creation time
- `updated_at` (DateTime, UTC) - Last profile update
- `last_login_at` (DateTime, UTC) - Last login timestamp
- `email_verified_at` (DateTime, UTC) - Email verification time

**Indexes:**
- Primary key on `id`
- Unique index on `email`
- Unique index on `username`

**Relationships:**
- One-to-Many with `tasks` (cascade delete)
- One-to-Many with `goals` (cascade delete)

**Security:**
- Passwords stored as bcrypt hashes (never plaintext)
- Email verification required for certain features
- Soft delete via `is_active` flag

---

### 2. Task Model (`tasks` table)

**Purpose:** Task management with user ownership

**Changes from SQLite:**
- ✅ Added `user_id` foreign key
- ✅ Changed `created_at` from local time to UTC
- ✅ Added `updated_at` timestamp
- ✅ Added composite indexes for common queries

**Fields:**
- `id` (Integer, PK, Indexed) - Task ID
- `user_id` (Integer, FK → users.id, Indexed, **NOT NULL**)
  - `ON DELETE CASCADE` - Delete tasks when user is deleted
- `parent_goal_id` (Integer, FK → goals.id, Indexed)
  - `ON DELETE SET NULL` - Unlink from goal if goal deleted
- `title` (String 500, NOT NULL) - Task title
- `description` (Text) - Detailed description
- `priority` (Integer) - 1=highest, 5=lowest (default: 3)
- `status` (String 50) - pending, in_progress, completed, blocked (default: pending)
- `category` (String 100, Indexed) - Task category (development, marketing, etc.)
- `estimated_hours` (Float) - Estimated time
- `actual_hours` (Float) - Actual time spent
- `due_date` (DateTime, Indexed) - When task is due
- `created_at` (DateTime, UTC, NOT NULL, Indexed) - Task creation time
- `updated_at` (DateTime, UTC, NOT NULL) - Last modification time
- `completed_at` (DateTime, UTC) - Completion timestamp
- `dependencies` (JSON) - Array of task IDs this depends on
- `notes` (Text) - Additional notes
- `tags` (JSON) - Array of tags for filtering

**Indexes:**
- Primary key on `id`
- Single column indexes: `user_id`, `parent_goal_id`, `category`, `due_date`, `created_at`
- Composite indexes for performance:
  - `(user_id, status)` - "Show me my active tasks"
  - `(user_id, due_date)` - "Show me my upcoming tasks"
  - `(user_id, category)` - "Show me my development tasks"
  - `(parent_goal_id, status)` - "Show me tasks for this goal"

**Relationships:**
- Many-to-One with `users` (required)
- Many-to-One with `goals` (optional)

---

### 3. Goal Model (`goals` table)

**Purpose:** Goal management with user ownership and hierarchy

**Changes from SQLite:**
- ✅ Added `user_id` foreign key
- ✅ Already had `created_at`/`updated_at` (UTC)
- ✅ Added `completed_at` timestamp
- ✅ Added composite indexes for common queries

**Fields:**
- `id` (Integer, PK, Indexed) - Goal ID
- `user_id` (Integer, FK → users.id, Indexed, **NOT NULL**)
  - `ON DELETE CASCADE` - Delete goals when user is deleted
- `parent_goal_id` (Integer, FK → goals.id, Indexed)
  - `ON DELETE SET NULL` - Self-referencing for goal hierarchy
- `title` (String 500, NOT NULL) - Goal title
- `description` (Text) - Detailed description
- `horizon` (String 50, Indexed) - yearly, quarterly, monthly, weekly
- `target_date` (DateTime, Indexed) - Target completion date
- `status` (String 50) - active, completed, on_hold, cancelled (default: active)
- `progress_percentage` (Float) - Auto-calculated from child tasks (0.0-100.0)
- `success_criteria` (Text) - How to measure success
- `created_at` (DateTime, UTC, NOT NULL, Indexed) - Goal creation time
- `updated_at` (DateTime, UTC, NOT NULL) - Last modification time
- `completed_at` (DateTime, UTC) - Completion timestamp
- `metrics` (JSON) - Custom metrics to track

**Indexes:**
- Primary key on `id`
- Single column indexes: `user_id`, `parent_goal_id`, `horizon`, `target_date`, `created_at`
- Composite indexes for performance:
  - `(user_id, status)` - "Show me my active goals"
  - `(user_id, horizon)` - "Show me my quarterly goals"
  - `(user_id, target_date)` - "Show me my upcoming goals"

**Relationships:**
- Many-to-One with `users` (required)
- One-to-Many with `tasks` (cascade delete to orphan)
- Self-referential One-to-Many for goal hierarchy

---

## Migration from SQLite

### Key Differences

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| User Support | ❌ No | ✅ Yes |
| Timestamps | Local time (mixed) | UTC (consistent) |
| Indexes | Basic | Composite indexes |
| JSON Support | Limited | Full JSON operators |
| Concurrent Writes | Limited | Excellent |
| Max DB Size | ~140 TB | Unlimited |

### Breaking Changes

1. **User ID Required**: All existing tasks/goals need to be assigned to a user
2. **Timestamp Format**: Existing local timestamps need conversion to UTC
3. **Foreign Key Constraints**: Stricter referential integrity

### Migration Strategy (Task 39)

See `backend/docs/MIGRATION_GUIDE.md` for detailed migration steps.

---

## Performance Considerations

### Composite Indexes

We've added composite indexes for the most common query patterns:

**Tasks:**
```sql
-- Fast: "Show my incomplete tasks"
SELECT * FROM tasks WHERE user_id = 1 AND status != 'completed';
-- Uses index: ix_tasks_user_status

-- Fast: "Show my overdue tasks"
SELECT * FROM tasks WHERE user_id = 1 AND due_date < NOW();
-- Uses index: ix_tasks_user_due_date

-- Fast: "Show development tasks"
SELECT * FROM tasks WHERE user_id = 1 AND category = 'phase-3-backend';
-- Uses index: ix_tasks_user_category
```

**Goals:**
```sql
-- Fast: "Show my active goals"
SELECT * FROM goals WHERE user_id = 1 AND status = 'active';
-- Uses index: ix_goals_user_status

-- Fast: "Show quarterly goals"
SELECT * FROM goals WHERE user_id = 1 AND horizon = 'quarterly';
-- Uses index: ix_goals_user_horizon
```

### JSON Columns

PostgreSQL provides excellent JSON support:

```sql
-- Query tasks with specific tag
SELECT * FROM tasks WHERE tags @> '["urgent"]';

-- Query dependencies
SELECT * FROM tasks WHERE dependencies @> '[42]';

-- Update metrics
UPDATE goals SET metrics = metrics || '{"velocity": 2.5}' WHERE id = 1;
```

---

## Security Considerations

### Row-Level Security (Future)

PostgreSQL supports row-level security policies:

```sql
-- Example policy (not implemented yet)
CREATE POLICY user_isolation ON tasks
  FOR ALL
  TO authenticated_user
  USING (user_id = current_user_id());
```

For now, we enforce user isolation in the application layer (FastAPI dependencies).

### Password Storage

- Passwords hashed with bcrypt (cost factor 12)
- Never stored in plaintext
- Never logged or exposed in API responses
- Hashed password only in User.hashed_password column

---

## Data Types

### DateTime Handling

**All timestamps use UTC:**
- Consistent across timezones
- Client converts to local time for display
- Server always works in UTC

**SQLAlchemy:**
```python
from datetime import datetime

# CORRECT: Use UTC
created_at = Column(DateTime, default=datetime.utcnow)

# WRONG: Don't use local time
created_at = Column(DateTime, default=datetime.now)  # ❌
```

### JSON Storage

**PostgreSQL JSONB advantages:**
- Indexable (GIN indexes)
- Query operators (`@>`, `?`, `?&`, `||`)
- Faster than TEXT with JSON parsing

**Example:**
```python
tags = Column(JSON)  # SQLAlchemy uses JSONB on PostgreSQL

# Python
task.tags = ["urgent", "backend", "phase-3"]

# SQL Query
SELECT * FROM tasks WHERE tags @> '["urgent"]';
```

---

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │
│─────────────│
│ id (PK)     │◄─────┐
│ email       │      │
│ username    │      │
│ ...         │      │
└─────────────┘      │
                     │
                     │ user_id (FK)
                     │
       ┌─────────────┴──────────┬───────────────┐
       │                        │               │
       │                        │               │
┌──────▼──────┐         ┌───────▼──────┐       │
│    tasks    │         │    goals     │       │
│─────────────│         │──────────────│       │
│ id (PK)     │         │ id (PK)      │◄──────┘
│ user_id (FK)│         │ user_id (FK) │  parent_goal_id (FK)
│ parent_goal │────────►│ parent_goal  │──┐
│   _id (FK)  │         │   _id (FK)   │  │ (self-reference)
│ title       │         │ title        │◄─┘
│ status      │         │ status       │
│ created_at  │         │ created_at   │
│ updated_at  │         │ updated_at   │
│ ...         │         │ ...          │
└─────────────┘         └──────────────┘
```

---

## Implementation Files

| File | Purpose |
|------|---------|
| `backend/models/base.py` | SQLAlchemy declarative base |
| `backend/models/user.py` | User model with auth fields |
| `backend/models/task.py` | Task model with user FK |
| `backend/models/goal.py` | Goal model with user FK |
| `backend/models/__init__.py` | Model exports |
| `backend/alembic/env.py` | Alembic migration config |
| `backend/alembic/versions/...` | Migration files |

---

## Next Steps

1. **Task 39**: Create database migration script (SQLite → PostgreSQL)
2. **Task 40**: Implement user authentication endpoints
3. **Task 41**: Implement task CRUD API with user filtering
4. **Task 42**: Implement goal CRUD API with user filtering

---

## Testing

### Unit Tests

```python
def test_user_task_relationship():
    """Test user can access their own tasks"""
    user = User(email="test@example.com", username="testuser")
    task = Task(title="Test Task", user=user)
    assert task.user_id == user.id
    assert task in user.tasks

def test_cascade_delete():
    """Test deleting user deletes their tasks"""
    user = User(email="test@example.com", username="testuser")
    task = Task(title="Test Task", user=user)
    session.add(user)
    session.commit()

    session.delete(user)
    session.commit()

    # Task should be deleted due to CASCADE
    assert session.query(Task).filter_by(id=task.id).first() is None
```

### Integration Tests

```python
def test_user_isolation():
    """Test users cannot see each other's data"""
    user1 = User(email="user1@example.com", username="user1")
    user2 = User(email="user2@example.com", username="user2")
    task1 = Task(title="User 1 Task", user=user1)
    task2 = Task(title="User 2 Task", user=user2)

    # User 1 should only see their task
    user1_tasks = session.query(Task).filter_by(user_id=user1.id).all()
    assert len(user1_tasks) == 1
    assert user1_tasks[0].title == "User 1 Task"
```

---

**Document Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Status:** Implementation Complete ✅
