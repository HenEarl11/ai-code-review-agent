# AI Code Review — Panel Briefing

A plain-English explanation of what was built, why, and answers to the questions a
panel is likely to ask.

---

## The 60-second version

> Every time a developer opens a pull request, an AI reviewer reads the changed
> files and leaves comments on the exact lines where it finds security holes,
> misconfigurations or bugs — with a one-click fix where it can. It runs entirely
> inside GitHub on a free runner, using an open-source AI model that runs locally,
> so **no code ever leaves GitHub**, and it costs nothing per review. It's live on
> three repositories today (Terraform, Python, TypeScript).

---

## The problem it solves

- Human code review is slow and inconsistent. Security mistakes (hard-coded
  passwords, open firewall rules, SQL injection) slip through because reviewers are
  busy or not specialists.
- Commercial AI review tools (Copilot Review, CodeRabbit, etc.) send your source code
  to a third-party cloud — often a non-starter for sensitive codebases — and charge
  per seat.
- Traditional linters catch only what someone has already written a rule for.

## What the solution does

1. Developer opens a PR (or pushes more commits to it).
2. GitHub Actions spins up a fresh, disposable Linux machine.
3. It installs **Ollama** (an open-source tool for running AI models locally) and
   loads **Mistral 7B**, an open-weights model. The 4 GB model is cached so it
   downloads once, not every run.
4. Our reviewer script looks at each changed `.tf`, `.py`, `.ts` file and does two
   passes:
   - **Fast rules** — ~20 regex checks for well-known problems (hard-coded secrets,
     `0.0.0.0/0` firewall rules, unencrypted storage, `eval()`, `innerHTML`...).
     Deterministic, instant, and each comes with a known-good one-line fix.
   - **AI pass** — the model reads the whole file, numbered line by line, and is
     asked to return a structured list of problems: line, severity, explanation and
     (optionally) a corrected line.
5. Results are merged and posted as **one PR review** with inline comments. Where a
   safe one-line fix exists it's shown as a GitHub *suggestion* — the developer
   clicks **Apply suggestion** and it's committed. Nothing is changed automatically.
6. The check is advisory by default (never blocks a merge) but can be flipped to
   block on high-severity findings with one setting.

## What it found on the demo PRs

| Repo | Findings | Of which from the AI | Time |
|---|---|---|---|
| Terraform (5 files, web-app stack) | 21 (11 high) | 13 | ~10 min |
| Python (2 files, orders API) | 10 | 9 | ~9 min |
| TypeScript (2 files, dashboard) | 9 | 7 | ~5 min |

Examples: publicly-readable S3 bucket, database with no encryption and
`skip_final_snapshot`, SSH open to the world, hard-coded API key, SQL built with
string formatting, `dangerouslySetInnerHTML`, `eval()` on user input, N+1 query loop.

## Design decisions (and why)

| Decision | Why |
|---|---|
| **Local open-source model, not a cloud API** | Code never leaves the GitHub runner. No API keys, no per-token bill, no vendor data-retention policy to review. |
| **Mistral 7B over a smaller model** | Tested `qwen2.5-coder:3b`: 3× faster but found about half the issues and misdiagnosed one. Review quality matters more than 5 minutes. |
| **Rules + AI, not AI alone** | Rules give a guaranteed floor (a hard-coded secret is *always* flagged) and precise fixes. The AI finds the things nobody wrote a rule for. |
| **Suggestions only, never auto-commit** | Developer stays in control; nothing merges without a human deciding. Also avoids the AI "fixing" a secret by inventing a new one — we explicitly guard against that. |
| **One central script, fetched at run time** | Three repos, one copy of the logic. Each consumer repo contains a single 80-line workflow file. |
| **Pinned to a release tag** | Consumers reference `v1.0.0`, so a change to the reviewer can't silently alter behaviour across every repo. Upgrades are a deliberate one-line bump; rollback is the same line. |
| **Standard library only, no dependencies** | Nothing to install, nothing to audit, nothing to break. |
| **Uses the built-in `GITHUB_TOKEN`** | No personal access tokens or secrets to create, rotate or leak. Permissions are the minimum: read code, write PR comments. |

## Limitations (say these before they ask)

- **Speed.** CPU-only runners mean ~1–3 minutes per file. A big PR could take 30+
  minutes. A self-hosted runner with a GPU would make it under a minute; the
  workflow already supports pointing at one.
- **Non-deterministic.** The AI pass can find slightly different things on
  re-runs. The rules pass is fully deterministic and is the safety net.
- **False positives happen.** It's a reviewer, not a gate. That's why it's advisory
  by default.
- **Reviews files, not architecture.** It sees one file at a time; it won't spot a
  problem that spans several modules.
- **Reviews what changed, not what was already there.** By design it only flags
  lines the PR touched, so pre-existing problems in the same file go unremarked.
  A one-off `AICR_SCOPE: full` run covers that when needed.
- **Three languages today.** Adding one is adding an entry to a dictionary plus a
  few regexes.

---

## Likely questions

**"Is our code sent to OpenAI / Anthropic / anyone?"**
No. The model runs on the GitHub Actions runner itself, which is a throw-away VM
that's destroyed after the job. The only network calls are to GitHub's own API to
post the comments and to download the model weights from Ollama's registry (which
is a download *to* the runner, not code going out).

**"How much does it cost?"**
Nothing beyond GitHub Actions minutes, which are free for public repos and included
in the plan for private ones. No model API fees, no per-seat licence.

**"How accurate is it?"**
On the seeded demo files, it found every planted issue and added several genuine
ones we hadn't planted. Hard-to-quantify on real code yet — the sensible next step
is a month of running advisory-only and tracking which comments developers act on.

**"What stops it making things worse?"**
It never changes code itself. Every fix is a suggestion the developer has to click
to accept, and appears in the PR diff like any other commit. We also block the AI
from suggesting a replacement secret value.

**"What if the AI is down or slow?"**
If Ollama fails to start or times out, the rules pass still runs and the review is
still posted — you get a reduced review, not a failed check. Each file has a
10-minute ceiling and the whole job 45 minutes.

**"Why not just use GitHub Copilot's code review?"**
Copilot sends code to Microsoft/OpenAI's cloud and is a paid add-on. This is the
same *shape* of feature with the data staying in-house and zero marginal cost — and
we control exactly what it looks for.

**"Can it block a merge?"**
Yes — set `AICR_FAIL_ON_HIGH: "true"` and make the check required in branch
protection. Recommended only after a bedding-in period so developers trust it.

**"If a developer decides to ignore a suggestion, will it keep nagging?"**
No. It only reviews lines the PR actually changed, and when more commits are
pushed it only looks at what changed since the last review. An ignored finding
stays in the earlier review for the record, but isn't re-raised unless that line
is edited again.

**"How do we roll it out to another repo?"**
Copy one file (`ai-review.yml`) into `.github/workflows/`. Nothing else. Takes
under five minutes; documented in `ROLLOUT.md`.

**"How do we update it, and what if an update breaks things?"**
Change the script, tag a release, bump `AICR_VERSION` in the consumer repos. Roll
back by changing the version back. Consumers never pick up changes they didn't
opt into.

**"Can we add our own rules?"**
Yes. Each rule is a single line: an ID, a regex, a severity, a message and an
optional fixer. Typical time to add one is a few minutes.

**"Could we use a bigger/better model?"**
Yes — it's one environment variable. Anything Ollama can run works. A larger model
on a CPU runner would be slower; a GPU runner opens up 13B–70B models.

**"What did this cost to build?"**
One script (~400 lines, Python standard library), one workflow file, no
infrastructure. Built and rolled out to three repos in a single working session.

---

## If you have to demo it live

1. Open one of the demo PRs (links in `ROLLOUT.md`). Show the inline comments with
   🔴/🟠/🟡 severity, the `🧠 ollama` tag on AI findings, and an **Apply suggestion**
   button.
2. Open the Actions run log — show the `[ollama] file.tf: 7 raw -> 7 valid findings`
   lines to make the point that the model is doing real work.
3. Show the consumer repo's `.github/workflows/ai-review.yml` — the entire footprint
   in that repo is that one file.
