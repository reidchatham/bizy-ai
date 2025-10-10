.PHONY: test install dev clean lint help

help:  ## Show this help message
	@echo "Bizy AI Development Commands"
	@echo "============================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

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
