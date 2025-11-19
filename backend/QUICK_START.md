# Quick Start - Bizy AI Backend

Fast setup guide for local testing.

## Prerequisites

```bash
# Check you have everything:
ruby --version      # Need 3.0+
python3 --version   # Need 3.11+
psql --version      # Need PostgreSQL
jq --version        # For JSON parsing

# Install missing tools:
brew install postgresql@16 jq  # macOS
brew services start postgresql@16
```

## Start Everything

```bash
cd /Users/reidchatham/Developer/business-agent
./backend/scripts/start-dev.sh
```

This starts:
- **Auth Server** (port 4567)
- **Backend API** (port 8000)

## Test Everything

```bash
# In another terminal:
./backend/scripts/test-api.sh
```

Output shows 15 test cases passing with a JWT token at the end.

## Use the API

```bash
# Copy token from test output, then:
export TOKEN='eyJhbGciOiJI...'

# List tasks
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" | jq

# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My task", "priority": 1}' | jq
```

## Interactive Docs

Open in browser: http://localhost:8000/api/docs

1. Click "Authorize"
2. Enter: `Bearer YOUR_TOKEN_HERE`
3. Try any endpoint

## Stop Everything

```bash
./backend/scripts/stop-dev.sh
```

## View Logs

```bash
# Backend logs
tail -f /tmp/backend.log

# Auth server logs
tail -f /tmp/auth-server.log
```

## Full Documentation

See [TESTING.md](docs/TESTING.md) for comprehensive guide.

## Common Commands

```bash
# Restart everything
./backend/scripts/stop-dev.sh && ./backend/scripts/start-dev.sh

# Check services are running
curl http://localhost:4567/health
curl http://localhost:8000/health

# Database access
psql -U postgres -d bizy_dev
```

## Troubleshooting

**Port already in use?**
```bash
lsof -ti:4567 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

**PostgreSQL not running?**
```bash
brew services start postgresql@16
```

**Token expired?**
```bash
# Re-run test to get fresh token
./backend/scripts/test-api.sh
```

---

That's it! You're ready to develop. 🚀
