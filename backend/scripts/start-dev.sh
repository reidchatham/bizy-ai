#!/bin/bash
# Start development servers for local testing
# This script starts all required services for Bizy AI backend testing

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Bizy AI Development Environment${NC}"
echo "=========================================="
echo ""

# Check if running from correct directory
if [ ! -f "backend/run.sh" ]; then
    echo -e "${RED}❌ Error: Must run from project root${NC}"
    echo "   cd /Users/reidchatham/Developer/business-agent"
    exit 1
fi

# Check if auth-server-ruby exists
if [ ! -d "../auth-server-ruby" ]; then
    echo -e "${RED}❌ Error: auth-server-ruby not found${NC}"
    echo "   Expected at: /Users/reidchatham/Developer/auth-server-ruby"
    exit 1
fi

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Check if services are already running
if check_port 4567; then
    echo -e "${YELLOW}⚠️  Port 4567 (auth-server) already in use${NC}"
    if [ -z "$CI" ]; then
        echo "   Kill it? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            lsof -ti:4567 | xargs kill -9
            echo -e "${GREEN}✓ Killed process on port 4567${NC}"
        fi
    else
        # Non-interactive mode (CI or automated deployment)
        lsof -ti:4567 | xargs kill -9
        echo -e "${GREEN}✓ Killed process on port 4567${NC}"
    fi
fi

if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 (backend) already in use${NC}"
    if [ -z "$CI" ]; then
        echo "   Kill it? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            lsof -ti:8000 | xargs kill -9
            echo -e "${GREEN}✓ Killed process on port 8000${NC}"
        fi
    else
        # Non-interactive mode (CI or automated deployment)
        lsof -ti:8000 | xargs kill -9
        echo -e "${GREEN}✓ Killed process on port 8000${NC}"
    fi
fi

# Generate JWT_SECRET if not exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}📝 Creating backend/.env file...${NC}"

    # Generate secure JWT secret
    JWT_SECRET=$(openssl rand -hex 32)

    cp backend/.env.example backend/.env

    # Update JWT_SECRET in backend/.env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-secret-key-change-this-in-production-must-match-auth-server/$JWT_SECRET/" backend/.env
    else
        sed -i "s/your-secret-key-change-this-in-production-must-match-auth-server/$JWT_SECRET/" backend/.env
    fi

    echo -e "${GREEN}✓ Created backend/.env${NC}"
else
    # Extract JWT_SECRET from existing .env
    JWT_SECRET=$(grep JWT_SECRET backend/.env | cut -d '=' -f2)
fi

# Setup auth-server-ruby if needed
cd ../auth-server-ruby

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating auth-server-ruby/.env file...${NC}"
    cp .env.example .env

    # Update JWT_SECRET to match backend
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-secret-key-here/$JWT_SECRET/" .env
    else
        sed -i "s/your-secret-key-here/$JWT_SECRET/" .env
    fi

    echo -e "${GREEN}✓ Created auth-server-ruby/.env${NC}"
fi

# Check if auth-server dependencies installed
if [ ! -d "vendor/bundle" ]; then
    echo -e "${YELLOW}📦 Installing auth-server dependencies...${NC}"
    bundle install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Setup auth-server database
if [ ! -f "db/development.sqlite3" ]; then
    echo -e "${YELLOW}🗄️  Setting up auth-server database...${NC}"
    bundle exec rake db:migrate
    echo -e "${GREEN}✓ Database setup complete${NC}"
fi

# Start auth-server in background
echo ""
echo -e "${BLUE}🔐 Starting auth-server-ruby (port 4567)...${NC}"
bundle exec rackup -p 4567 > /tmp/auth-server.log 2>&1 &
AUTH_PID=$!
echo $AUTH_PID > /tmp/auth-server.pid
echo -e "${GREEN}✓ auth-server-ruby started (PID: $AUTH_PID)${NC}"
echo "   Logs: tail -f /tmp/auth-server.log"

# Wait for auth-server to be ready
sleep 3
if ! check_port 4567; then
    echo -e "${RED}❌ auth-server failed to start${NC}"
    echo "   Check logs: cat /tmp/auth-server.log"
    exit 1
fi

# Test auth-server health
if curl -s http://localhost:4567/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ auth-server health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  auth-server health check failed (may still be starting)${NC}"
fi

# Return to business-agent
cd /Users/reidchatham/Developer/business-agent

# Setup backend if needed
cd backend

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate venv and install dependencies
source venv/bin/activate

if [ ! -f "venv/bin/uvicorn" ]; then
    echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
    pip install -r requirements-dev.txt > /tmp/pip-install.log 2>&1
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Start backend
echo ""
echo -e "${BLUE}🚀 Starting Bizy Backend API (port 8000)...${NC}"
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/backend.pid
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "   Logs: tail -f /tmp/backend.log"

# Wait for backend to be ready
sleep 3
if ! check_port 8000; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "   Check logs: cat /tmp/backend.log"
    kill $AUTH_PID 2>/dev/null
    exit 1
fi

# Test backend health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Backend health check failed (may still be starting)${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Development Environment Ready!"
echo "==========================================${NC}"
echo ""
echo "Services:"
echo "  🔐 Auth Server:  http://localhost:4567"
echo "  🚀 Backend API:  http://localhost:8000"
echo "  📚 API Docs:     http://localhost:8000/api/docs"
echo ""
echo "Logs:"
echo "  Auth Server:     tail -f /tmp/auth-server.log"
echo "  Backend:         tail -f /tmp/backend.log"
echo ""
echo "Stop servers:"
echo "  ./backend/scripts/stop-dev.sh"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for Ctrl+C
trap 'echo -e "\n${YELLOW}Stopping services...${NC}"; kill $AUTH_PID $BACKEND_PID 2>/dev/null; echo -e "${GREEN}✓ Services stopped${NC}"; exit 0' INT

# Keep script running
tail -f /tmp/backend.log /tmp/auth-server.log
