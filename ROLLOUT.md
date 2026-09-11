# Rolling out AI PR Review to a repository

The reviewer lives in **this** repo and is fetch## What is in this repo

| Path | Status |
|---|---|
| `scripts/pr_review_action.py` | **Live** — fetched by every consumer repo on every PR (at the tag in `AICR_VERSION`). Do not rename/move without a release. |
| `templates/github-workflows/ai-review.yml` | **Live** — the workflow consumers copy. |
| `.github/workflows/ai-review.yml` | Same workflow, so this repo reviews its own PRs. |
| `samples/` | Intentionally vulnerable demo/test fixtures for the reviewer. |
| `PANEL_BRIEF.md` | Plain-English explanation and Q&A for presenting the solution. |n-time by each consumer repo,
so there is exactly one copy to maintain. Adding a repo is a single-file change.

## What each consumer repo gets

On every `pull_request` (opened / synchronize / reopened):

1. Checks out the PR head on an `ubuntu-latest` runner.
2. Installs Ollama, restores the cached `mistral` model, starts `ollama serve`.
3. Downloads `scripts/pr_review_action.py` from this repo at the pinned tag `AICR_VERSION`.
4. For each changed `.tf` / `.py` / `.ts` / `.tsx` / `.js` / `.jsx` file:
   - fast regex rules (deterministic, with one-line fixes), then
   - an Ollama review of the whole file (large files are split into ~6 KB
     overlapping chunks so nothing is skipped), merged in.
5. Posts **one** PR review with inline comments; safe fixes appear as
   ` ```suggestion ``` ` blocks with an **Apply suggestion** button.

Suggestions only — nothing is committed or pushed. Uses the built-in `GITHUB_TOKEN`;
no PATs or secrets required.

## Add it to a repo (Terraform, Python or TypeScript — same steps)

```bash
cd /path/to/target-repo
mkdir -p .github/workflows
curl -fsSL https://raw.githubusercontent.com/HenEarl11/ai-code-review-agent/main/templates/github-workflows/ai-review.yml \
  -o .github/workflows/ai-review.yml
git add .github/workflows/ai-review.yml
git commit -m "Add AI PR review"
git push
```

Then confirm in the repo: **Settings → Actions → General → Workflow permissions** is
*Read and write* (or that `pull-requests: write` in the workflow is honoured — it is by default).

Open any PR that touches a supported file type and watch the **AI Code Review** check.
First run downloads the 4.4 GB model (~10 min); later runs use the cache.

## Repos currently using it

| Repo | Language | Since |
|---|---|---|
| [HenEarl11/terraform](https://github.com/HenEarl11/terraform) | Terraform | 2026-09-11 — see [PR #1](https://github.com/HenEarl11/terraform/pull/1) |
| [HenEarl11/python](https://github.com/HenEarl11/python) | Python | 2026-09-11 — see [PR #1](https://github.com/HenEarl11/python/pull/1) |
| [HenEarl11/typescript](https://github.com/HenEarl11/typescript) | TypeScript | 2026-09-11 — see [PR #1](https://github.com/HenEarl11/typescript/pull/1) |

## Per-repo knobs (edit `env:` in the workflow)

| Variable | Default | Effect |
|---|---|---|
| `AICR_VERSION` | `v1.0.0` | Git tag of this repo to fetch the reviewer from. Bump to upgrade; set to `main` to always track latest |
| `OLLAMA_MODEL` | `mistral` | `qwen2.5-coder:3b` is ~3× faster with shallower, fewer findings |
| `AICR_FAIL_ON_HIGH` | `"false"` | `"true"` fails the check on any high-severity finding — pair with a required status check to block merges |
| `AICR_USE_OLLAMA` | `"true"` | `"false"` = regex rules only (seconds, no model download) |
| `AICR_MAX_LLM_CHUNKS` | `6` | Max ~6 KB chunks per file sent to Ollama (caps runtime on very large files) |
| `AICR_OLLAMA_URL` | `http://localhost:11434` | Point at a self-hosted GPU runner's Ollama and drop the install/pull steps for sub-minute reviews |

## Releasing a new version

Consumer repos are pinned to a tag, so pushing to `main` does **not** change their
behaviour. To ship a change:

```bash
git tag -a v1.1.0 -m "describe the change"
git push origin v1.1.0
```

then bump `AICR_VERSION` in each consumer's `.github/workflows/ai-review.yml`.
Roll back by pointing `AICR_VERSION` at the previous tag.

## Extending the rules

Regex rules are in `DETECTORS` in `scripts/pr_review_action.py`, keyed by language.
Each is one tuple: `(id, regex, severity, message, fixer_or_None)`. Tag a release
(above) and bump `AICR_VERSION` in the consumers to pick it up.

## Testing a change locally before pushing

```bash
ollama serve &
python3 - <<'EOF'
import sys; sys.path.insert(0, 'scripts')
from pathlib import Path
import pr_review_action as r
for p in [Path('samples/terraform/demo/rds.tf'), Path('samples/python/vulnerable_api.py'), Path('samples/typescript/api.ts')]:
    for x in r.scan(p, r.EXT_TO_LANG[p.suffix], use_llm=True):
        print(f"{p.name}:{x['line']} {x['severity']} [{x['source']}] {x['id']} — {x['message'][:80]}")
EOF
```

## What in this repo is live vs. legacy

| Path | Status |
|---|---|
| `scripts/pr_review_action.py` | **Live** — fetched by every consumer repo on every PR. Do not rename/move without updating consumers. |
| `templates/github-workflows/ai-review.yml` | **Live** — the workflow consumers copy. |
| `samples/` | Demo/test fixtures for the reviewer. |
| `backend/`, `vscode-extension/`, Docker files, `scripts/local_*`, `scripts/apply_*`, `scripts/pr_review.py`, `scripts/create_pr_with_docker.sh`, `tests/` | Legacy — earlier Flask-backend and auto-fix iterations. Not used by the PR review workflow. Safe to archive. |
