#!/bin/bash
# Quick script to test the API endpoints

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="${1:-http://localhost:8000}"

echo -e "${BLUE}🧪 Testing Bizy AI Backend API${NC}"
echo "================================"
echo "API URL: $API_URL"
echo ""

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
echo "GET $API_URL/health"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_URL/health")
http_code=$(echo "$response" | grep HTTP_STATUS | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_STATUS/d')

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✅ Status: $http_code${NC}"
    echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 2: Root Endpoint
echo -e "${BLUE}Test 2: Root Endpoint${NC}"
echo "GET $API_URL/"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_URL/")
http_code=$(echo "$response" | grep HTTP_STATUS | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_STATUS/d')

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✅ Status: $http_code${NC}"
    echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 3: OpenAPI Docs
echo -e "${BLUE}Test 3: OpenAPI Schema${NC}"
echo "GET $API_URL/api/openapi.json"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_URL/api/openapi.json")
http_code=$(echo "$response" | grep HTTP_STATUS | cut -d: -f2)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✅ Status: $http_code${NC}"
    echo "Schema available ✓"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
fi
echo ""

# Summary
echo "================================"
echo -e "${GREEN}🎉 API Testing Complete${NC}"
echo ""
echo "View interactive docs at:"
echo "  📚 Swagger UI: $API_URL/api/docs"
echo "  📖 ReDoc: $API_URL/api/redoc"
echo ""
