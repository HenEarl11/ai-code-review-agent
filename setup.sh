#!/bin/bash

# AI Code Review Agent - Docker Compose Setup Script
# This script helps initialize and manage the Docker Compose environment

set -e

echo "🚀 AI Code Review Agent - Local Development Setup"
echo "================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"
echo ""

# Commands
command=$1

case $command in
    "start")
        echo -e "${BLUE}Starting services...${NC}"
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✓ Services started!${NC}"
        echo ""
        echo "Service URLs:"
        echo -e "  Backend:    ${BLUE}http://localhost:5000${NC}"
        echo -e "  Jira:       ${BLUE}http://localhost:8080${NC}"
        echo -e "  Ollama:     ${BLUE}http://localhost:11434${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Wait for Jira to start (2-3 minutes)"
        echo "  2. Pull a model: docker exec ai-review-ollama ollama pull mistral"
        echo "  3. Configure Jira at http://localhost:8080"
        echo ""
        ;;
    "stop")
        echo -e "${BLUE}Stopping services...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ Services stopped${NC}"
        ;;
    "restart")
        echo -e "${BLUE}Restarting services...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ Services restarted${NC}"
        ;;
    "logs")
        service=$2
        if [ -z "$service" ]; then
            docker-compose logs -f
        else
            docker-compose logs -f $service
        fi
        ;;
    "status")
        echo -e "${BLUE}Service Status:${NC}"
        docker-compose ps
        echo ""
        echo -e "${BLUE}Health Checks:${NC}"
        echo -n "  Backend: "
        if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Healthy${NC}"
        else
            echo -e "${RED}✗ Unhealthy${NC}"
        fi
        
        echo -n "  Jira: "
        if curl -s http://localhost:8080/status > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Healthy${NC}"
        else
            echo -e "${RED}✗ Unhealthy${NC}"
        fi
        
        echo -n "  Ollama: "
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Healthy${NC}"
        else
            echo -e "${RED}✗ Unhealthy${NC}"
        fi
        ;;
    "pull-model")
        model=$2
        if [ -z "$model" ]; then
            model="mistral"
        fi
        echo -e "${BLUE}Pulling model: $model${NC}"
        docker exec ai-review-ollama ollama pull $model
        echo -e "${GREEN}✓ Model pulled successfully${NC}"
        ;;
    "clean")
        echo -e "${YELLOW}⚠️  This will delete all containers and volumes${NC}"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            echo -e "${GREEN}✓ Cleaned up${NC}"
        else
            echo "Aborted"
        fi
        ;;
    "build")
        echo -e "${BLUE}Building images...${NC}"
        docker-compose build
        echo -e "${GREEN}✓ Build complete${NC}"
        ;;
    "shell")
        service=$2
        if [ -z "$service" ]; then
            service="backend"
        fi
        echo -e "${BLUE}Connecting to $service...${NC}"
        docker-compose exec $service /bin/bash
        ;;
    "test")
        echo -e "${BLUE}Testing API endpoints...${NC}"
        echo ""
        
        echo "Testing /api/health:"
        curl -s http://localhost:5000/api/health | jq .
        echo ""
        
        echo "Testing /api/status:"
        curl -s http://localhost:5000/api/status | jq .
        echo ""
        
        echo "Testing /api/analyze with sample code:"
        curl -s -X POST http://localhost:5000/api/analyze \
          -H "Content-Type: application/json" \
          -d '{
            "file_path": "test.py",
            "code": "import os\npassword = \"secret123\"\n",
            "language": "python"
          }' | jq .
        echo ""
        ;;
    "help")
        echo "Usage: ./setup.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start           Start all services"
        echo "  stop            Stop all services"
        echo "  restart         Restart all services"
        echo "  status          Show service status and health checks"
        echo "  logs [service]  View logs (default: all services)"
        echo "  pull-model      Pull LLM model (default: mistral)"
        echo "  build           Build Docker images"
        echo "  shell [svc]     Connect to service shell (default: backend)"
        echo "  test            Test API endpoints"
        echo "  clean           Remove all containers and volumes"
        echo "  help            Show this help message"
        echo ""
        ;;
    *)
        echo "Unknown command: $command"
        echo "Run './setup.sh help' for usage information"
        exit 1
        ;;
esac
