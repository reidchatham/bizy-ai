#!/bin/bash
# Initialize development environment

echo "🚀 Setting up Bizy AI Development Environment..."
echo "================================================"
echo ""

# Set development environment
export BIZY_ENV=development

# Initialize development database
echo "📦 Initializing development database..."
python3 -c "from agent.models import init_database; init_database()"

echo ""
echo "✅ Development environment ready!"
echo ""
echo "📍 Database location: ~/.business-agent/dev_tasks.db"
echo "🔧 Environment: BIZY_ENV=development"
echo ""
echo "To use development mode, run:"
echo "  export BIZY_ENV=development"
echo ""
echo "Happy coding! 🎉"
