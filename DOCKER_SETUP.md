# AI Code Review Agent - Docker Compose Setup

## Quick Start

### Prerequisites
- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- 4GB+ RAM available
- ~10GB disk space

### Start Services

```bash
# Make setup script executable
chmod +x setup.sh

# Start all services
./setup.sh start
```

This will start three services:
- **Backend API** - http://localhost:5000
- **Jira** - http://localhost:8080
- **Ollama** - http://localhost:11434

### Initialize Services

1. **Wait for services to fully start** (2-3 minutes for Jira)
```bash
./setup.sh status
```

2. **Pull LLM model for analysis**
```bash
./setup.sh pull-model mistral
# Or use another model: llama2, neural-chat, codellama, etc.
```

3. **Configure Jira**
   - Open http://localhost:8080
   - Follow the setup wizard (takes 1-2 minutes)
   - Create a project key `AICR` (AI Code Review)
   - Note the API token for `.env` configuration

### Test the Setup

```bash
# Test API endpoints
./setup.sh test
```

## Available Commands

```bash
./setup.sh start              # Start all services
./setup.sh stop               # Stop all services
./setup.sh restart            # Restart all services
./setup.sh status             # Show status and health checks
./setup.sh logs               # View all logs
./setup.sh logs backend       # View backend logs
./setup.sh logs jira          # View Jira logs
./setup.sh logs ollama        # View Ollama logs
./setup.sh pull-model [name]  # Pull LLM model
./setup.sh build              # Rebuild images
./setup.sh shell [service]    # Connect to service shell
./setup.sh test               # Test API endpoints
./setup.sh clean              # Remove all containers and volumes
./setup.sh help               # Show help
```

## Service Details

### Backend API (Port 5000)

Flask application running the analysis engine.

**Key Endpoints:**
- `GET /api/health` - Health check
- `GET /api/status` - System status (Ollama, Jira, DB)
- `POST /api/analyze` - Analyze code
- `GET /api/issues` - List synced issues
- `POST /api/jira-sync` - Sync to Jira

**Example Analysis Request:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "example.py",
    "code": "import os\npassword = \"secret123\"",
    "language": "python"
  }'
```

### Ollama (Port 11434)

Local LLM inference server for AI-powered code analysis.

**Available Models:**
- `mistral` - Fast, efficient (recommended for hackathon)
- `neural-chat` - Good for conversations
- `codellama` - Specialized for code analysis
- `llama2` - General purpose

**Pull a model:**
```bash
./setup.sh pull-model mistral
```

**Ollama API:**
- `GET /api/tags` - List available models
- `POST /api/generate` - Generate text with model

### Jira (Port 8080)

Atlassian Jira Software for issue tracking and management.

**Initial Setup:**
1. Navigate to http://localhost:8080
2. Complete setup wizard
3. Create project with key `AICR`
4. Create API token in personal settings

**Using H2 Database (default):**
- Data is stored in `jira-data` volume
- No external database needed
- Suitable for development/testing

**Switch to PostgreSQL (optional):**
Uncomment PostgreSQL service in `docker-compose.yml` and update Jira environment variables.

## Environment Variables

**Backend Configuration** (`.env` in backend directory):
```
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000

OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=mistral

JIRA_HOST=http://jira:8080
JIRA_USERNAME=admin
JIRA_API_TOKEN=your_token_here
JIRA_PROJECT_KEY=AICR

DATABASE_URL=sqlite:///./db/ai_review.db
MAX_FILE_SIZE=1000000
ANALYSIS_TIMEOUT=30
CACHE_ENABLED=True
```

## Troubleshooting

### Jira won't start
```bash
# Check logs
./setup.sh logs jira

# Jira needs 60+ seconds to start, check status after waiting
./setup.sh status
```

### Backend can't reach Ollama
```bash
# Ensure Ollama is running
./setup.sh status

# Check backend logs
./setup.sh logs backend

# Verify network connectivity
docker network inspect ai-review-network
```

### Out of disk space
```bash
# Ollama models can be large, check available space
df -h

# Remove unused Docker resources
docker system prune -a
```

### Port already in use
If ports 5000, 8080, or 11434 are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Change 5000 to 5001, etc.
```

## Performance Tuning

### Increase Ollama Performance
```bash
# Edit docker-compose.yml and increase OLLAMA_NUM_THREAD
environment:
  - OLLAMA_NUM_THREAD=8  # Adjust based on CPU cores
```

### Increase Jira Memory
```bash
# Edit docker-compose.yml
environment:
  - JVM_MAXIMUM_MEMORY=2048m  # Increase from 1024m
```

### Backend Database
By default uses SQLite for simplicity. For production, switch to PostgreSQL:
1. Uncomment PostgreSQL service in `docker-compose.yml`
2. Update `DATABASE_URL` to point to PostgreSQL

## Persistence

Data is persisted in Docker volumes:
- `ollama-data` - LLM models cache
- `jira-data` - Jira database and configuration
- `db` - Backend SQLite database

**Backup volumes:**
```bash
docker run --rm -v ai-review-agent_jira-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/jira-backup.tar.gz -C /data .
```

## Stopping Services

```bash
# Stop without removing containers/volumes
./setup.sh stop

# Stop and remove everything (loses data)
./setup.sh clean
```

## Network

Services communicate via internal Docker network `ai-review-network`:
- Backend → Ollama: `http://ollama:11434`
- Backend → Jira: `http://jira:8080`
- Host → Backend: `http://localhost:5000`
- Host → Jira: `http://localhost:8080`
- Host → Ollama: `http://localhost:11434`

## Next Steps

1. ✅ Start services: `./setup.sh start`
2. ⏳ Wait for Jira to initialize
3. 📦 Pull LLM model: `./setup.sh pull-model mistral`
4. ⚙️ Configure Jira at http://localhost:8080
5. 🧪 Test API: `./setup.sh test`
6. 🚀 Build VS Code extension
7. 📝 Create sample code with issues

## Getting Help

```bash
./setup.sh help
```

For detailed logs:
```bash
./setup.sh logs backend
./setup.sh logs jira
./setup.sh logs ollama
```
