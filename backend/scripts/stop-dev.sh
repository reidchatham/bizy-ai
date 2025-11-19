#!/bin/bash
# Stop development servers

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Stopping Bizy AI development servers..."

# Stop auth-server
if [ -f /tmp/auth-server.pid ]; then
    AUTH_PID=$(cat /tmp/auth-server.pid)
    if kill -0 $AUTH_PID 2>/dev/null; then
        kill $AUTH_PID
        echo -e "${GREEN}✓ Stopped auth-server (PID: $AUTH_PID)${NC}"
    fi
    rm /tmp/auth-server.pid
fi

# Stop backend
if [ -f /tmp/backend.pid ]; then
    BACKEND_PID=$(cat /tmp/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo -e "${GREEN}✓ Stopped backend (PID: $BACKEND_PID)${NC}"
    fi
    rm /tmp/backend.pid
fi

# Kill any remaining processes on ports
lsof -ti:4567 | xargs kill -9 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null

echo -e "${GREEN}✓ All services stopped${NC}"
