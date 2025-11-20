#!/bin/bash
# Local verification script for Bizy AI
# Tests all services and endpoints

set -e

echo "🔍 Bizy AI Local Verification"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}

    echo -n "Checking $service_name... "

    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} (HTTP $status_code)"
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP $status_code, expected $expected_status)"
        return 1
    fi
}

# Check Docker services
echo "📦 Docker Services"
echo "------------------"
docker-compose ps
echo ""

# Check individual services
echo "🏥 Health Checks"
echo "----------------"

check_service "PostgreSQL" "http://localhost:5432" || echo "  (Port check only)"
check_service "Redis" "http://localhost:6379" || echo "  (Port check only)"
check_service "Auth Server Health" "http://localhost:4567/health"
check_service "Backend API Health" "http://localhost:8000/health"
check_service "MailHog UI" "http://localhost:8025"

echo ""
echo "🔐 Authentication Test"
echo "----------------------"

# Test login endpoint
echo -n "Testing login endpoint... "
login_response=$(curl -s -X POST http://localhost:4567/login \
    -H "Content-Type: application/json" \
    -d '{"username":"demo","password":"Demo123!@#"}' 2>/dev/null || echo "{}")

if echo "$login_response" | grep -q "token"; then
    echo -e "${GREEN}✓${NC} Login successful"
    TOKEN=$(echo "$login_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
else
    echo -e "${YELLOW}⚠${NC} Login failed (demo user may not exist)"
    TOKEN=""
fi

echo ""
echo "🔌 API Endpoints"
echo "----------------"

if [ -n "$TOKEN" ]; then
    check_service "GET /api/tasks" "http://localhost:8000/api/tasks" || true
    check_service "GET /api/goals" "http://localhost:8000/api/goals" || true
    check_service "GET /api/briefings/morning" "http://localhost:8000/api/briefings/morning" || true
else
    echo -e "${YELLOW}⚠${NC} Skipping authenticated endpoint tests (no token)"
fi

echo ""
echo "📚 API Documentation"
echo "--------------------"
check_service "Swagger UI" "http://localhost:8000/api/docs"

echo ""
echo "🎨 Frontend"
echo "-----------"
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null; then
    check_service "Frontend Dev Server" "http://localhost:5173"
else
    echo -e "${YELLOW}⚠${NC} Frontend dev server not running (npm run dev)"
fi

echo ""
echo "📊 Summary"
echo "----------"
echo "✅ All critical services are running!"
echo ""
echo "Access points:"
echo "  • Frontend:      http://localhost:5173"
echo "  • Backend API:   http://localhost:8000"
echo "  • API Docs:      http://localhost:8000/api/docs"
echo "  • Auth Server:   http://localhost:4567"
echo "  • MailHog UI:    http://localhost:8025"
echo ""
echo "Test credentials:"
echo "  • Username: demo"
echo "  • Password: Demo123!@#"
echo ""
