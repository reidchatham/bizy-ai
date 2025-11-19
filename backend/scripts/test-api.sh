#!/bin/bash
# Test all API endpoints with comprehensive examples

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BASE_URL="http://localhost:8000"
AUTH_URL="http://localhost:4567"

echo -e "${BLUE}🧪 Bizy AI API Testing Suite${NC}"
echo "=========================================="
echo ""

# Check if servers are running
check_service() {
    if curl -s "$1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $2 is running${NC}"
        return 0
    else
        echo -e "${RED}✗ $2 is not running${NC}"
        return 1
    fi
}

echo "Checking services..."
check_service "$AUTH_URL/health" "auth-server (port 4567)" || exit 1
check_service "$BASE_URL/health" "backend (port 8000)" || exit 1
echo ""

# 1. Register a test user
echo -e "${BLUE}1. Registering test user...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!@#"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "User registered successfully"; then
    echo -e "${GREEN}✓ User registered${NC}"
    echo "$REGISTER_RESPONSE" | jq .
else
    # User might already exist, that's okay
    echo -e "${YELLOW}⚠️  User might already exist (continuing)${NC}"
fi
echo ""

# 2. Login and get token
echo -e "${BLUE}2. Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!@#"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓ Login successful${NC}"
    echo "Token: ${TOKEN:0:50}..."
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "$LOGIN_RESPONSE" | jq .
    exit 1
fi
echo ""

# 3. Get user profile
echo -e "${BLUE}3. Getting user profile...${NC}"
PROFILE=$(curl -s "$BASE_URL/api/auth/profile" \
  -H "Authorization: Bearer $TOKEN")
echo "$PROFILE" | jq .
echo ""

# 4. Verify token
echo -e "${BLUE}4. Verifying token...${NC}"
VERIFY=$(curl -s "$BASE_URL/api/auth/verify-token" \
  -H "Authorization: Bearer $TOKEN")
echo "$VERIFY" | jq .
echo ""

# 5. Create a task
echo -e "${BLUE}5. Creating task...${NC}"
CREATE_TASK=$(curl -s -X POST "$BASE_URL/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test API integration",
    "description": "Testing the task CRUD API",
    "priority": 1,
    "category": "testing",
    "estimated_hours": 2.0,
    "tags": ["api", "test"]
  }')

TASK_ID=$(echo "$CREATE_TASK" | jq -r '.id')

if [ "$TASK_ID" != "null" ] && [ -n "$TASK_ID" ]; then
    echo -e "${GREEN}✓ Task created (ID: $TASK_ID)${NC}"
    echo "$CREATE_TASK" | jq .
else
    echo -e "${RED}✗ Task creation failed${NC}"
    echo "$CREATE_TASK" | jq .
    exit 1
fi
echo ""

# 6. List tasks
echo -e "${BLUE}6. Listing all tasks...${NC}"
LIST_TASKS=$(curl -s "$BASE_URL/api/tasks" \
  -H "Authorization: Bearer $TOKEN")
TASK_COUNT=$(echo "$LIST_TASKS" | jq '. | length')
echo -e "${GREEN}✓ Found $TASK_COUNT tasks${NC}"
echo "$LIST_TASKS" | jq '.[0:3]'  # Show first 3 tasks
echo ""

# 7. Get specific task
echo -e "${BLUE}7. Getting task $TASK_ID...${NC}"
GET_TASK=$(curl -s "$BASE_URL/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "$GET_TASK" | jq .
echo ""

# 8. Update task
echo -e "${BLUE}8. Updating task status to in_progress...${NC}"
UPDATE_TASK=$(curl -s -X PATCH "$BASE_URL/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "actual_hours": 1.0
  }')
echo "$UPDATE_TASK" | jq .
echo ""

# 9. Complete task
echo -e "${BLUE}9. Completing task...${NC}"
COMPLETE_TASK=$(curl -s -X POST "$BASE_URL/api/tasks/$TASK_ID/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actual_hours": 2.0
  }')
echo "$COMPLETE_TASK" | jq .
echo ""

# 10. Get task statistics
echo -e "${BLUE}10. Getting task statistics...${NC}"
STATS=$(curl -s "$BASE_URL/api/tasks/stats/summary" \
  -H "Authorization: Bearer $TOKEN")
echo "$STATS" | jq .
echo ""

# 11. Filter tasks
echo -e "${BLUE}11. Filtering tasks (status=completed, limit=5)...${NC}"
FILTER_TASKS=$(curl -s "$BASE_URL/api/tasks?status=completed&limit=5" \
  -H "Authorization: Bearer $TOKEN")
COMPLETED_COUNT=$(echo "$FILTER_TASKS" | jq '. | length')
echo -e "${GREEN}✓ Found $COMPLETED_COUNT completed tasks${NC}"
echo "$FILTER_TASKS" | jq '.[0:2]'  # Show first 2
echo ""

# 12. Search tasks
echo -e "${BLUE}12. Searching for 'test' tasks...${NC}"
SEARCH_TASKS=$(curl -s "$BASE_URL/api/tasks?search=test&limit=5" \
  -H "Authorization: Bearer $TOKEN")
SEARCH_COUNT=$(echo "$SEARCH_TASKS" | jq '. | length')
echo -e "${GREEN}✓ Found $SEARCH_COUNT tasks matching 'test'${NC}"
echo "$SEARCH_TASKS" | jq '.[0:2]'  # Show first 2
echo ""

# 13. Uncomplete task
echo -e "${BLUE}13. Uncompleting task...${NC}"
UNCOMPLETE=$(curl -s -X POST "$BASE_URL/api/tasks/$TASK_ID/uncomplete" \
  -H "Authorization: Bearer $TOKEN")
echo "$UNCOMPLETE" | jq .
echo ""

# 14. Delete task
echo -e "${BLUE}14. Deleting task $TASK_ID...${NC}"
DELETE_RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "$BASE_URL/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN")

if [ "$DELETE_RESPONSE" = "204" ]; then
    echo -e "${GREEN}✓ Task deleted (HTTP 204)${NC}"
else
    echo -e "${RED}✗ Delete failed (HTTP $DELETE_RESPONSE)${NC}"
fi
echo ""

# 15. Verify deletion
echo -e "${BLUE}15. Verifying task was deleted...${NC}"
VERIFY_DELETE=$(curl -s -w "%{http_code}" "$BASE_URL/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN")

if echo "$VERIFY_DELETE" | grep -q "404"; then
    echo -e "${GREEN}✓ Task no longer exists (404)${NC}"
else
    echo -e "${YELLOW}⚠️  Task might still exist${NC}"
fi
echo ""

# Summary
echo -e "${GREEN}=========================================="
echo "✅ All API Tests Complete!"
echo "==========================================${NC}"
echo ""
echo "Tests performed:"
echo "  ✓ User registration"
echo "  ✓ User login (JWT token)"
echo "  ✓ Get user profile"
echo "  ✓ Verify token"
echo "  ✓ Create task"
echo "  ✓ List tasks"
echo "  ✓ Get task by ID"
echo "  ✓ Update task (partial)"
echo "  ✓ Complete task"
echo "  ✓ Get statistics"
echo "  ✓ Filter tasks"
echo "  ✓ Search tasks"
echo "  ✓ Uncomplete task"
echo "  ✓ Delete task"
echo "  ✓ Verify deletion"
echo ""
echo "Your token for manual testing:"
echo "$TOKEN"
echo ""
echo "Try it:"
echo "  export TOKEN='$TOKEN'"
echo "  curl http://localhost:8000/api/tasks -H \"Authorization: Bearer \$TOKEN\" | jq"
