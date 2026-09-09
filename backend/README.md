# AI Code Review Agent - Backend

Python-based backend for analyzing code and detecting issues.

## Setup

### Prerequisites
- Python 3.11+
- Ollama (for LLM inference)
- Jira instance (local or cloud)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from template:
```bash
cp .env.example .env
```

4. Update `.env` with your settings:
- Ollama host/model
- Jira credentials
- Database path

### Running

Start the server:
```bash
python app.py
```

Server will run on `http://localhost:5000`

## API Endpoints

### POST /api/analyze
Analyze code for issues
```json
{
  "file_path": "path/to/file.py",
  "code": "code content",
  "language": "python"
}
```

### GET /api/issues
Get all synced Jira issues

### POST /api/jira-sync
Sync analysis results to Jira
```json
{
  "analysis_result_id": 1,
  "create_new": true
}
```

### GET /api/health
Health check

### GET /api/status
System status (Ollama, Jira, Database)

## Project Structure

```
backend/
├── app.py                 # Flask app factory
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── api/
│   └── routes.py        # API endpoints
├── analysis/
│   ├── engine.py        # Main orchestrator
│   ├── parsers/         # Code parsers
│   ├── detectors/       # Issue detectors
│   └── llm/             # LLM integration
├── jira/
│   └── client.py        # Jira REST client
└── db/
    ├── database.py      # SQLAlchemy models
    └── cache.py         # Caching logic
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
