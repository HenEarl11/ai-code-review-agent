# Demo & Walkthrough Guide

## Quick Start (5 minutes)
1. Clone the repo and open it in VS Code.
2. Open sample files under `samples/`.
3. Run tests: `python -m pytest tests -q`.
4. Open `vscode-extension/` and run the Extension Development Host:

	 - In a terminal (run from repo root):

		 ```bash
		 cd vscode-extension
		 npm install
		 npm run compile
		 # (optional) in a separate terminal: npm run watch
		 code .
		 ```

	 - In VS Code (the `vscode-extension` window) press F5 (Run → Start Debugging) to open the Extension Development Host.

	 - If `code` is not on your PATH, open VS Code and use File → Open Folder → select `vscode-extension`, then press F5.

5. Save a sample file to trigger analysis diagnostics.

## Full Setup with Ollama (10 minutes)
1. Install Ollama from https://ollama.com.
2. Pull a model: `ollama pull mistral` (or another local model you prefer).
3. Start the Ollama service: `ollama serve` (default: `http://localhost:11434`).

Docker (recommended, isolates local Python/tooling differences)

4. Build and run the backend container (the image uses Python 3.11 as in the project Dockerfile):

	 - Build image (from repo root):

		 ```bash
		 docker build -t ai-review-backend ./backend
		 ```

	 - Run the container and point it to your host Ollama instance. On macOS use `host.docker.internal` so the container can reach your host's Ollama service:

		 ```bash
		 # default map host:5000 -> container:5000
		 docker run -d --name ai-review-backend -p 5000:5000 \
			 -e FLASK_ENV=development -e FLASK_DEBUG=True \
			 -e OLLAMA_HOST="http://host.docker.internal:11434" ai-review-backend
		 ```

	 - If port 5000 is already in use on your machine, map to an alternate host port (example uses 5001):

		 ```bash
		 docker run -d --name ai-review-backend -p 5001:5000 \
			 -e FLASK_ENV=development -e FLASK_DEBUG=True \
			 -e OLLAMA_HOST="http://host.docker.internal:11434" ai-review-backend
		 ```

	 - To use docker-compose (recommended for full stack: Ollama + Jira + backend):

		 ```bash
		 docker-compose up --build
		 ```

5. Verify the backend is running:

	 - Health (adjust host port if you used a different mapping):

		 ```bash
		 curl http://localhost:5000/api/health || curl http://localhost:5001/api/health
		 ```

6. Run a quick sample analysis (this posts the contents of a sample file to the backend). If you ran the container on 5001, update the URL accordingly.

	 - Quick test using Python (from repo root):

		 ```bash
		 # example: posts samples/python/vulnerable_api.py to the running backend
		 python3 - <<'PY'
		 import json,urllib.request
		 code = open('samples/python/vulnerable_api.py').read()
		 data = json.dumps({
			 'file_path': 'samples/python/vulnerable_api.py',
			 'code': code,
			 'language': 'python'
		 }).encode()
		 url = 'http://localhost:5000/api/analyze'
		 try:
			 req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
			 resp = urllib.request.urlopen(req, timeout=60)
			 print(resp.read().decode())
		 except Exception as e:
			 # retry against alternate host port
			 url = 'http://localhost:5001/api/analyze'
			 try:
				 req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
				 resp = urllib.request.urlopen(req, timeout=60)
				 print(resp.read().decode())
			 except Exception as e2:
				 print('ANALYZE FAILED:', e2)
		 PY
		 ```

Notes
- The backend environment variable used in the demo is `OLLAMA_HOST` (the Dockerfile and the demo use `host.docker.internal` to reach the host's `ollama serve`). Some local runs use `AICR_OLLAMA_URL` environment var; both are supported by the demo config — prefer `OLLAMA_HOST` when running the Docker container.
- If Ollama isn't running or the model isn't pulled you will see an LLM-related error in the analyze response or container logs; pull and serve the model first.

## Ollama Configuration for Different Codebase Styles
- Use multiple profiles (`strict`, `balanced`, `fast`) in the VS Code extension.
- Point to different local models by backend configuration (for example `mistral` vs code-tuned models).
- Keep pattern detectors constant and adjust LLM prompt style per repository standards.

## Testing Each Configuration
- `strict`: emphasize security and standards.
- `balanced`: default mix of security, quality, and performance.
- `fast`: lightweight checks for quick save-time feedback.

## Walkthrough: Python Django Sample
1. Open `samples/python/vulnerable_api.py`.
2. Highlight findings: hardcoded secrets, SQL injection, unsafe deserialization, bare except, N+1 query.
3. Show corresponding tests in `tests/test_python_analysis.py`.

## Walkthrough: Terraform Infrastructure Sample
1. Open `samples/terraform/main.tf` and `samples/terraform/kubernetes.yaml`.
2. Highlight public S3 bucket, unencrypted RDS, backup disabled, single replica.
3. Show corresponding tests in `tests/test_terraform_analysis.py`.

## Walkthrough: React/TypeScript Sample
1. Open `samples/typescript/React.tsx`.
2. Highlight missing typings, `useEffect` dependencies, event listener leak, XSS risk, console logs.
3. Show corresponding tests in `tests/test_typescript_analysis.py`.

## Jira Integration Walkthrough
1. Run the `AI Code Review: Sync Issues to Jira` command in VS Code.
2. Explain issue count and key generation using `tests/test_jira_sync.py` behavior.

## VS Code Extension Demo Flow
1. Run command: `AI Code Review: Analyze Current File`.
2. Save file to trigger real-time diagnostics.
3. Observe status bar issue counts.
4. Run `AI Code Review: Open Results` to show webview output.

## Performance Metrics to Present
- Save-to-diagnostic feedback: near real-time local checks.
- Test runtime: fast local pytest runs.
- LLM path: optional and local via Ollama endpoint.

## Tips for Judges
- Start with quick start path first.
- Demonstrate one issue per language quickly.
- Show local/offline readiness with Ollama.
- Emphasize extensibility: detectors + LLM profiles + Jira sync.
