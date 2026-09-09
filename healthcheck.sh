#!/bin/bash

# Quick health check script
# Run: ./healthcheck.sh

echo "🏥 Health Check - AI Code Review Agent"
echo "======================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_service() {
    local name=$1
    local url=$2
    local expected_code=$3
    
    echo -n "Checking $name... "
    
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓ OK (HTTP $http_code)${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED (HTTP $http_code, expected $expected_code)${NC}"
        return 1
    fi
}

echo -e "${BLUE}Backend Services:${NC}"
check_service "Backend API" "http://localhost:5000/api/health" "200"
check_service "Backend Status" "http://localhost:5000/api/status" "200"

echo ""
echo -e "${BLUE}LLM Service:${NC}"
check_service "Ollama Tags" "http://localhost:11434/api/tags" "200"

echo ""
echo -e "${BLUE}Jira Service:${NC}"
check_service "Jira Status" "http://localhost:8080/status" "200"

echo ""
echo -e "${BLUE}Docker Containers:${NC}"
echo "Active containers:"
docker ps --filter "network=ai-review-network" --format "table {{.Names}}\t{{.Status}}"

echo ""
echo -e "${BLUE}Disk Usage:${NC}"
docker system df

echo ""
echo "✅ Health check complete!"
