#!/bin/bash
# Run test suite with coverage

echo "🧪 Running Bizy AI Test Suite..."
echo "================================"
echo ""

# Set test environment
export BIZY_ENV=test

# Run tests with coverage
pytest tests/ -v --cov=agent --cov-report=html --cov-report=term

echo ""
echo "✅ Tests complete!"
echo "📊 Coverage report generated in htmlcov/index.html"
