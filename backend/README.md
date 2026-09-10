# AI Code Review Agent - Backend

Python-based backend for analyzing code and detecting issues.

## Setup

### Prerequisites
- Python 3.11+
- Ollama (for LLM inference)
- Jira instance (local or cloud)
# AI Code Review Agent - Backend

Python-based backend for analyzing code and detecting issues.

## Configuration templates

The backend uses configuration templates to control analysis behavior. Templates are stored in `backend/config_templates/` and can be selected at runtime using the `CODEBASE_STYLE` environment variable.

Common template names: `python`, `terraform`, `typescript`.

To inspect available templates and examples, see `backend/config_templates/README.md`.

## Setup

### Prerequisites
- Python 3.11+
- Ollama (for LLM inference) or another supported LLM runtime
- Jira instance (optional, for sync features)

### Installation

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` from the example and update values:
```bash
cp .env.example .env
```

Important values:
- `OLLAMA_HOST` / `OLLAMA_MODEL`
- `JIRA_URL`, `JIRA_USER`, `JIRA_TOKEN`
- `DATABASE_URL`

### Running

Select a configuration template and start the server:

```bash
export CODEBASE_STYLE=python
python app.py
```

The server will run on `http://localhost:5000` by default.

### Docker (recommended)

Build and run using the repo-level Dockerfile which uses Python 3.11. This avoids local Python/packaging differences.

```bash
docker build -t ai-review-backend ./backend
docker run -d --name ai-review-backend -p 5000:5000 \
  -e FLASK_ENV=development -e FLASK_DEBUG=True \
  -e OLLAMA_HOST="http://host.docker.internal:11434" ai-review-backend
```

If your host port 5000 is in use, map to another host port (for example 5001):

```bash
docker run -d --name ai-review-backend -p 5001:5000 \
  -e FLASK_ENV=development -e FLASK_DEBUG=True \
  -e OLLAMA_HOST="http://host.docker.internal:11434" ai-review-backend
```

Health and analyze examples:

```bash
curl http://localhost:5000/api/health || curl http://localhost:5001/api/health

curl -X POST http://localhost:5000/api/analyze -H "Content-Type: application/json" \
  -d '{"file_path":"example.py","code":"print(1)","language":"python"}' || \
  curl -X POST http://localhost:5001/api/analyze -H "Content-Type: application/json" \
  -d '{"file_path":"example.py","code":"print(1)","language":"python"}'
```

## API Endpoints (quick)

POST /api/analyze - Analyze a single file payload
GET /api/issues - List stored issues
POST /api/jira-sync - Sync analysis output to Jira
GET /api/health - Health check
GET /api/status - System status (LLM, Jira, DB)

Example analyze request:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"file_path":"example.py","code":"print(1)","language":"python"}'
```

## Project structure

```
backend/
├── app.py                 # Flask app factory
├── config.py              # Configuration loader
├── requirements.txt       # Dependencies
├── api/
│   └── routes.py          # API endpoints
├── analysis/
│   ├── engine.py          # Main orchestrator
│   ├── parsers/           # Code parsers
│   ├── detectors/         # Issue detectors
│   └── llm/               # LLM integration
├── jira/
│   └── client.py          # Jira REST client
└── db/
    ├── database.py        # Database models
    └── cache.py           # Caching logic
```

## Development

Run tests:
```bash
python -m pytest tests/
```

Format code:
```bash
black .
```

Lint:
```bash
flake8 .
```

## Notes

When you add a new template under `backend/config_templates/`, update the `__init__.py` in that folder to register the template with the `ConfigManager` if required.
