.PHONY: test install dev clean lint help docker-up docker-down docker-build docker-ps logs status

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help:  ## Show this help message
	@echo "$(BLUE)Bizy AI Development Commands$(NC)"
	@echo "============================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

test:  ## Run test suite with coverage
	@export BIZY_ENV=test && pytest tests/ -v --cov=agent --cov-report=html --cov-report=term

test-watch:  ## Run tests in watch mode (requires pytest-watch)
	@export BIZY_ENV=test && ptw tests/ -- -v

install:  ## Install package in editable mode
	@pipx install -e .

install-dev:  ## Install package with development dependencies
	@python3 -m pip install -e ".[dev]"

dev:  ## Set up development environment
	@./scripts/dev_setup.sh

clean:  ## Clean up temporary files and caches
	@rm -rf tests/__pycache__ agent/__pycache__ scripts/__pycache__
	@rm -rf .pytest_cache .coverage htmlcov
	@rm -f tests/test_tasks.db ~/.business-agent/dev_tasks.db
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✨ Cleaned up temporary files"

lint:  ## Format code with black and check with flake8
	@black agent/ tests/
	@flake8 agent/ tests/ --max-line-length=120

prod:  ## Reminder to use production database
	@echo "⚠️  Production Mode"
	@echo "==================="
	@echo "Run: export BIZY_ENV=production"
	@echo "Database: ~/.business-agent/tasks.db"

##@ Docker Deployment

docker-build:  ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker-compose build

docker-up:  ## Start all services with Docker Compose
	@echo "$(BLUE)Starting Docker services...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file with JWT_SECRET...$(NC)"; \
		echo "JWT_SECRET=$$(openssl rand -hex 32)" > .env; \
	fi
	@docker-compose up -d
	@sleep 5
	@echo "$(GREEN)✅ Services started!$(NC)"
	@make docker-ps

docker-down:  ## Stop and remove Docker containers
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	@docker-compose down

docker-down-volumes:  ## Stop and remove containers AND data volumes
	@echo "$(YELLOW)WARNING: This will delete all data!$(NC)"
	@sleep 3
	@docker-compose down -v

docker-restart:  ## Restart all Docker services
	@docker-compose restart

docker-ps:  ## Show running Docker containers
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

docker-stats:  ## Show Docker container resource usage
	@docker stats --no-stream

##@ Docker Logs

logs:  ## View all Docker service logs
	@docker-compose logs --tail=50 --follow

logs-backend:  ## View backend logs
	@docker-compose logs backend --tail=50 --follow

logs-auth:  ## View auth server logs
	@docker-compose logs auth-server --tail=50 --follow

logs-postgres:  ## View PostgreSQL logs
	@docker-compose logs postgres --tail=50 --follow

##@ Database Management

db-migrate:  ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@docker-compose exec auth-server bundle exec rake db:migrate
	@docker-compose exec backend alembic upgrade head

db-shell:  ## Open PostgreSQL shell
	@docker-compose exec postgres psql -U bizy -d bizy_dev

db-backup:  ## Backup PostgreSQL database
	@echo "$(BLUE)Backing up database...$(NC)"
	@mkdir -p backups
	@docker-compose exec postgres pg_dump -U bizy bizy_dev > backups/bizy_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup saved to backups/$(NC)"

db-reset:  ## Reset database (WARNING: deletes all data)
	@echo "$(YELLOW)WARNING: This will delete all data!$(NC)"
	@sleep 3
	@docker-compose down -v
	@docker-compose up -d postgres redis
	@sleep 5
	@make db-migrate

##@ Testing

test-api:  ## Run automated API tests
	@./backend/scripts/test-api.sh

test-verify:  ## Verify deployment health
	@./backend/scripts/verify-deployment.sh

##@ User Management

user-create:  ## Create new user (make user-create USERNAME=admin EMAIL=admin@example.com PASSWORD=pass)
	@if [ -z "$(USERNAME)" ] || [ -z "$(EMAIL)" ] || [ -z "$(PASSWORD)" ]; then \
		echo "$(YELLOW)Usage: make user-create USERNAME=admin EMAIL=admin@example.com PASSWORD=Admin123!$(NC)"; \
		exit 1; \
	fi
	@curl -X POST http://localhost:4567/register \
		-H "Content-Type: application/json" \
		-d '{"username":"$(USERNAME)","email":"$(EMAIL)","password":"$(PASSWORD)"}'
	@echo ""

user-verify:  ## Verify user email (make user-verify USERNAME=admin)
	@if [ -z "$(USERNAME)" ]; then \
		echo "$(YELLOW)Usage: make user-verify USERNAME=admin$(NC)"; \
		exit 1; \
	fi
	@docker-compose exec auth-server bundle exec ruby -e " \
		require './app'; \
		user = User.find_by(username: '$(USERNAME)'); \
		user&.update(email_verified: true); \
		puts 'User verified'"

user-admin:  ## Promote user to admin (make user-admin USERNAME=admin)
	@if [ -z "$(USERNAME)" ]; then \
		echo "$(YELLOW)Usage: make user-admin USERNAME=admin$(NC)"; \
		exit 1; \
	fi
	@docker-compose exec auth-server bundle exec ruby -e " \
		require './app'; \
		user = User.find_by(username: '$(USERNAME)'); \
		user&.update(is_admin: true); \
		puts 'User promoted to admin'"

user-list:  ## List all users
	@docker-compose exec auth-server bundle exec ruby -e " \
		require './app'; \
		User.all.each { |u| puts \"#{u.id} | #{u.username} | #{u.email} | Verified: #{u.email_verified}\" }"

##@ Setup & Deployment

setup:  ## Initial Docker deployment setup
	@echo "$(BLUE)Setting up Bizy AI with Docker...$(NC)"
	@make docker-build
	@make docker-up
	@sleep 5
	@make db-migrate
	@echo ""
	@echo "$(GREEN)✅ Setup complete!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Create user: make user-create USERNAME=admin EMAIL=admin@example.com PASSWORD=Admin123!"
	@echo "  2. Verify: make user-verify USERNAME=admin"
	@echo "  3. Admin: make user-admin USERNAME=admin"
	@echo "  4. Visit: http://localhost:8000/api/docs"

dev-local:  ## Start local development (non-Docker)
	@./backend/scripts/start-dev.sh

dev-local-stop:  ## Stop local development servers
	@./backend/scripts/stop-dev.sh

##@ Health & Status

health:  ## Check health of all services
	@echo "$(BLUE)Service Health:$(NC)"
	@echo -n "Backend:      "
	@curl -s http://localhost:8000/health | grep -q "healthy" && echo "$(GREEN)✓$(NC)" || echo "$(YELLOW)✗$(NC)"
	@echo -n "Auth Server:  "
	@curl -s http://localhost:4567/health | grep -q "ok" && echo "$(GREEN)✓$(NC)" || echo "$(YELLOW)✗$(NC)"

status:  ## Show comprehensive status
	@echo "$(BLUE)Bizy AI Status$(NC)"
	@echo "=================================="
	@echo ""
	@echo "$(YELLOW)Containers:$(NC)"
	@make docker-ps
	@echo ""
	@echo "$(YELLOW)Health:$(NC)"
	@make health
	@echo ""
	@echo "$(YELLOW)URLs:$(NC)"
	@echo "  Backend:     http://localhost:8000"
	@echo "  API Docs:    http://localhost:8000/api/docs"
	@echo "  Auth:        http://localhost:4567"
	@echo "  MailHog:     http://localhost:8025"

urls:  ## Display all service URLs
	@echo "$(BLUE)Service URLs:$(NC)"
	@echo "  Backend API:    http://localhost:8000"
	@echo "  API Docs:       http://localhost:8000/api/docs"
	@echo "  Auth Server:    http://localhost:4567"
	@echo "  MailHog UI:     http://localhost:8025"

docs:  ## Open API documentation
	@open http://localhost:8000/api/docs

##@ Shortcuts

up: docker-up  ## Alias for docker-up
down: docker-down  ## Alias for docker-down
ps: docker-ps  ## Alias for docker-ps
build: docker-build  ## Alias for docker-build
