#!/bin/bash
# Quick script to run the FastAPI server

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 Starting Bizy AI Backend Server..."
echo ""

# Check if we're in the backend directory
if [[ ! -f "api/main.py" ]]; then
    echo -e "${RED}❌ Error: Run this script from the backend/ directory${NC}"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo -e "${RED}❌ Error: Virtual environment not found${NC}"
    echo "   Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo "   Creating from template..."
    cp .env.example .env
    echo -e "${YELLOW}   IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY${NC}"
    echo ""
fi

# Check if ANTHROPIC_API_KEY is set
if ! grep -q "ANTHROPIC_API_KEY=sk-" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: ANTHROPIC_API_KEY not configured in .env${NC}"
    echo ""
fi

# Get port from command line or use default
PORT="${1:-8000}"

echo "📍 Server will start at: http://localhost:$PORT"
echo "📚 API Docs: http://localhost:$PORT/api/docs"
echo "❤️  Health Check: http://localhost:$PORT/health"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop the server${NC}"
echo ""

# Run the server
uvicorn api.main:app --reload --host 0.0.0.0 --port $PORT
