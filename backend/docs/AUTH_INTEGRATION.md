# Authentication Microservice Integration

**Architecture:** Bizy AI Backend + auth-server-ruby microservice
**Date:** November 18, 2025
**Status:** Complete

---

## Architecture Overview

```
┌─────────────┐
│   Frontend  │
│  (React)    │
└──────┬──────┘
       │ HTTP Requests
       │ Authorization: Bearer <token>
       ▼
┌──────────────────────┐
│   Bizy Backend API   │
│   (FastAPI:8000)     │
│                      │
│  ┌────────────────┐  │
│  │ JWT Validation │  │
│  │  Middleware    │  │
│  └────────────────┘  │
│         │            │
│         ▼            │
│  ┌────────────────┐  │
│  │  Protected     │  │
│  │   Routes       │  │
│  └────────────────┘  │
└──────────┬───────────┘
           │
           │ Auth operations
           │ (register, login)
           ▼
    ┌──────────────┐
    │ auth-server  │
    │ (Ruby:4567)  │
    │              │
    │ - Register   │
    │ - Login      │
    │ - Profile    │
    │ - JWT Issue  │
    └──────────────┘
```

---

## How It Works

### 1. User Registration

```
Frontend → Bizy Backend → auth-server-ruby
        POST /api/auth/register
           {username, email, password}
                      ↓
           POST http://localhost:4567/register
                      ↓
                Creates user
                Sends verification email
                      ↓
                Returns user object
```

### 2. User Login

```
Frontend → Bizy Backend → auth-server-ruby
        POST /api/auth/login
           {username, password}
                      ↓
           POST http://localhost:4567/login
                      ↓
                Validates credentials
                Issues JWT token
                      ↓
           Returns {token, user}
                      ↓
        Frontend stores token
```

### 3. Authenticated Requests

```
Frontend → Bizy Backend
        GET /api/tasks
        Authorization: Bearer <JWT>
                ↓
        JWT Validation Middleware
        - Decode token with JWT_SECRET
        - Check expiration
        - Extract user_id
                ↓
        Protected Route Handler
        - user_id available
        - Query user's tasks
                ↓
        Return user's data
```

---

## Services

### 1. auth-server-ruby (Port 4567)

**Responsibilities:**
- User registration
- User login
- Password reset
- Email verification
- JWT token issuance
- User management

**Endpoints:**
- `POST /register` - Create new user
- `POST /login` - Authenticate and get JWT
- `GET /profile` - Get user profile (requires JWT)
- `POST /forgot_password` - Password reset
- `POST /verify_email` - Email verification
- `GET /health` - Health check

**Technology:**
- Ruby 3.2+ with Sinatra
- SQLite (dev) / PostgreSQL (prod)
- bcrypt password hashing
- JWT tokens (HS256, 24-hour expiration)

### 2. Bizy Backend API (Port 8000)

**Responsibilities:**
- Task/Goal CRUD operations
- AI briefing generation
- Analytics and charts
- PDF export
- Calendar views
- JWT token validation
- User data filtering

**Authentication Endpoints:**
- `POST /api/auth/register` - Proxy to auth-server
- `POST /api/auth/login` - Proxy to auth-server
- `GET /api/auth/profile` - Current user info
- `GET /api/auth/verify-token` - Token validation
- `POST /api/auth/logout` - Client-side logout

**Protected Endpoints:**
- `GET /api/tasks` - User's tasks (requires auth)
- `POST /api/tasks` - Create task (requires auth)
- `GET /api/goals` - User's goals (requires auth)
- And all other CRUD operations...

**Technology:**
- Python 3.12+ with FastAPI
- PostgreSQL database
- PyJWT for token validation
- httpx for auth-server communication

---

## Configuration

### Environment Variables

**Both services must share the same JWT_SECRET:**

**auth-server-ruby (.env):**
```bash
# In /Users/reidchatham/Developer/auth-server-ruby/.env
JWT_SECRET=your-super-secret-key-at-least-32-characters-long-please-change-this
PORT=4567
```

**Bizy Backend (.env):**
```bash
# In /Users/reidchatham/Developer/business-agent/backend/.env
AUTH_SERVER_URL=http://localhost:4567
JWT_SECRET=your-super-secret-key-at-least-32-characters-long-please-change-this
JWT_ALGORITHM=HS256
```

**⚠️ CRITICAL:** Both services MUST use the same JWT_SECRET, otherwise token validation will fail.

### Generate Secure JWT_SECRET

```bash
# Generate a random 64-character hex string
ruby -e "require 'securerandom'; puts SecureRandom.hex(32)"

# Or in Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Setup Instructions

### Option 1: Docker Compose (Recommended)

**Start all services:**
```bash
cd /Users/reidchatham/Developer/business-agent

# Generate JWT secret
JWT_SECRET=$(ruby -e "require 'securerandom'; puts SecureRandom.hex(32)")

# Create .env file
cat > .env <<EOF
POSTGRES_USER=bizy
POSTGRES_PASSWORD=bizy_dev_password
POSTGRES_DB=bizy_dev
JWT_SECRET=$JWT_SECRET
ANTHROPIC_API_KEY=your-anthropic-api-key
EOF

# Start all services (auth-server, postgres, redis, backend, mailhog)
docker-compose up -d

# Check health
curl http://localhost:4567/health  # Auth server
curl http://localhost:8000/health  # Bizy backend
```

**Access points:**
- Auth Server: http://localhost:4567
- Bizy Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- MailHog (email): http://localhost:8025

### Option 2: Local Development

**Terminal 1 - Start auth-server-ruby:**
```bash
cd /Users/reidchatham/Developer/auth-server-ruby

# Setup
cp .env.example .env
nano .env  # Add JWT_SECRET

# Install and run
make setup && make db && make server
```

**Terminal 2 - Start Bizy Backend:**
```bash
cd /Users/reidchatham/Developer/business-agent/backend

# Setup
cp .env.example .env
nano .env  # Add same JWT_SECRET as auth-server

# Install dependencies
source venv/bin/activate
pip install -r requirements-dev.txt

# Run server
./run.sh
```

**Terminal 3 - Test:**
```bash
# Health checks
curl http://localhost:4567/health
curl http://localhost:8000/health
curl http://localhost:8000/api/auth/auth-server-health
```

---

## API Usage Examples

### 1. Register New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecureP@ss123"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully. Please check your email for verification.",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_admin": false,
    "email_verified": false
  }
}
```

### 2. Verify Email (Development)

Check MailHog at http://localhost:8025 for verification email.

### 3. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecureP@ss123"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_admin": false,
    "email_verified": true
  }
}
```

### 4. Access Protected Route

```bash
TOKEN="<token from login>"

curl http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_admin": false,
  "email_verified": true
}
```

### 5. Create Task (Protected)

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My first task",
    "priority": 1,
    "category": "development"
  }'
```

---

## Implementation Details

### JWT Token Structure

**Token Payload (from auth-server-ruby):**
```json
{
  "user_id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_admin": false,
  "exp": 1700000000
}
```

**Token Validation (in Bizy Backend):**
```python
import jwt
from api.auth import decode_token, get_current_user

# Middleware automatically validates token
@app.get("/api/tasks")
async def get_tasks(current_user: TokenData = Depends(get_current_user)):
    # current_user.user_id is automatically extracted
    tasks = query_tasks_for_user(current_user.user_id)
    return tasks
```

### Security Features

**auth-server-ruby provides:**
- ✅ bcrypt password hashing
- ✅ Account lockout (5 failed attempts)
- ✅ Rate limiting
- ✅ Email verification
- ✅ Password reset via email
- ✅ Strong password requirements
- ✅ Input sanitization

**Bizy Backend adds:**
- ✅ JWT token validation
- ✅ User data isolation (via user_id)
- ✅ CORS protection
- ✅ Security headers
- ✅ Request validation (Pydantic)

---

## Testing

### Manual Testing

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@test.com", "password": "Test123!@#"}'

# 2. Check email in MailHog
open http://localhost:8025

# 3. Login (skip verification in dev mode)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "Test123!@#"}'

# 4. Save token and test protected route
TOKEN="<paste token here>"
curl http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"

# 5. Test token validation
curl http://localhost:8000/api/auth/verify-token \
  -H "Authorization: Bearer $TOKEN"
```

### Automated Testing

```python
# tests/test_auth_integration.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_login_flow():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Register
        response = await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test123!@#"
        })
        assert response.status_code == 201

        # Login
        response = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "Test123!@#"
        })
        assert response.status_code == 200
        token = response.json()["token"]

        # Access protected route
        response = await client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
```

---

## Troubleshooting

### Issue: "Invalid token" errors

**Cause:** JWT_SECRET mismatch between services

**Solution:**
```bash
# Check secrets match
echo "Auth server:"
grep JWT_SECRET ~/Developer/auth-server-ruby/.env

echo "Bizy backend:"
grep JWT_SECRET ~/Developer/business-agent/backend/.env

# They should be identical
```

### Issue: "Auth server unavailable"

**Cause:** auth-server-ruby not running

**Solution:**
```bash
# Check if auth server is running
curl http://localhost:4567/health

# If not, start it
cd ~/Developer/auth-server-ruby
make server

# Or with Docker
docker-compose up -d auth-server
```

### Issue: "Token has expired"

**Cause:** JWT tokens expire after 24 hours

**Solution:**
```bash
# Login again to get new token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

### Issue: "User not found" after migration

**Cause:** PostgreSQL database has users from old auth system

**Solution:**
```bash
# Users are managed by auth-server-ruby
# Register via auth server:
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@bizy.local", "password": "Admin123!@#"}'
```

---

## Migration from Old Auth

### If you had old auth code in Bizy Backend:

**Remove old auth code:**
```bash
# Delete old dependencies
# In requirements-dev.txt:
# - python-jose[cryptography]
# - passlib[bcrypt]
# - bcrypt

# Delete old auth routes
rm backend/api/routes/auth.py  # If it existed
```

**Use new auth:**
```python
# Old way (deprecated):
from api.dependencies import get_current_user  # Don't use this

# New way:
from api.auth import get_current_user, TokenData

@app.get("/api/tasks")
async def get_tasks(current_user: TokenData = Depends(get_current_user)):
    # current_user is validated by auth-server-ruby
    return query_tasks(current_user.user_id)
```

---

## Production Deployment

### Environment Variables (Production)

```bash
# Auth Server
JWT_SECRET=<64-character-random-hex>
DATABASE_URL=postgresql://user:pass@host:5432/auth_db
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=<sendgrid-api-key>

# Bizy Backend
AUTH_SERVER_URL=http://auth-server:4567  # Internal Docker network
JWT_SECRET=<same-as-auth-server>
DATABASE_URL=postgresql://user:pass@host:5432/bizy_db
ANTHROPIC_API_KEY=<your-key>
```

### Docker Production

```bash
# Use production docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale backend if needed
docker-compose up -d --scale backend=3
```

---

## Benefits of Microservice Architecture

✅ **Separation of Concerns**
- Auth logic isolated in auth-server-ruby
- Bizy backend focuses on business logic

✅ **Reusability**
- auth-server-ruby can serve multiple applications
- Already battle-tested and production-ready

✅ **Independent Scaling**
- Scale auth server separately from backend
- Different resource requirements

✅ **Technology Choice**
- Ruby for auth (excellent security libraries)
- Python for AI/analytics (excellent ML libraries)

✅ **Independent Development**
- Auth team can work independently
- Backend team doesn't need Ruby knowledge

✅ **Security**
- Centralized authentication
- Single point for security updates

---

## Files Created

```
backend/
├── api/
│   ├── auth.py                     # JWT validation middleware
│   └── routes/
│       └── auth_proxy.py           # Auth proxy routes
├── Dockerfile                      # Backend container
├── requirements-dev.txt            # Updated with PyJWT
└── docs/
    └── AUTH_INTEGRATION.md         # This file

docker-compose.yml                  # Multi-service orchestration
```

---

## Next Steps

1. ✅ **Task 40 Complete** - Auth microservice integration
2. 🔜 **Task 41** - Implement task CRUD with user filtering
3. 🔜 **Task 42** - Implement goal CRUD with user filtering
4. 🔜 **Frontend** - Build React auth UI

---

**Document Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Status:** Complete ✅
