# DPF Hackathon — Final Presentation Pack

**Project:** AI Code Review Agent — private, suggestion-only AI peer review on every pull request
**Format:** 10 min presentation · 5 min demo · 5 min questions

---

## Part 1 — Presentation (10 minutes, 8 slides)

Timings are a guide; ~75 seconds a slide.

### Slide 1 — Title (0:30)
> **AI Code Review Agent**
> Every pull request gets an expert security review in minutes — with the code never leaving our GitHub.

One line on who you are; then straight in.

### Slide 2 — The problem → DPF use case (1:30)
*Judging: Problem Understanding & Relevance (15%)*

Quote the brief (DPF Hackathon use case #3, *AI Code Review Agent*):

> "Developers often wait for code reviews, while reviewers spend significant time identifying common issues such as **coding standard violations, potential bugs, performance concerns, missing tests and security risks**. Many review comments are repetitive and could be detected automatically before a pull request reaches human reviewers. This slows delivery and reduces the time reviewers can spend on higher-value discussions such as architecture and design decisions."

Two costs: **developers wait**, and **reviewers burn time on the repetitive 80%**.

Then map the five issue classes to what the agent does today:

| Brief says | Agent does | Evidence |
|---|---|---|
| Security risks | Rules + LLM: secrets, open SGs, unencrypted storage, SQLi, `eval`, `pickle`, XSS | 11 high findings on terraform PR #1 |
| Potential bugs | LLM pass: logic/reliability issues no rule anticipates | `🧠 ollama` findings on all three PRs |
| Performance concerns | LLM pass: N+1 loops, repeated queries | `app/reports.py` findings |
| Coding standard violations | Rules: bare `except`, `console.log`, `:latest` tags, single-AZ… | low/medium findings with one-click fixes |
| Missing tests | **Not yet** — on the roadmap (PR-level "new module without a test file" check) | Slide 8 |

**Why we chose PR-time, not the IDE:** the brief's cost is borne at the pull request — that is where developers wait and reviewers spend time. A PR check covers *every* developer and *every* editor with one file per repo, needs no plugin install, and produces a record on the PR that humans and auditors can see. The findings still surface in the IDE for free via the GitHub Pull Requests extension in VS Code. Jira is a natural next step (raise a ticket for unresolved high findings), not a prerequisite for the value.

### Slide 3 — What we built (1:00)
- A GitHub Actions workflow that runs on every PR.
- Two-pass review: **fast deterministic rules** + a **locally-run open-source LLM (Mistral 7B via Ollama)**.
- Posts **one PR review** with inline comments graded 🔴🟠🟡 and GitHub-native **suggestion blocks** → *Commit suggestion* button.
- **Suggestions only.** Nothing is ever committed by the bot.
- Live today on three repos: Terraform, Python, TypeScript.

### Slide 4 — Design & architecture (2:00)
*Judging: Innovation & Design (20%)*

```
Developer opens / updates PR
        │
        ▼
GitHub Actions runner (ephemeral ubuntu VM)
  ├─ actions/checkout   → PR head
  ├─ Ollama + Mistral   → model cached between runs (4.4 GB, pulled once)
  ├─ curl reviewer      → scripts/pr_review_action.py @ pinned tag  (central repo)
  └─ python3 reviewer
        ├─ GitHub API: which files/lines changed?  (scope = changed lines only)
        ├─ Pass 1: regex rules  (instant, deterministic, known fixes)
        ├─ Pass 2: Ollama       (only the chunks that contain changed lines)
        └─ GitHub API: post ONE review + inline ```suggestion``` comments
        │
        ▼
Developer clicks "Commit suggestion"  → GitHub commits it as the developer
        │
        ▼
Push triggers re-review, scoped to only what changed since last time
```

Design decisions to call out (each is a deliberate, defensible choice):

| Decision | Why |
|---|---|
| **Local open-weights model, not a cloud API** | Zero data egress; zero per-token cost; no vendor retention policy to review. |
| **Rules + LLM, not LLM alone** | Rules give a guaranteed floor (a hard-coded secret is *always* caught) and precise fixes; LLM finds what nobody wrote a rule for. |
| **Suggestions only** | Human stays the committer. We also guard the LLM from "fixing" a secret by inventing a new one. |
| **Changed-lines-only, incremental on re-push** | No nagging about things the author chose to ignore; re-runs take a fraction of the time. |
| **One central script, consumers pin a release tag** | Three repos, one copy of the logic; upgrades are a one-line bump; rollback is the same line. |
| **Stdlib-only Python, built-in `GITHUB_TOKEN`** | Nothing to install, no secrets to rotate, minimal permissions (`pull-requests: write`). |
| **Provider-agnostic core** | GitHub-specific calls are isolated; same core would drive CodeCommit / GitLab adapters. |

### Slide 5 — Benefits (1:00)
*Judging: Impact & Practicality (15%)*

- **Security:** every PR reviewed for the OWASP/CIS classics before a human even looks.
- **Speed:** review lands in ~2–10 min; fixes applied in one click.
- **Consistency:** the same standard on every repo, every language.
- **Confidentiality:** no code leaves GitHub; auditable, deterministic floor.
- **Cost:** no licences, no model API fees (next slide).
- **Adoption cost:** one 80-line file per repo, no secrets, five minutes.

### Slide 6 — Results so far (1:00)
*Judging: Technical Execution — set up the demo*

| Repo | Files | Findings | From LLM | First run | Incremental re-run |
|---|---|---|---|---|---|
| terraform (web-app stack) | 5 | 21 (11 high) | 13 | ~10 min | — |
| python (orders API) | 2 | 10 | 9 | 8m 49s | **1 finding, 1 file, ~2 min** |
| typescript (dashboard) | 2 | 9 | 7 | 4m 37s | — |

Examples caught: public S3 ACL, RDS unencrypted + publicly accessible, SSH open to 0.0.0.0/0, hard-coded API keys, SQL built by string formatting, `pickle.loads` on untrusted data, `eval()`, `dangerouslySetInnerHTML`, N+1 query loop.

### Slide 7 — Operating costs (1:00)

| Item | Cost |
|---|---|
| Model (Mistral 7B, Apache-2.0) | **£0** |
| Model API calls | **£0** — runs on the runner |
| GitHub Actions minutes (public repos) | **£0** |
| GitHub Actions minutes (private repos) | 2,000 min/month included; then ~$0.008/min Linux. At ~8 min/PR → **≈ $0.06 per PR**; 100 PRs/month ≈ 800 min → **within the free allowance** |
| Model cache | 4.4 GB of the 10 GB free Actions cache |
| Optional: self-hosted GPU runner (g4dn.xlarge) | ≈ $0.53/hr on-demand → sub-minute reviews; only worth it above ~500 PRs/month |
| Maintenance | One Python file, stdlib only; rules are one line each |

Compare: commercial AI review is typically **$15–30 per developer per month** plus data leaving the estate.

### Slide 8 — Next steps (1:00)

**Near term (weeks)**
- **Missing-tests check** — the one brief item not yet covered: flag a PR that adds/changes a source module without touching a corresponding test file.
- **Jira integration** — the brief's suggested MCP: on merge (or on request), raise a ticket per unresolved high-severity finding, linked to the PR line. Uses Jira REST/MCP; ~50 lines.
- **IDE surface** — findings already appear in VS Code via the GitHub Pull Requests extension; optional: a thin extension that runs the same rules pre-commit.
- Run advisory-only across more DPF repos for a month; measure which findings developers accept → tune rules, prune false positives.
- Add `# aicr:ignore <rule>` inline suppression with justification (auditable risk acceptance).
- Self-hosted GPU runner for sub-minute reviews.

**Medium term**
- Split into `core` + provider adapters → **AWS CodeCommit** (EventBridge → CodeBuild → `PostCommentForPullRequest`), GitLab, Bitbucket.
- Larger models (13B–70B) on GPU; per-team rule packs; org-wide dashboard of finding trends.
- Flip `AICR_FAIL_ON_HIGH` on for production repos once trust is established.

**Close:** *"One file per repo, zero data egress, zero licence cost — and a developer can accept a security fix with one click. It's live on three repos today."*

---

## Part 2 — Demo script (5 minutes)

Have these tabs open **before** you start; do not rely on live model runs (they take minutes).

| Time | Tab | Do | Say |
|---|---|---|---|
| 0:00 | Consumer repo `.github/workflows/ai-review.yml` | Scroll it once | "This is the entire footprint in a consumer repo — one file, no secrets." |
| 0:45 | `HenEarl11/terraform` PR #1 → **Files changed** | Show the inline comments in `rds.tf` | "Rule findings in red/orange/yellow, each explains the risk and offers a fix." |
| 1:30 | Same PR, `ecs.tf` comment tagged `🧠 ollama` | Point at the tag | "This one no rule knew about — the model found it. We label them so you always know the source." |
| 2:15 | Same PR, `rds.tf:16` `storage_encrypted` suggestion | **Click "Commit suggestion"** (or show the one already committed) | "One click. GitHub commits it *as me* — the bot never writes code." |
| 3:00 | Actions tab → the run triggered by that commit | Open the log, find `Review scope: lines changed since …` and `Skipping … (no changed lines in scope)` | "The re-review only looks at what changed — so it's fast and it doesn't nag about things I've chosen to leave." |
| 3:45 | Any run log | Find `[ollama] app/orders.py: 7 raw item(s) -> 7 valid finding(s)` | "Proof the model is doing real work — and that we validate everything it returns before it reaches a developer." |
| 4:15 | `PANEL_BRIEF.md` or `ROLLOUT.md` | Show the knobs table | "Model, scope, fail-on-high, version — all one-line settings per repo." |
| 4:45 | — | Stop. | Hand over for questions. |

**Fallbacks:** if GitHub is slow, every screen above exists as a static PR page. If asked to run it live, push a one-line change to the python demo branch at the *start* of the presentation so it's finished by the demo.

**Judging criterion "document ingestion and Q&A smooth"** maps here to: PR ingestion → review comments. Show that the run starts within seconds of the push and the comments land on the correct lines.

---

## Part 3 — Questions (5 minutes) — likely questions and short answers

**The brief suggested an IDE agent and Jira MCP — why didn't you build that?** The brief's *problem* is time lost at the pull request — developers waiting, reviewers repeating themselves. We put the agent where that cost is. One file per repo covers every developer and every editor with nothing to install, and leaves an auditable record on the PR. An IDE plugin only helps the developers who install it and leaves no trace. Findings do appear in VS Code today via the GitHub PR extension; Jira ticketing is a ~50-line next step we've scoped, not a prerequisite for the value.

**You don't detect missing tests.** Correct — it's the one of the brief's five classes we haven't covered yet. It's a PR-level check (source module changed, no matching test file touched), scoped for the next release.

**Is our code sent to OpenAI / Anthropic / anyone?** No. The model runs on the ephemeral GitHub runner; the only outbound calls are to GitHub's own API (to post comments) and to Ollama's registry (to *download* the model, once).

**How accurate is it?** Found every seeded issue on the demo repos plus several unplanned ones. The rules pass is 100% deterministic. The LLM pass will have false positives — which is why it's advisory by default and why the next step is a month of measurement.

**What stops it making things worse?** It cannot write code. Every fix is a GitHub suggestion the developer must click; the commit is authored by the developer. We also block the LLM from proposing replacement secret values.

**Why Mistral 7B?** Tested against `qwen2.5-coder:3b`: 3× faster but found roughly half the issues and misdiagnosed one. Model is a one-line setting; GPU runners open up 13B–70B.

**Why not GitHub Copilot code review?** Same shape of feature, but Copilot sends code to Microsoft/OpenAI's cloud and is a paid add-on. Ours: in-house, zero marginal cost, and we control exactly what it checks.

**What if the model is down or slow?** Rules still run and post; you get a reduced review, not a failed check. Per-file 10-min ceiling, 45-min job ceiling.

**Can it block merges?** Yes — `AICR_FAIL_ON_HIGH: "true"` plus the `review` check is already required by branch protection on all repos.

**Does it nag about things we've decided to ignore?** No — it only reviews lines changed since the last review. Ignoring is explicit: branch protection requires every conversation to be resolved, so the decision is recorded on the PR.

**Could this run on AWS CodeCommit?** Yes — the core is provider-agnostic; the GitHub-specific parts are ~5 API calls. CodeCommit equivalents: EventBridge trigger → CodeBuild job → `PostCommentForPullRequest`. The one gap is CodeCommit has no "apply suggestion" button. (Note: AWS closed CodeCommit to new customers in 2024.)

**What did it cost to build?** One ~450-line Python file, one workflow file, no infrastructure. Built and rolled out to three repos in a single day.

**How do we add a repo / a language / a rule?** Repo: copy one file. Language: one dictionary entry + file extensions. Rule: one line `(id, regex, severity, message, fixer)`.

---

## Part 4 — Judging criteria → where we score

| Criterion | Weight | Where it's evidenced |
|---|---|---|
| Problem Understanding & Relevance | 15 | Slide 2: named DPF use case; solution maps 1:1 to "review on every PR, code stays in-house". |
| Innovation & Design | 20 | Slide 4: rules+LLM hybrid, changed-lines incremental scoping, local model, pinned central script, provider-agnostic core. Modularity: adding repo/language/rule are each one-line changes. |
| Technical Execution | 35 | Live PRs with real findings; working *Commit suggestion*; run logs showing model output validated; incremental re-run proven (1 finding vs 10). Nothing faked — every finding is traceable to a rule or a logged model response. |
| Presentation & Clarity | 15 | 8 slides, one message each; story = "expert review, in minutes, without the code leaving the building". |
| Impact & Practicality | 15 | Already live on 3 repos; £0 licence cost; 5-minute onboarding; roadmap to CodeCommit/GitLab. |

---

## Appendix A — Component fact sheet

### A1. `scripts/pr_review_action.py` — the reviewer
- **What:** single-file Python 3 program, **standard library only** (`json`, `re`, `subprocess`, `urllib`, `pathlib`). ~450 lines. Lives in `HenEarl11/ai-code-review-agent`; consumers download it at run time from a **pinned git tag**.
- **Inputs:** PR number (argv); env vars `GITHUB_REPOSITORY`, `GH_TOKEN`, `AICR_*`.
- **Sections:**
  - **`DETECTORS`** — dictionary keyed by language (`terraform` 11 rules, `python` 5, `typescript` 4). Each rule is a tuple `(id, compiled regex, severity, message, fixer|None)`. A fixer is a tiny function that returns the corrected line (e.g. `_tf_set("storage_encrypted", "true")`).
  - **`EXT_TO_LANG` / `IGNORE_DIRS`** — which file extensions map to which rule set; vendored/build dirs skipped.
  - **GitHub helpers** — `gh_api()` shells out to the `gh` CLI (pre-installed on runners, authenticates with `GH_TOKEN`); `get_pr_files()` paginates `/pulls/{n}/files`; `incremental_added_lines()` calls `/compare/{before}...{head}`.
  - **Diff parsing** — `_patch_lines()` walks unified-diff hunks to compute (a) lines *added* (review targets) and (b) lines *present in the diff* (where GitHub allows inline comments).
  - **Ollama pass** — `_chunk_lines()` splits files into ≤6 KB windows with 8-line overlap; `_llm_prompt()` numbers every line and asks for strict JSON `{"findings":[{line, severity, id, message, replacement}]}`; `_llm_scan_chunk()` POSTs to `/api/generate` with `format:json`, `temperature 0.1`; parser accepts array / wrapped object / single object; **validation**: line must be inside the chunk, severity normalised, `_looks_like_code()` rejects prose masquerading as a fix, `_safe_replacement()` refuses to suggest a new secret literal.
  - **`scan()`** — runs rules on target lines, then Ollama on chunks containing target lines; rule wins if both hit the same line.
  - **`build_comment()`** — renders 🔴/🟠/🟡, severity, rule id, `🧠 ollama` tag, message, and a ` ```suggestion ` block when a replacement exists.
  - **`main()`** — determines scope (`full` / all-added / incremental), loops files, posts **one** review via `POST /pulls/{n}/reviews` (falls back to a plain issue comment if GitHub rejects a position), optional non-zero exit on high findings.
- **Env knobs:** `AICR_OLLAMA_URL`, `AICR_OLLAMA_MODEL`, `AICR_OLLAMA_TIMEOUT`, `AICR_USE_OLLAMA`, `AICR_SCOPE`, `AICR_BEFORE_SHA`, `AICR_HEAD_SHA`, `AICR_MAX_LLM_CHUNKS`, `AICR_FAIL_ON_HIGH`.

### A2. `templates/github-workflows/ai-review.yml` — the workflow
- **What:** ~85-line GitHub Actions workflow; the **only file a consumer repo needs**. Identical copy runs in the central repo to review its own PRs.
- **Trigger:** `pull_request` on `opened`, `synchronize`, `reopened`. `concurrency` cancels a superseded run on the same PR.
- **Permissions:** `contents: read`, `pull-requests: write` — the minimum to read code and post a review.
- **Env:** `OLLAMA_MODEL: mistral`, `AICR_VERSION: v1.1.0`.
- **Steps, in order:**
  1. `actions/checkout@v4` at the PR **head SHA** — the exact code under review.
  2. `curl … ollama.com/install.sh | sh` — installs the Ollama binary (~30 s).
  3. `actions/cache@v4` on `~/.ollama/models`, key `ollama-mistral` — restores the 4.4 GB model; download happens once per repo, not per run.
  4. `ollama serve &` → wait for `/api/tags` → `ollama pull` (no-op when cached).
  5. `curl` the reviewer from `raw.githubusercontent.com/…/${AICR_VERSION}/scripts/pr_review_action.py`.
  6. `python3 /tmp/pr_review_action.py <pr-number>` with `GH_TOKEN=${{ secrets.GITHUB_TOKEN }}` and the `AICR_*` env.
  7. On failure only: print `/tmp/ollama.log`.
- **Limits:** `timeout-minutes: 45`; per-file Ollama timeout 600 s.

### A3. Ollama — local model runtime
- **What:** open-source (MIT) server that runs GGUF-quantised LLMs on CPU or GPU and exposes a small HTTP API on `localhost:11434`.
- **Role here:** installed fresh on each ephemeral runner; serves `mistral`; receives our prompt on `/api/generate` and returns JSON. Runs entirely on the runner — no external inference calls.
- **Why:** trivial install, model caching, `format: json` mode, and the same API works unchanged against a persistent GPU host by changing `AICR_OLLAMA_URL`.

### A4. Mistral 7B — the model
- **What:** 7-billion-parameter open-weights LLM (Apache-2.0) by Mistral AI; Ollama's default 4-bit quantisation is 4.4 GB.
- **Role here:** reads a numbered code chunk and returns structured findings. Chosen after a head-to-head with `qwen2.5-coder:3b` (7 vs 13 findings on the same file; the 3B model misdiagnosed one).
- **Cost/perf:** free; ~1–3 min per 6 KB chunk on a 4-vCPU CPU runner; seconds on a GPU.
- **Trust model:** every response is validated before use; findings are labelled `🧠 ollama` so reviewers know the source.

### A5. GitHub Actions — the compute
- **What:** GitHub's hosted CI. `ubuntu-latest` = 4 vCPU / 16 GB RAM ephemeral VM, destroyed after the job.
- **Role here:** the sandbox everything runs in. Nothing persists except the model cache. Free for public repos; 2,000 min/month included for private.

### A6. `GITHUB_TOKEN` — the identity
- **What:** a short-lived token GitHub mints for each workflow run, scoped by the `permissions:` block, expiring when the job ends.
- **Role here:** authenticates the `gh` CLI. No personal access tokens, no stored secrets, nothing to rotate or leak. Comments appear as `github-actions[bot]`.

### A7. GitHub suggestion blocks — the "apply" mechanism
- **What:** GitHub-native markdown: a review comment containing ` ```suggestion\n<new line>\n``` ` is rendered as a diff with **Commit suggestion** / **Add suggestion to batch** buttons.
- **Role here:** our script only *writes the comment*; GitHub owns the buttons, creates the commit (authored by the clicker, co-authored by the bot), pushes it and resolves the thread. This is why the bot never needs write access to code.

### A8. Branch protection — the guard-rail
- **Where:** `main` in all four repos, applied via `PUT /repos/{r}/branches/main/protection`.
- **Rules:** PRs required; `review` status check required and up-to-date; every conversation resolved before merge; no force-push/delete; enforced for admins; 0 approvals (solo maintainer — raise for teams).
- **Effect:** the AI review *always* runs before merge, and ignoring a finding is an explicit, recorded **Resolve conversation** click.

### A9. Versioning — the release mechanism
- **What:** annotated git tags on the central repo (`v1.0.0`, `v1.1.0`). Consumers set `AICR_VERSION`.
- **Effect:** merging to `main` changes nothing downstream; consumers upgrade deliberately (one-line bump) and roll back the same way.

### A10. `samples/` — test fixtures
- Intentionally vulnerable Terraform (`demo/` web-app stack: S3, RDS, network, ECS), Python (`vulnerable_api.py`, `bad_performance.py`) and TypeScript (`api.ts`, `React.tsx`). Used to seed the demo PRs and to regression-test the reviewer locally.

### A11. Consumer repos
- `HenEarl11/terraform`, `HenEarl11/python`, `HenEarl11/typescript` — each contains the workflow file, a README, and a demo PR (#1) with a live review. The central repo `HenEarl11/ai-code-review-agent` also runs the workflow on itself.

### A12. Documentation
- `README.md` — what/why/layout. `ROLLOUT.md` — onboarding, knobs, protection, release procedure. `PANEL_BRIEF.md` — plain-English explainer and Q&A. This file — presentation pack.

---

## Appendix B — Data-flow / trust boundary (one slide if needed)

```
┌──────────────────────── GitHub (our tenancy) ────────────────────────┐
│                                                                        │
│  Repo ──PR event──▶ Actions runner (ephemeral VM)                      │
│                       │  code checked out here                         │
│                       │  Ollama + Mistral run here                     │
│                       │  reviewer script runs here                     │
│                       └──review comments──▶ PR                         │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
        ▲ one-time model download (public weights, inbound only)
   ollama.com registry            ← no source code ever crosses this line
```
