# Bizy AI - FastAPI Backend

FastAPI backend for Phase 3 web interface.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Copy example
cp .env.example .env

# Edit with your values
ANTHROPIC_API_KEY=your-key-here
DATABASE_URL=sqlite:///~/.business-agent/tasks.db
JWT_SECRET=your-secret-key-change-this-in-production
```

### 3. Run Development Server

```bash
# Option 1: Using uvicorn directly
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
cd backend
python -m api.main

# Option 3: From project root
cd ..
python -m backend.api.main
```

### 4. Access API

- **API Root:** http://localhost:8000/
- **API Docs (Swagger):** http://localhost:8000/api/docs
- **API Docs (ReDoc):** http://localhost:8000/api/redoc
- **Health Check:** http://localhost:8000/health

## Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── dependencies.py      # Dependency injection (DB, auth)
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── tasks.py         # Task CRUD
│   │   ├── goals.py         # Goal CRUD
│   │   ├── briefings.py     # Briefings
│   │   ├── analytics.py     # Analytics
│   │   └── dashboard.py     # Dashboard
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   ├── middleware/          # Custom middleware
│   └── websocket/           # WebSocket handlers
├── tests/                   # Backend tests
├── scripts/                 # Utility scripts
├── migrations/              # Alembic migrations
├── config.py                # Configuration
└── requirements.txt         # Python dependencies
```

## Development

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=api --cov-report=html

# Specific test file
pytest tests/test_auth.py -v
```

### Code Quality

```bash
# Format code
black api/
isort api/

# Lint
flake8 api/
mypy api/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

### Authentication (TODO)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Tasks (TODO)
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/{id}/complete` - Complete task

### Goals (TODO)
- `GET /api/goals` - List goals
- `POST /api/goals` - Create goal
- `GET /api/goals/{id}` - Get goal
- `PATCH /api/goals/{id}` - Update goal
- `DELETE /api/goals/{id}` - Delete goal
- `POST /api/goals/{id}/breakdown` - AI breakdown

### Briefings (TODO)
- `POST /api/briefings/morning` - Generate morning briefing
- `POST /api/briefings/evening` - Generate evening review
- `GET /api/briefings/weekly` - Get weekly report

### Analytics (TODO)
- `GET /api/analytics/stats` - Get statistics
- `GET /api/analytics/velocity` - Get velocity data
- `GET /api/analytics/goal-progress` - Get goal progress

### Dashboard (TODO)
- `GET /api/dashboard/summary` - Get dashboard summary

### WebSocket (TODO)
- `WS /ws/updates` - Real-time updates

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `False` | Enable debug mode |
| `ENVIRONMENT` | `development` | Environment (development, staging, production) |
| `API_HOST` | `0.0.0.0` | API host |
| `API_PORT` | `8000` | API port |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS allowed origins |
| `DATABASE_URL` | SQLite path | Database connection URL |
| `POSTGRES_*` | Various | PostgreSQL connection details |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `JWT_SECRET` | (required) | JWT secret key |
| `ANTHROPIC_API_KEY` | (required) | Anthropic API key |
| `SENDGRID_API_KEY` | (optional) | SendGrid API key |

## Next Steps

1. ✅ FastAPI project structure setup
2. ⏳ Implement authentication endpoints
3. ⏳ Implement task CRUD endpoints
4. ⏳ Implement goal CRUD endpoints
5. ⏳ Add WebSocket support
6. ⏳ Write tests

## License

MIT
