# CLAUDE.md - Bizy AI Project Instructions

This file provides guidance to Claude Code when working in the business-agent repository.

## Project Overview

Bizy AI is a full-stack AI-powered business planning and execution platform:
- **CLI Agent** (`agent/`): Python Click-based CLI with SQLite, Claude API integration
- **Backend API** (`backend/`): FastAPI REST API with PostgreSQL, JWT authentication
- **Frontend** (`frontend/`): React + TypeScript + Vite SPA with Tailwind CSS

## Development Commands

### CLI Agent
```bash
bizy task list                  # List tasks (scoped to current repo)
bizy task add "Title" -p 1      # Add task (1=high, 2=medium, 3=low)
bizy task complete <ID>         # Complete a task
bizy goal list                  # List goals
bizy goal add "Title" -h yearly # Add goal
bizy brief                      # AI morning briefing
bizy stats                      # View statistics
export BIZY_ENV=test            # Use test database
python -m pytest tests/ -v      # Run CLI tests
```

### Backend API
```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v --cov=api      # Run tests with coverage
black api/ tests/               # Format code
isort api/ tests/               # Sort imports
flake8 api/ tests/              # Lint code
```

### Frontend
```bash
cd frontend
npm install
npm run dev                     # Development server
npm run build                   # Production build
npm run lint                    # Run ESLint
npx tsc --noEmit                # Type check
```

### Docker
```bash
docker-compose up -d            # Start all services
docker-compose logs -f backend  # View backend logs
docker-compose exec backend pytest tests/ -v  # Run tests in container
```

## Session Protocol for AI Development

### Starting a Session
1. Run `bizy task list` to see current tasks
2. Run `bizy goal list` to check goal progress
3. Identify highest priority incomplete task
4. Use TodoWrite to plan execution steps

### During Development
1. Mark task as in-progress in your todo list
2. Write tests FIRST (TDD required)
3. Run tests frequently: `pytest tests/ -v`
4. Commit working code in small increments

### Ending a Session
1. Run full test suite, ensure all pass
2. Update CHANGELOG.md with changes
3. Mark bizy task complete: `bizy task complete <ID>`
4. Commit with descriptive message

### Test-Driven Development (Required)
1. Write failing test first
2. Implement minimal code to pass
3. Refactor while keeping tests green
4. Maintain 80%+ coverage

## Architecture Notes

### Backend API Structure (`backend/api/`)
- `main.py` - FastAPI app with CORS, routes
- `auth.py` - JWT authentication with get_current_user dependency
- `dependencies.py` - Database session management
- `routes/` - API endpoint handlers (tasks, goals, analytics, ai)

### Testing Patterns
- Use `app.dependency_overrides[get_current_user]` for auth mocking
- Create fixtures in `conftest.py` for test data
- Authorization tests need manual override switching for multi-user scenarios

### Database
- CLI: SQLite with SQLAlchemy ORM
- Backend: PostgreSQL (production), SQLite (testing)
- Models in `models/` directory

## CI/CD Pipeline

### Continuous Integration (`.github/workflows/ci.yml`)
- Backend: lint (black, isort, flake8), typecheck (mypy), test (pytest)
- Frontend: lint (ESLint), typecheck (tsc), build
- Docker: Build validation for both images

### Continuous Deployment (`.github/workflows/deploy.yml`)
- Triggers on push to main (after CI passes)
- Deploys to DigitalOcean App Platform
- Runs smoke tests post-deployment

## Key Files

| File | Purpose |
|------|---------|
| `app.yaml` | DigitalOcean App Platform config |
| `docker-compose.yml` | Local development stack |
| `backend/tests/conftest.py` | Test fixtures and auth mocking |
| `.github/workflows/ci.yml` | CI pipeline definition |
| `.github/workflows/deploy.yml` | CD pipeline definition |

## Current Status

- **Launch MVP Goal**: Track progress with `bizy goal list`
- **Task 43**: Backend API tests - 80%+ coverage target
- **Phase**: Backend complete, tests complete, CI/CD configured
