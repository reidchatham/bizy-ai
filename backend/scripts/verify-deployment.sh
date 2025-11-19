#!/bin/bash
# Verify Docker deployment of Bizy AI
# Runs comprehensive checks on all deployed services

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔍 Bizy AI Deployment Verification${NC}"
echo "=========================================="
echo ""

ERRORS=0

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "Checking $name... "

    response=$(curl -s "$url" || echo "FAILED")

    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        echo "  Expected: $expected"
        echo "  Got: $response"
        ((ERRORS++))
        return 1
    fi
}

# Function to check container
check_container() {
    local container=$1

    echo -n "Container $container... "

    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        status=$(docker ps --format '{{.Status}}' --filter "name=^${container}$")
        echo -e "${GREEN}✓${NC} ($status)"
        return 0
    else
        echo -e "${RED}✗ Not running${NC}"
        ((ERRORS++))
        return 1
    fi
}

# 1. Check Docker is running
echo -e "${BLUE}1. Docker Status${NC}"
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker Desktop"
    exit 1
fi
echo ""

# 2. Check containers
echo -e "${BLUE}2. Container Status${NC}"
check_container "bizy-postgres"
check_container "bizy-redis"
check_container "bizy-mailhog"
check_container "bizy-auth-server"
check_container "bizy-backend"
echo ""

# 3. Check health endpoints
echo -e "${BLUE}3. Service Health Checks${NC}"
check_service "Backend API" "http://localhost:8000/health" "healthy"
check_service "Auth Server" "http://localhost:4567/health" "ok"
echo ""

# 4. Check service endpoints
echo -e "${BLUE}4. Service Accessibility${NC}"
check_service "Swagger UI" "http://localhost:8000/api/docs" "Swagger UI"
check_service "MailHog UI" "http://localhost:8025/" "MailHog"
echo ""

# 5. Test authentication flow
echo -e "${BLUE}5. Authentication Flow${NC}"

# Try to register a test user
echo -n "User registration... "
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:4567/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"verifytest","email":"verify@test.com","password":"Test123!@#"}' || echo "FAILED")

if echo "$REGISTER_RESPONSE" | grep -q "successful\|already exists"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️  May already exist${NC}"
fi

# Verify the user
docker-compose exec -T auth-server bundle exec ruby -e "
require './app'
user = User.find_by(username: 'verifytest')
user&.update(email_verified: true) rescue nil
" > /dev/null 2>&1

# Test login
echo -n "User login... "
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:4567/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"verifytest","password":"Test123!@#"}')

if echo "$LOGIN_RESPONSE" | grep -q "token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✓${NC} (Token received)"
else
    echo -e "${RED}✗${NC}"
    echo "  Response: $LOGIN_RESPONSE"
    ((ERRORS++))
fi
echo ""

# 6. Test authenticated endpoints
if [ -n "$TOKEN" ]; then
    echo -e "${BLUE}6. Authenticated Endpoints${NC}"

    # Test task creation
    echo -n "Create task... "
    CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/tasks" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"title":"Verification test","priority":1}')

    if echo "$CREATE_RESPONSE" | grep -q "id"; then
        TASK_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":[0-9]*' | cut -d: -f2)
        echo -e "${GREEN}✓${NC} (ID: $TASK_ID)"

        # Test task list
        echo -n "List tasks... "
        LIST_RESPONSE=$(curl -s "http://localhost:8000/api/tasks" \
          -H "Authorization: Bearer $TOKEN")

        if echo "$LIST_RESPONSE" | grep -q "id"; then
            TASK_COUNT=$(echo "$LIST_RESPONSE" | grep -o '"id":' | wc -l | tr -d ' ')
            echo -e "${GREEN}✓${NC} (Found $TASK_COUNT tasks)"
        else
            echo -e "${RED}✗${NC}"
            ((ERRORS++))
        fi

        # Test task deletion
        if [ -n "$TASK_ID" ]; then
            echo -n "Delete task... "
            DELETE_RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "http://localhost:8000/api/tasks/$TASK_ID" \
              -H "Authorization: Bearer $TOKEN")

            if [ "$DELETE_RESPONSE" = "204" ]; then
                echo -e "${GREEN}✓${NC}"
            else
                echo -e "${RED}✗ (HTTP $DELETE_RESPONSE)${NC}"
                ((ERRORS++))
            fi
        fi
    else
        echo -e "${RED}✗${NC}"
        echo "  Response: $CREATE_RESPONSE"
        ((ERRORS++))
    fi
    echo ""
fi

# 7. Check volumes
echo -e "${BLUE}7. Data Volumes${NC}"
for volume in postgres_data redis_data auth_db; do
    echo -n "Volume $volume... "
    if docker volume ls | grep -q "business-agent_$volume"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠️  Not found${NC}"
    fi
done
echo ""

# 8. Check logs for errors
echo -e "${BLUE}8. Recent Log Errors${NC}"
BACKEND_ERRORS=$(docker-compose logs backend --tail=100 2>&1 | grep -i "error\|exception\|traceback" | wc -l | tr -d ' ')
AUTH_ERRORS=$(docker-compose logs auth-server --tail=100 2>&1 | grep -i "error\|exception" | wc -l | tr -d ' ')

echo -n "Backend errors... "
if [ "$BACKEND_ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✓ None${NC}"
else
    echo -e "${YELLOW}⚠️  Found $BACKEND_ERRORS${NC}"
fi

echo -n "Auth server errors... "
if [ "$AUTH_ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✓ None${NC}"
else
    echo -e "${YELLOW}⚠️  Found $AUTH_ERRORS${NC}"
fi
echo ""

# Summary
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Deployment verified.${NC}"
    echo ""
    echo "Services:"
    echo "  Backend API:  http://localhost:8000"
    echo "  Auth Server:  http://localhost:4567"
    echo "  Swagger UI:   http://localhost:8000/api/docs"
    echo "  MailHog UI:   http://localhost:8025"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Deployment verification failed with $ERRORS errors${NC}"
    echo ""
    echo "Check logs:"
    echo "  docker-compose logs backend"
    echo "  docker-compose logs auth-server"
    echo ""
    exit 1
fi
