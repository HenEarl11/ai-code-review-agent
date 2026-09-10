# ai-code-review-agent
AI-powered code review agent that detects common issues, integrates with IDEs, and syncs with Jira.

## Overview

This repository contains a backend service that analyzes code using configurable templates (Python, Terraform, TypeScript, etc.), a VS Code extension for IDE integration, sample codebases, and tests. Configuration templates live under `backend/config_templates/` and define which detectors, LLM settings, and analysis patterns the engine uses.

See `backend/config_templates/README.md` for full details on available templates and how to add new ones.

## Quickstart

1. Backend prerequisites:
	- Python 3.11+
	- Ollama or another supported LLM runtime (if using LLM features)

2. Basic steps to run the backend locally:

```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
# Optionally select a configuration template
export CODEBASE_STYLE=python
python backend/app.py
```

After starting, the backend exposes endpoints under `http://localhost:5000` (see `backend/README.md` for API details).

### Docker quickstart (recommended)

If you prefer to avoid local Python/tooling differences, use the included Dockerfile which uses Python 3.11.

- Build the backend image (from the repo root):

```bash
docker build -t ai-review-backend ./backend
```

- Run the container and point it at a local Ollama instance. On macOS use `host.docker.internal` so the container can reach your host's Ollama service:

```bash
# default mapping host:5000 -> container:5000
docker run -d --name ai-review-backend -p 5000:5000 \
	-e FLASK_ENV=development -e FLASK_DEBUG=True \
	-e OLLAMA_HOST="http://host.docker.internal:11434" ai-review-backend
```

- If port 5000 is already in use on your host, map to an alternate host port (example uses 5001):

```bash
docker run -d --name ai-review-backend -p 5001:5000 \
	-e FLASK_ENV=development -e FLASK_DEBUG=True \
	-e OLLAMA_HOST="http://host.docker.internal:11434" ai-review-backend
```

- Check health:

```bash
curl http://localhost:5000/api/health || curl http://localhost:5001/api/health
```

- Quick analyze test (posts a sample file to the running backend):

```bash
python3 - <<'PY'
import json,urllib.request
code = open('samples/python/vulnerable_api.py').read()
data = json.dumps({'file_path':'samples/python/vulnerable_api.py','code':code,'language':'python'}).encode()
for port in (5000,5001):
		url = f'http://localhost:{port}/api/analyze'
		try:
				req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
				resp = urllib.request.urlopen(req, timeout=60)
				print(resp.read().decode())
				break
		except Exception as e:
				print('ERR', port, e)
PY
```

## Configuration templates

The analysis engine behavior is controlled by templates under `backend/config_templates/`. Use the `CODEBASE_STYLE` environment variable to select a template at runtime (for example, `python`, `terraform`, or `typescript`).

To learn more about available templates, file patterns, and examples, open:

```
backend/config_templates/README.md
```

## Development

- Run unit and integration tests: `python -m pytest tests/`
- Format: `black .`
- Lint: `flake8 .`

For backend-specific instructions and API endpoints, see `backend/README.md`.
# ai-code-review-agent
AI-powered code review agent that detects common issues, integrates with IDEs, and syncs with Jira
