# AI Code Review Agent

Automated, suggestion-only pull-request review powered by a **locally-run open-source
model** (Ollama + Mistral) with a set of fast regex rules as a safety net.

On every PR in a consumer repo it posts one review with inline comments — 🔴 high /
🟠 medium / 🟡 low — and, where a safe one-line fix exists, a GitHub `suggestion` block
the developer can apply with one click. Nothing is ever committed automatically, and
no source code leaves the GitHub Actions runner.

Supports **Terraform**, **Python** and **TypeScript/JavaScript**.

## Layout

| Path | Purpose |
|---|---|
| `scripts/pr_review_action.py` | The reviewer. Python standard library only. Fetched at run time by every consumer repo — do not rename or move without a release. |
| `templates/github-workflows/ai-review.yml` | The workflow consumers copy into `.github/workflows/`. Pinned to a release tag via `AICR_VERSION`. |
| `samples/` | Intentionally vulnerable Terraform / Python / TypeScript fixtures used for demos and for testing the reviewer. |
| `.github/workflows/ai-review.yml` | This repo reviews its own PRs with the same workflow. |
| `ROLLOUT.md` | How to add the reviewer to a repo, tune it, release a new version. |
| `PANEL_BRIEF.md` | Plain-English explanation and likely Q&A for presenting the solution. |

## Add it to a repo

```bash
mkdir -p .github/workflows
curl -fsSL https://raw.githubusercontent.com/HenEarl11/ai-code-review-agent/main/templates/github-workflows/ai-review.yml \
  -o .github/workflows/ai-review.yml
git add .github/workflows/ai-review.yml && git commit -m "Add AI PR review" && git push
```

No secrets or tokens required. See [`ROLLOUT.md`](ROLLOUT.md) for details.

## Test a change locally

```bash
ollama serve &
ollama pull mistral
python3 - <<'EOF'
import sys; sys.path.insert(0, 'scripts')
from pathlib import Path
import pr_review_action as r
for p in [Path('samples/terraform/demo/rds.tf'), Path('samples/python/vulnerable_api.py'), Path('samples/typescript/api.ts')]:
    for x in r.scan(p, r.EXT_TO_LANG[p.suffix], use_llm=True):
        print(f"{p.name}:{x['line']} {x['severity']} [{x['source']}] {x['id']} — {x['message'][:80]}")
EOF
```

## Repos using it

[terraform](https://github.com/HenEarl11/terraform) ·
[python](https://github.com/HenEarl11/python) ·
[typescript](https://github.com/HenEarl11/typescript)
