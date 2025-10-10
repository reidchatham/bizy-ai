# Contributing to Bizy AI

Thank you for your interest in contributing to Bizy AI! This document provides guidelines and best practices for development.

## Development Philosophy

Bizy AI follows **Test-Driven Development (TDD)** principles. All contributions should include tests.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/bizy-ai.git
cd bizy-ai
```

### 2. Install Development Dependencies

```bash
# Install package with dev dependencies
make install-dev

# Or manually:
pip install -e ".[dev]"
```

### 3. Set Up Development Environment

```bash
# Initialize development database
make dev

# Or manually:
export BIZY_ENV=development
./scripts/dev_setup.sh
```

## Test-Driven Development (TDD) Workflow

### The TDD Cycle

1. **🔴 Red** - Write a failing test first
2. **🟢 Green** - Write minimal code to make it pass
3. **🔵 Refactor** - Clean up code while keeping tests passing

### Example TDD Workflow

```bash
# 1. Write a test that fails
vim tests/test_new_feature.py

# 2. Run the test (it should fail)
make test

# 3. Implement the feature
vim agent/new_feature.py

# 4. Run the test again (it should pass)
make test

# 5. Refactor if needed
# 6. Run tests again to ensure nothing broke
make test
```

## Database Environments

Bizy AI uses three separate database environments:

- **Test**: In-memory SQLite (`:memory:`) - Clean for each test
- **Development**: `~/.business-agent/dev_tasks.db` - Safe for experimentation
- **Production**: `~/.business-agent/tasks.db` - Your actual business data

### Switching Environments

```bash
# Test environment (automatically set by pytest)
export BIZY_ENV=test

# Development environment
export BIZY_ENV=development

# Production environment (default)
export BIZY_ENV=production
```

### Important Rules

✅ **DO**:
- Always use development database for testing features
- Write tests before implementing features
- Run tests before committing
- Use the Bizy CLI for database operations

❌ **DON'T**:
- Never directly edit the production database
- Never commit code without tests
- Never skip running tests before pushing

## Running Tests

```bash
# Run all tests with coverage
make test

# Run tests in watch mode (auto-runs on file changes)
make test-watch

# Run specific test file
pytest tests/test_tasks.py -v

# Run specific test function
pytest tests/test_tasks.py::test_create_task -v
```

## Code Style

```bash
# Format code with Black
make lint

# This runs:
# - black agent/ tests/  (auto-formatter)
# - flake8 agent/ tests/ (linter)
```

## Writing Tests

### Test Structure

```python
# tests/test_feature.py
import pytest
from agent.your_module import YourClass

class TestYourFeature:
    """Test YourFeature functionality"""

    def test_basic_functionality(self, test_session):
        """Test basic feature works correctly"""
        # Arrange
        obj = YourClass()

        # Act
        result = obj.do_something()

        # Assert
        assert result == expected_value
```

### Using Fixtures

```python
def test_with_sample_data(test_session, sample_goal, sample_task):
    """Use fixtures for common test data"""
    # test_session, sample_goal, sample_task are provided by conftest.py
    assert sample_goal.id is not None
    assert sample_task.id is not None
```

### Mocking AI Calls

```python
from unittest.mock import Mock, patch

@patch('agent.planner.anthropic.Anthropic')
def test_ai_feature(mock_anthropic, test_session):
    """Mock Anthropic API calls in tests"""
    # Set up mock
    mock_response = Mock()
    mock_response.content = [Mock(text='{"result": "test"}')]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    # Test your feature
    result = your_ai_function()
    assert result is not None
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first (TDD!)**
   ```bash
   vim tests/test_your_feature.py
   make test  # Should fail
   ```

3. **Implement the feature**
   ```bash
   vim agent/your_feature.py
   make test  # Should pass
   ```

4. **Ensure all tests pass**
   ```bash
   make test
   make lint
   ```

5. **Commit with meaningful messages**
   ```bash
   git add .
   git commit -m "Add feature: descriptive message

   - Added tests for X
   - Implemented Y
   - Updated documentation"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Commit Message Guidelines

```
<type>: <subject>

<body>

<footer>
```

### Types:
- **feat**: New feature
- **fix**: Bug fix
- **test**: Adding tests
- **docs**: Documentation changes
- **refactor**: Code refactoring
- **style**: Formatting changes
- **chore**: Maintenance tasks

### Example:
```
feat: Add goal assignment to task creation

- Added interactive goal selection during task creation
- Users can now choose existing goal or create new one
- Updated CLI with --goal/-g option
- Added comprehensive tests for goal assignment

Closes #123
```

## Testing Checklist

Before submitting a PR, ensure:

- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make lint`)
- [ ] New features have tests
- [ ] Tests follow TDD principles (written first)
- [ ] Used development database, not production
- [ ] Documentation updated if needed
- [ ] No direct database modifications in code

## Questions?

Open an issue or reach out to the maintainers!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
