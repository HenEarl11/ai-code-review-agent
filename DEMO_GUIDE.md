# Demo & Walkthrough Guide

## Quick Start (5 minutes)
1. Clone the repo and open it in VS Code.
2. Open sample files under `samples/`.
3. Run tests: `python -m pytest tests -q`.
4. Open `vscode-extension/` and run extension host.
5. Save a sample file to trigger analysis diagnostics.

## Full Setup with Ollama (10 minutes)
1. Install Ollama from https://ollama.com.
2. Pull a model: `ollama pull mistral`.
3. Start service: `ollama serve` (default `http://localhost:11434`).
4. Configure backend to use `AICR_OLLAMA_URL=http://localhost:11434`.
5. Re-run the analysis flow and verify LLM-assisted summaries.

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
