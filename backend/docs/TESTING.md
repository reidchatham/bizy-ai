# Local Testing Guide - Bizy AI Backend

**Complete guide for testing the Bizy AI backend API locally**

---

## Quick Start

```bash
# From project root (/Users/reidchatham/Developer/business-agent)
./backend/scripts/start-dev.sh

# In another terminal, run tests
./backend/scripts/test-api.sh

# Stop servers when done
./backend/scripts/stop-dev.sh
```

---

## Prerequisites

### Required Software

1. **Ruby 3.0+** (for auth-server-ruby)
   ```bash
   ruby --version  # Should be 3.0+
   ```

2. **Bundler** (Ruby package manager)
   ```bash
   gem install bundler
   ```

3. **Python 3.11+** (for Bizy backend)
   ```bash
   python3 --version  # Should be 3.11+
   ```

4. **PostgreSQL** (database)
   ```bash
   # macOS
   brew install postgresql@16
   brew services start postgresql@16

   # Ubuntu/Debian
   sudo apt install postgresql-16
   sudo systemctl start postgresql
   ```

5. **jq** (JSON parsing for test scripts)
   ```bash
   # macOS
   brew install jq

   # Ubuntu/Debian
   sudo apt install jq
   ```

### Project Setup

Both `auth-server-ruby` and `business-agent` must be sibling directories:

```
/Users/reidchatham/Developer/
├── auth-server-ruby/
│   ├── app.rb
│   ├── Gemfile
│   └── .env
└── business-agent/
    ├── backend/
    └── bizy.py
```

---

## Development Environment Setup

### 1. Start Development Servers

The startup script handles everything automatically:

```bash
cd /Users/reidchatham/Developer/business-agent
./backend/scripts/start-dev.sh
```

**What it does:**

1. **Validates directory structure** - Ensures auth-server-ruby exists
2. **Checks for port conflicts** - Asks to kill processes on ports 4567 and 8000
3. **Generates JWT_SECRET** - Creates matching secret for both services
4. **Sets up auth-server-ruby:**
   - Creates `.env` with JWT_SECRET
   - Installs dependencies (`bundle install`)
   - Sets up database (`rake db:migrate`)
   - Starts server on port 4567
5. **Sets up Bizy backend:**
   - Creates Python venv if needed
   - Installs dependencies from `requirements-dev.txt`
   - Starts FastAPI server on port 8000
6. **Performs health checks** - Verifies both services are responding
7. **Displays service URLs and log locations**

**Output:**

```
🚀 Starting Bizy AI Development Environment
==========================================

✓ auth-server-ruby started (PID: 12345)
   Logs: tail -f /tmp/auth-server.log

✓ Backend started (PID: 12346)
   Logs: tail -f /tmp/backend.log

==========================================
✅ Development Environment Ready!
==========================================

Services:
  🔐 Auth Server:  http://localhost:4567
  🚀 Backend API:  http://localhost:8000
  📚 API Docs:     http://localhost:8000/api/docs

Logs:
  Auth Server:     tail -f /tmp/auth-server.log
  Backend:         tail -f /tmp/backend.log

Stop servers:
  ./backend/scripts/stop-dev.sh
```

**Troubleshooting:**

If startup fails, check the logs:

```bash
# Auth server logs
tail -f /tmp/auth-server.log

# Backend logs
tail -f /tmp/backend.log
```

Common issues:

- **Port already in use:** Script will prompt to kill the process
- **PostgreSQL not running:** Start it with `brew services start postgresql@16`
- **Missing dependencies:** Script will install them automatically
- **JWT_SECRET mismatch:** Script ensures they match by using same value

### 2. Stop Development Servers

```bash
./backend/scripts/stop-dev.sh
```

**What it does:**

1. Reads PIDs from `/tmp/auth-server.pid` and `/tmp/backend.pid`
2. Kills processes gracefully
3. Falls back to killing processes on ports 4567 and 8000 if PIDs missing
4. Cleans up PID files

**Output:**

```
Stopping Bizy AI development servers...
✓ Stopped auth-server (PID: 12345)
✓ Stopped backend (PID: 12346)
✓ All services stopped
```

---

## Running Tests

### Automated API Testing

The test script performs comprehensive end-to-end testing:

```bash
./backend/scripts/test-api.sh
```

**What it tests (15 test cases):**

1. ✓ User registration
2. ✓ User login (JWT token)
3. ✓ Get user profile
4. ✓ Verify token
5. ✓ Create task
6. ✓ List tasks
7. ✓ Get task by ID
8. ✓ Update task (partial PATCH)
9. ✓ Complete task
10. ✓ Get task statistics
11. ✓ Filter tasks (by status)
12. ✓ Search tasks (by keyword)
13. ✓ Uncomplete task
14. ✓ Delete task
15. ✓ Verify deletion (404)

**Example output:**

```
🧪 Bizy AI API Testing Suite
==========================================

Checking services...
✓ auth-server (port 4567) is running
✓ backend (port 8000) is running

1. Registering test user...
✓ User registered

2. Logging in...
✓ Login successful
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

3. Getting user profile...
{
  "user_id": 1,
  "username": "testuser",
  "email": "test@example.com"
}

...

==========================================
✅ All API Tests Complete!
==========================================

Your token for manual testing:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Try it:
  export TOKEN='...'
  curl http://localhost:8000/api/tasks -H "Authorization: Bearer $TOKEN" | jq
```

**Test data:**

- **Test user:** `testuser` / `test@example.com` / `Test123!@#`
- Creates a test task, modifies it, and cleans up after

**Troubleshooting:**

If tests fail:

1. **Services not running:** Start them with `./backend/scripts/start-dev.sh`
2. **User already exists:** Test script handles this gracefully
3. **Token expired:** Re-run the test to get a fresh token
4. **Database errors:** Check backend logs at `/tmp/backend.log`

---

## Manual Testing

### Using cURL

The test script outputs a JWT token you can use for manual testing:

```bash
# Run test script to get token
./backend/scripts/test-api.sh

# Copy the token from output, then:
export TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'

# Test endpoints manually
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Example requests:**

```bash
# 1. Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "email": "my@example.com",
    "password": "MyPass123!@#"
  }' | jq

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "MyPass123!@#"
  }' | jq -r '.token')

echo "Token: $TOKEN"

# 3. Get user profile
curl http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build amazing feature",
    "description": "Implement the coolest feature ever",
    "priority": 1,
    "category": "development",
    "estimated_hours": 8.0
  }' | jq

# 5. List all tasks
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" | jq

# 6. List pending high-priority tasks
curl "http://localhost:8000/api/tasks?status=pending&priority=1" \
  -H "Authorization: Bearer $TOKEN" | jq

# 7. Search for tasks
curl "http://localhost:8000/api/tasks?search=feature" \
  -H "Authorization: Bearer $TOKEN" | jq

# 8. Get task by ID
TASK_ID=1
curl http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# 9. Update task
curl -X PATCH http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "actual_hours": 2.5
  }' | jq

# 10. Complete task
curl -X POST http://localhost:8000/api/tasks/$TASK_ID/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actual_hours": 8.0
  }' | jq

# 11. Uncomplete task
curl -X POST http://localhost:8000/api/tasks/$TASK_ID/uncomplete \
  -H "Authorization: Bearer $TOKEN" | jq

# 12. Get task statistics
curl http://localhost:8000/api/tasks/stats/summary \
  -H "Authorization: Bearer $TOKEN" | jq

# 13. Delete task
curl -X DELETE http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Using Swagger UI

The backend provides interactive API documentation:

**URL:** http://localhost:8000/api/docs

**Steps:**

1. **Open Swagger UI:** Navigate to http://localhost:8000/api/docs
2. **Authorize:**
   - Click "Authorize" button (lock icon)
   - Enter: `Bearer YOUR_JWT_TOKEN`
   - Click "Authorize" and "Close"
3. **Try endpoints:**
   - Click any endpoint to expand
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
4. **View response:**
   - Response body (JSON)
   - Response headers
   - Status code

**Benefits:**

- Interactive testing without cURL
- See all available endpoints and parameters
- Automatic request/response validation
- Schema documentation

### Using httpie (alternative to cURL)

If you prefer httpie for cleaner syntax:

```bash
# Install httpie
brew install httpie  # macOS
pip install httpie   # Python

# Login and save token
http POST :8000/api/auth/login username=testuser password=Test123!@#
export TOKEN='...'

# List tasks (cleaner syntax)
http :8000/api/tasks "Authorization: Bearer $TOKEN"

# Create task (JSON inference)
http POST :8000/api/tasks "Authorization: Bearer $TOKEN" \
  title="My task" priority:=1 category="dev"
```

---

## Testing User Isolation

**Critical security feature:** Users can only see their own data.

Test this by creating two users:

```bash
# 1. Create and login as user1
TOKEN1=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "password": "Pass123!@#"
  }' | jq -r '.token')

# Create task as user1
TASK1=$(curl -s -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"title": "User1 task", "priority": 1}' | jq -r '.id')

# 2. Create and login as user2
TOKEN2=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user2",
    "password": "Pass123!@#"
  }' | jq -r '.token')

# 3. Try to access user1's task as user2 (should fail with 404)
curl -s http://localhost:8000/api/tasks/$TASK1 \
  -H "Authorization: Bearer $TOKEN2"

# Expected: {"detail": "Task not found"}

# 4. List tasks as user2 (should be empty or only user2's tasks)
curl -s http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN2" | jq
```

**What this tests:**

- User1 cannot see User2's tasks
- User2 cannot see User1's tasks
- User2 cannot modify User1's tasks (404 not found)
- Database queries automatically filter by user_id

---

## Testing Token Expiration

JWT tokens expire after 24 hours. Test expiration handling:

```bash
# 1. Login and save token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!@#"
  }' | jq -r '.token')

# 2. Use token immediately (should work)
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"

# 3. Wait 24 hours (or modify token manually to test)
# After expiration, should get 401 error:
# {"detail": "Token has expired"}

# 4. Login again to get fresh token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!@#"
  }' | jq -r '.token')
```

---

## Database Inspection

### PostgreSQL CLI

Connect to the database to inspect data:

```bash
# Connect to database
psql -U postgres -d bizy_dev

# List tables
\dt

# View users
SELECT id, username, email, created_at FROM users;

# View tasks for specific user
SELECT id, title, status, priority, user_id
FROM tasks
WHERE user_id = 1;

# View task statistics
SELECT status, COUNT(*)
FROM tasks
GROUP BY status;

# View goals
SELECT id, title, horizon, user_id FROM goals;

# Exit
\q
```

### Database Migrations

View and manage database schema:

```bash
cd backend

# View current migration status
alembic current

# View migration history
alembic history

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## Performance Testing

### Load Testing with Apache Bench

Test API performance under load:

```bash
# Install Apache Bench (ab)
# macOS: comes with Apache
# Ubuntu: sudo apt install apache2-utils

# Get a valid token first
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!@#"
  }' | jq -r '.token')

# Test GET /api/tasks (100 requests, 10 concurrent)
ab -n 100 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks

# Analyze results:
# - Requests per second
# - Time per request
# - Failed requests (should be 0)
```

**Expected performance:**

- GET endpoints: ~100-200 req/sec
- POST endpoints: ~50-100 req/sec
- Database-heavy queries: ~30-50 req/sec

### Database Query Performance

Check slow queries:

```sql
-- Enable query logging (PostgreSQL)
ALTER DATABASE bizy_dev SET log_min_duration_statement = 100;

-- View slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC;
```

---

## Common Issues and Solutions

### Issue 1: Port Already in Use

**Error:**
```
⚠️  Port 4567 (auth-server) already in use
```

**Solution:**
```bash
# Kill process on port 4567
lsof -ti:4567 | xargs kill -9

# Or use the startup script, which will prompt you
./backend/scripts/start-dev.sh
```

### Issue 2: JWT_SECRET Mismatch

**Error:**
```
{"detail": "Could not validate credentials"}
```

**Cause:** Backend and auth-server have different JWT_SECRET values

**Solution:**
```bash
# Stop servers
./backend/scripts/stop-dev.sh

# Remove .env files
rm backend/.env
rm ../auth-server-ruby/.env

# Restart (will regenerate matching secrets)
./backend/scripts/start-dev.sh
```

### Issue 3: PostgreSQL Not Running

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# macOS
brew services start postgresql@16

# Ubuntu
sudo systemctl start postgresql

# Verify it's running
psql -U postgres -c "SELECT version();"
```

### Issue 4: Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Issue 5: Database Migration Issues

**Error:**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**
```bash
cd backend
alembic upgrade head
```

---

## Development Workflow

### Typical Development Session

```bash
# 1. Start servers
./backend/scripts/start-dev.sh

# 2. Open logs in separate terminals
tail -f /tmp/auth-server.log
tail -f /tmp/backend.log

# 3. Make code changes
# backend/api/routes/tasks.py
# ... edit code ...

# 4. Backend auto-reloads (FastAPI --reload)
# Check logs for errors

# 5. Test changes
./backend/scripts/test-api.sh

# Or test manually
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" | jq

# 6. When done
./backend/scripts/stop-dev.sh
```

### Testing Workflow

```bash
# 1. Write tests
# tests/test_tasks_api.py

# 2. Run specific test
pytest tests/test_tasks_api.py::test_create_task -v

# 3. Run all tests
pytest tests/ -v

# 4. Check coverage
pytest tests/ --cov=backend --cov-report=html

# 5. View coverage report
open htmlcov/index.html
```

---

## API Endpoints Reference

### Authentication (auth-server-ruby)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get JWT | No |
| GET | `/api/auth/profile` | Get user profile | Yes |
| POST | `/api/auth/logout` | Logout (invalidate token) | Yes |
| POST | `/api/auth/verify-token` | Verify JWT validity | Yes |
| GET | `/api/auth/auth-server-health` | Auth server health | No |

### Tasks (Bizy backend)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/tasks` | List tasks with filters | Yes |
| POST | `/api/tasks` | Create new task | Yes |
| GET | `/api/tasks/{id}` | Get task details | Yes |
| PATCH | `/api/tasks/{id}` | Update task (partial) | Yes |
| DELETE | `/api/tasks/{id}` | Delete task | Yes |
| POST | `/api/tasks/{id}/complete` | Mark task complete | Yes |
| POST | `/api/tasks/{id}/uncomplete` | Undo completion | Yes |
| GET | `/api/tasks/stats/summary` | Task statistics | Yes |

### System

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Backend health check | No |
| GET | `/` | API information | No |
| GET | `/api/docs` | Swagger UI docs | No |

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres@localhost/bizy_dev

# Authentication
AUTH_SERVER_URL=http://localhost:4567
JWT_SECRET=<generated-by-start-script>
JWT_ALGORITHM=HS256

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
BIZY_ENV=development
```

### Auth Server (../auth-server-ruby/.env)

```bash
# JWT Configuration (must match backend)
JWT_SECRET=<same-as-backend>
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400

# Database
DATABASE_URL=sqlite:db/development.sqlite3

# Server
RACK_ENV=development
PORT=4567
```

---

## Next Steps

### After Basic Testing

1. **Add more test users** - Test multi-user scenarios
2. **Test edge cases** - Invalid data, missing fields, etc.
3. **Load testing** - Use Apache Bench or wrk
4. **Integration tests** - Write automated test suite (Task 43)

### Before Production

1. **Security audit** - Review all authentication flows
2. **Performance optimization** - Identify slow queries
3. **Error handling** - Test failure scenarios
4. **Monitoring** - Set up logging and alerting

---

## Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **JWT.io:** https://jwt.io/ (decode tokens)
- **Postman:** https://www.postman.com/ (GUI alternative to cURL)
- **Insomnia:** https://insomnia.rest/ (another GUI alternative)

---

**Status:** ✅ Complete local testing infrastructure
**Last Updated:** November 18, 2025
**Version:** 1.0

Happy testing! 🧪
