# Terraform AI Review Demo

A small, realistic "web app on AWS" stack with **deliberate misconfigurations** for
demonstrating the AI PR reviewer. Do **not** apply this in a real account.

| File | What it defines | Planted issues |
|---|---|---|
| `main.tf` | provider, variables | clean (baseline) |
| `s3.tf` | assets + logs buckets | 🔴 public-read ACL · 🟠 versioning suspended · 🟡 no lifecycle on logs |
| `rds.tf` | Postgres instance | 🔴 hardcoded password · 🔴 unencrypted · 🔴 publicly accessible · 🟠 no backups · 🟠 skip final snapshot · 🟡 single-AZ · 🟡 no deletion protection |
| `network.tf` | VPC, subnets, SGs | 🔴 SSH open to 0.0.0.0/0 · 🔴 Postgres open to 0.0.0.0/0 |
| `ecs.tf` | Fargate service + IAM | 🔴 IAM `Action:*` / `Resource:*` · 🔴 DB password + payments API key in env vars · 🟠 public IP on task · 🟡 `:latest` image tag · 🟡 debug logging |

Expected: ~25 findings (≈13 high / 8 medium / 4 low). Regex rules catch the well-known
RDS/S3/SG misconfigs with one-click `suggestion` fixes; Ollama adds the contextual ones
(over-broad IAM, secrets in env vars, missing lifecycle/deletion protection).

## Demo script (5 min)

1. In your target repo (e.g. `HenEarl11/terraform`) make sure
   `.github/workflows/ai-review.yml` is installed (see `templates/github-workflows/`).
2. Create a branch and copy these files in:
   ```bash
   git checkout -b demo/webapp-stack
   mkdir -p infra && cp path/to/ai-code-review-agent/samples/terraform/demo/*.tf infra/
   git add infra && git commit -m "Add web app infrastructure" && git push -u origin demo/webapp-stack
   gh pr create --fill
   ```
3. Watch the **AI Code Review** check run (~3–5 min first time while the model downloads; faster after caching).
4. Open the PR **Files changed** tab:
   - 🔴/🟠/🟡 inline comments on the offending lines
   - `🧠 ollama` tag on findings that came from the model
   - **Apply suggestion** buttons on lines with a safe one-line fix (`storage_encrypted = true`, `acl = "private"` …)
5. Click a few **Apply suggestion** → **Commit suggestion**. Push triggers a re-review; those findings disappear.

## Run locally without a PR

```bash
ollama serve &
AICR_OLLAMA_MODEL=mistral python3 - <<'EOF'
import sys; sys.path.insert(0,'scripts')
from pathlib import Path
import pr_review_action as r
for f in sorted(Path('samples/terraform/demo').glob('*.tf')):
    for x in r.scan(f, 'terraform', use_llm=True):
        print(f"{f.name}:{x['line']} {x['severity']} [{x['source']}] {x['id']} — {x['message'][:80]}")
EOF
```
