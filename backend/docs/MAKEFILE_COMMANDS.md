# Makefile Commands Reference

Quick reference for all `make` commands available in Bizy AI.

---

## Quick Start

```bash
# See all available commands
make help

# Initial setup with Docker
make setup

# Start services
make up

# Check status
make status

# Stop services
make down
```

---

## Command Categories

### Development (Bizy CLI)

| Command | Description |
|---------|-------------|
| `make test` | Run test suite with coverage |
| `make test-watch` | Run tests in watch mode |
| `make install` | Install package in editable mode |
| `make install-dev` | Install with dev dependencies |
| `make dev` | Set up development environment |
| `make clean` | Clean temporary files and caches |
| `make lint` | Format code with black and flake8 |

### Docker Deployment

| Command | Description |
|---------|-------------|
| `make docker-build` | Build Docker images |
| `make docker-up` | Start all services with Docker Compose |
| `make docker-down` | Stop and remove containers |
| `make docker-down-volumes` | Stop and remove containers + data |
| `make docker-restart` | Restart all services |
| `make docker-ps` | Show running containers |
| `make docker-stats` | Show resource usage |

### Docker Logs

| Command | Description |
|---------|-------------|
| `make logs` | View all service logs (follow mode) |
| `make logs-backend` | View backend logs |
| `make logs-auth` | View auth server logs |
| `make logs-postgres` | View PostgreSQL logs |

### Database Management

| Command | Description |
|---------|-------------|
| `make db-migrate` | Run database migrations |
| `make db-shell` | Open PostgreSQL shell |
| `make db-backup` | Backup PostgreSQL database |
| `make db-reset` | Reset database (WARNING: deletes all data) |

### Testing

| Command | Description |
|---------|-------------|
| `make test-api` | Run automated API tests |
| `make test-verify` | Verify deployment health |

### User Management

| Command | Description | Example |
|---------|-------------|---------|
| `make user-create` | Create new user | `make user-create USERNAME=admin EMAIL=admin@example.com PASSWORD=Admin123!` |
| `make user-verify` | Verify user email | `make user-verify USERNAME=admin` |
| `make user-admin` | Promote user to admin | `make user-admin USERNAME=admin` |
| `make user-list` | List all users | `make user-list` |

### Setup & Deployment

| Command | Description |
|---------|-------------|
| `make setup` | Initial Docker deployment setup |
| `make dev-local` | Start local development (non-Docker) |
| `make dev-local-stop` | Stop local development servers |

### Health & Status

| Command | Description |
|---------|-------------|
| `make health` | Check health of all services |
| `make status` | Show comprehensive status |
| `make urls` | Display all service URLs |
| `make docs` | Open API documentation in browser |

### Shortcuts

| Command | Alias For | Description |
|---------|-----------|-------------|
| `make up` | `make docker-up` | Start services |
| `make down` | `make docker-down` | Stop services |
| `make ps` | `make docker-ps` | Show containers |
| `make build` | `make docker-build` | Build images |

---

## Common Workflows

### First Time Setup

```bash
# 1. Initial deployment
make setup

# 2. Create admin user
make user-create USERNAME=admin EMAIL=admin@example.com PASSWORD=Admin123!

# 3. Verify and promote to admin
make user-verify USERNAME=admin
make user-admin USERNAME=admin

# 4. Check everything is working
make test-verify
```

### Daily Development

```bash
# Start services
make up

# View logs
make logs-backend

# Check status
make status

# Stop when done
make down
```

### Making Code Changes

```bash
# 1. Make code changes to backend/

# 2. Rebuild and restart backend
docker-compose build backend
docker-compose up -d backend

# 3. Check logs
make logs-backend

# 4. Test changes
make test-api
```

### Database Operations

```bash
# Backup database
make db-backup

# Run migrations
make db-migrate

# Open PostgreSQL shell
make db-shell

# Reset database (WARNING: deletes data)
make db-reset
```

### User Management

```bash
# Create a new user
make user-create USERNAME=john EMAIL=john@example.com PASSWORD=Secret123!

# Verify their email (skip email in development)
make user-verify USERNAME=john

# List all users
make user-list

# Promote to admin
make user-admin USERNAME=john
```

### Troubleshooting

```bash
# Check service health
make health

# View all logs
make logs

# View specific service logs
make logs-backend
make logs-auth
make logs-postgres

# Check container status
make ps

# Restart everything
make docker-restart

# Full reset (nuclear option)
make docker-down-volumes
make setup
```

---

## Examples

### Example 1: Fresh Deployment

```bash
$ make setup
🔵 Setting up Bizy AI with Docker...
🔵 Building Docker images...
🔵 Starting Docker services...
✅ Services started!
🔵 Running database migrations...
✅ Setup complete!

Next steps:
  1. Create user: make user-create USERNAME=admin EMAIL=admin@example.com PASSWORD=Admin123!
  2. Verify: make user-verify USERNAME=admin
  3. Admin: make user-admin USERNAME=admin
  4. Visit: http://localhost:8000/api/docs
```

### Example 2: Creating a User

```bash
$ make user-create USERNAME=alice EMAIL=alice@example.com PASSWORD=Secret123!
{"message":"Registration successful. Please check your email to verify your account.","user_id":2}

$ make user-verify USERNAME=alice
User verified

$ make user-admin USERNAME=alice
User promoted to admin
```

### Example 3: Checking Status

```bash
$ make status
🔵 Bizy AI Status
==================================

🟡 Containers:
NAMES              STATUS                    PORTS
bizy-backend       Up 10 minutes (healthy)   0.0.0.0:8000->8000/tcp
bizy-auth-server   Up 10 minutes (healthy)   0.0.0.0:4567->4567/tcp
bizy-postgres      Up 10 minutes (healthy)   0.0.0.0:5432->5432/tcp
bizy-redis         Up 10 minutes (healthy)   0.0.0.0:6379->6379/tcp
bizy-mailhog       Up 10 minutes             0.0.0.0:1025->1025/tcp, 0.0.0.0:8025->8025/tcp

🟡 Health:
Backend:      ✓
Auth Server:  ✓

🟡 URLs:
  Backend:     http://localhost:8000
  API Docs:    http://localhost:8000/api/docs
  Auth:        http://localhost:4567
  MailHog:     http://localhost:8025
```

### Example 4: Database Backup

```bash
$ make db-backup
🔵 Backing up database...
✓ Backup saved to backups/

$ ls backups/
bizy_backup_20251119_154530.sql
```

### Example 5: Running Tests

```bash
$ make test-verify
🔍 Bizy AI Deployment Verification
==========================================

1. Docker Status
✓ Docker is running

2. Container Status
Container bizy-postgres... ✓ (Up 1 hour (healthy))
Container bizy-redis... ✓ (Up 1 hour (healthy))
Container bizy-mailhog... ✓ (Up 1 hour)
Container bizy-auth-server... ✓ (Up 1 hour (healthy))
Container bizy-backend... ✓ (Up 1 hour (healthy))

3. Service Health Checks
Checking Backend API... ✓
Checking Auth Server... ✓

...

==========================================
✅ All checks passed! Deployment verified.
```

---

## Tips

### Viewing Logs in Real-Time

```bash
# All services
make logs

# Specific service
make logs-backend

# Stop following with Ctrl+C
```

### Quick Status Check

```bash
# One command to see everything
make status
```

### Database Shell Access

```bash
# PostgreSQL shell
make db-shell

# Then run SQL:
SELECT * FROM users;
\q  # to exit
```

### Opening API Documentation

```bash
# Opens Swagger UI in browser
make docs
```

---

## Environment Variables

The Makefile automatically creates a `.env` file with:

```bash
JWT_SECRET=<randomly-generated-64-char-hex>
```

Additional variables can be added to `.env`:

```bash
# Database
POSTGRES_USER=bizy
POSTGRES_PASSWORD=bizy_dev_password
POSTGRES_DB=bizy_dev

# Ports
API_PORT=8000
POSTGRES_PORT=5432
REDIS_PORT=6379

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Troubleshooting Common Issues

### "make: command not found"

Install make:
```bash
# macOS
xcode-select --install

# Ubuntu
sudo apt install make
```

### "docker-compose: command not found"

Install Docker Desktop:
https://www.docker.com/products/docker-desktop

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000

# Kill the process
lsof -ti:8000 | xargs kill -9

# Or let docker-compose handle it
make docker-restart
```

### Services Not Starting

```bash
# Check logs
make logs

# Try full restart
make down
make up

# Nuclear option
make docker-down-volumes
make setup
```

---

## Advanced Usage

### Running Specific Migrations

```bash
# Inside backend container
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic downgrade -1

# Inside auth-server container
docker-compose exec auth-server bundle exec rake db:migrate
docker-compose exec auth-server bundle exec rake db:rollback
```

### Accessing Container Shells

```bash
# Backend (Python)
docker-compose exec backend bash

# Auth server (Ruby)
docker-compose exec auth-server bash

# PostgreSQL
docker-compose exec postgres bash
```

### Custom Database Backups

```bash
# Backup to specific file
docker-compose exec postgres pg_dump -U bizy bizy_dev > my_backup.sql

# Restore from specific file
cat my_backup.sql | docker-compose exec -T postgres psql -U bizy bizy_dev
```

---

## See Also

- [Deployment Guide](DEPLOYMENT_DOCKER.md) - Comprehensive deployment documentation
- [Testing Guide](TESTING.md) - Local testing instructions
- [API Documentation](http://localhost:8000/api/docs) - Swagger UI (when running)

---

**Quick Reference Card:**

```
make setup          - First time setup
make up             - Start all services
make down           - Stop all services
make status         - Check everything
make logs-backend   - View backend logs
make test-verify    - Run health checks
make help           - Show all commands
```
