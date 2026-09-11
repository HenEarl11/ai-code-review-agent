#!/usr/bin/env python3
"""Self-contained AI PR reviewer for GitHub Actions (suggestions only, no code changes).

Runs inside the target repo checkout. For every file changed in the PR it:
  1. Runs regex-based detectors (Terraform, Python, TypeScript).
  2. Maps each finding to a line in the PR diff.
  3. Posts ONE pull-request review containing inline comments, each with a
     ```suggestion``` block where a safe one-line replacement is known, so the
     author can click "Apply suggestion" in the GitHub UI.

Usage (in Actions):
    python3 pr_review_action.py <pr-number>

Required env: GITHUB_TOKEN (or GH_TOKEN), GITHUB_REPOSITORY (owner/repo).
Optional env: AICR_FAIL_ON_HIGH=true  -> exit 1 if any high-severity finding.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Detectors: (id, regex, severity, message, fixer | None)
# fixer(line) -> replacement line, or None if no safe auto-suggestion
# ---------------------------------------------------------------------------

def _tf_set(key, value):
    def fix(line):
        indent = re.match(r"^\s*", line).group(0)
        return f"{indent}{key} = {value}"
    return fix


DETECTORS = {
    "terraform": [
        ("public-s3-acl", re.compile(r'\bacl\s*=\s*"public-read(-write)?"'), "high",
         "S3 bucket ACL is public. Restrict access or use bucket policies.",
         _tf_set("acl", '"private"')),
        ("hardcoded-secret", re.compile(r'\b(password|secret|access_key|secret_key|token)\s*=\s*"[^"$]{4,}"', re.I), "high",
         "Hardcoded secret in Terraform. Use a variable, `sensitive = true`, or a secrets manager.",
         None),
        ("unencrypted-storage", re.compile(r'\bstorage_encrypted\s*=\s*false'), "high",
         "RDS storage is unencrypted. Enable encryption at rest.",
         _tf_set("storage_encrypted", "true")),
        ("publicly-accessible-db", re.compile(r'\bpublicly_accessible\s*=\s*true'), "high",
         "Database is publicly accessible. Set to false and access via VPC.",
         _tf_set("publicly_accessible", "false")),
        ("no-backup-retention", re.compile(r'\bbackup_retention_period\s*=\s*0\b'), "medium",
         "Backups are disabled. Set a retention period of at least 7 days.",
         _tf_set("backup_retention_period", "7")),
        ("skip-final-snapshot", re.compile(r'\bskip_final_snapshot\s*=\s*true'), "medium",
         "Final snapshot skipped on destroy — data loss risk.",
         _tf_set("skip_final_snapshot", "false")),
        ("single-az", re.compile(r'\bmulti_az\s*=\s*false'), "low",
         "Single-AZ deployment. Consider multi_az = true for production.",
         _tf_set("multi_az", "true")),
        ("single-replica", re.compile(r'\breplicas\s*=\s*1\b'), "low",
         "Single replica. Consider >= 2 for availability.",
         _tf_set("replicas", "2")),
        ("open-ingress", re.compile(r'cidr_blocks\s*=\s*\[\s*"0\.0\.0\.0/0"\s*\]'), "high",
         "Security group open to the world (0.0.0.0/0). Restrict CIDR ranges.",
         None),
        ("latest-image-tag", re.compile(r'image\s*=\s*"[^"]+:latest"'), "low",
         "Container image uses :latest tag. Pin to an immutable version.",
         None),
        ("no-versioning", re.compile(r'\bversioning\s*\{\s*enabled\s*=\s*false'), "low",
         "S3 versioning disabled. Enable to protect against accidental deletion.",
         None),
    ],
    "python": [
        ("hardcoded-credentials", re.compile(r'\b(API_KEY|SECRET|PASSWORD|TOKEN)\w*\s*=\s*["\'][^"\']+["\']', re.I), "high",
         "Hardcoded credential. Load from environment or a secrets manager.", None),
        ("unsafe-deserialization", re.compile(r'\bpickle\.loads?\('), "high",
         "Unsafe deserialization with pickle. Use json or a safe parser.", None),
        ("sql-injection", re.compile(r'\.execute\(\s*(f["\']|.*\+|.*%\s*\()'), "high",
         "Possible SQL injection. Use parameterised queries.", None),
        ("bare-except", re.compile(r'^\s*except\s*:'), "low",
         "Bare except swallows all errors. Catch specific exceptions.",
         lambda l: l.replace("except:", "except Exception:")),
        ("eval-usage", re.compile(r'\beval\('), "high",
         "eval() on untrusted input is dangerous.", None),
    ],
    "typescript": [
        ("xss-risk", re.compile(r'dangerouslySetInnerHTML'), "high",
         "dangerouslySetInnerHTML can introduce XSS. Sanitise HTML first.", None),
        ("unsafe-eval", re.compile(r'\beval\('), "high",
         "eval() is unsafe. Use JSON.parse or a safer alternative.", None),
        ("console-log", re.compile(r'^\s*console\.(log|debug)\('), "low",
         "Remove console logging from production code.",
         lambda l: re.sub(r'^(\s*)', r'\1// ', l, count=1)),
        ("event-listener-leak", re.compile(r'addEventListener\('), "low",
         "Ensure this listener is removed in a cleanup/unmount handler.", None),
    ],
}

EXT_TO_LANG = {
    ".tf": "terraform", ".tfvars": "terraform",
    ".py": "python",
    ".ts": "typescript", ".tsx": "typescript", ".js": "typescript", ".jsx": "typescript",
}

IGNORE_DIRS = ("node_modules/", "venv/", ".venv/", ".terraform/", "dist/", "build/", "__pycache__/")


# ---------------------------------------------------------------------------
# GitHub helpers
# ---------------------------------------------------------------------------

def gh_api(path, method="GET", payload=None):
    cmd = ["gh", "api", path, "-X", method, "-H", "Accept: application/vnd.github+json"]
    if payload is not None:
        cmd += ["--input", "-"]
        return subprocess.run(cmd, input=json.dumps(payload).encode(), check=True,
                              capture_output=True).stdout
    return subprocess.run(cmd, check=True, capture_output=True).stdout


def get_pr_files(repo, pr):
    files = []
    page = 1
    while True:
        out = gh_api(f"/repos/{repo}/pulls/{pr}/files?per_page=100&page={page}")
        batch = json.loads(out)
        if not batch:
            break
        files.extend(batch)
        page += 1
    return files


def added_or_context_lines(patch):
    """Return set of new-file line numbers that appear in the diff (commentable)."""
    lines = set()
    new_line = None
    for raw in patch.splitlines():
        if raw.startswith("@@"):
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", raw)
            new_line = int(m.group(1)) if m else None
            continue
        if new_line is None:
            continue
        if raw.startswith("+"):
            lines.add(new_line)
            new_line += 1
        elif raw.startswith("-"):
            pass
        else:
            lines.add(new_line)
            new_line += 1
    return lines


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def scan(path: Path, lang: str):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for rule_id, rx, sev, msg, fixer in DETECTORS[lang]:
            if rx.search(line):
                replacement = fixer(line) if fixer else None
                findings.append({
                    "id": rule_id, "line": lineno, "severity": sev,
                    "message": msg, "original": line, "replacement": replacement,
                })
    return findings


def build_comment(f):
    icon = {"high": "🔴", "medium": "🟠", "low": "🟡"}[f["severity"]]
    body = f"{icon} **{f['severity'].upper()}** `{f['id']}`\n\n{f['message']}"
    if f["replacement"] and f["replacement"] != f["original"]:
        body += f"\n\n```suggestion\n{f['replacement']}\n```"
    return body


def main(argv):
    if len(argv) < 2:
        print("Usage: pr_review_action.py <pr-number>", file=sys.stderr)
        return 2
    pr = argv[1]
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        print("GITHUB_REPOSITORY not set", file=sys.stderr)
        return 2

    files = get_pr_files(repo, pr)
    comments, summary, high_count = [], [], 0

    for f in files:
        name = f["filename"]
        if f.get("status") == "removed" or any(d in name for d in IGNORE_DIRS):
            continue
        lang = EXT_TO_LANG.get(Path(name).suffix.lower())
        if not lang or not f.get("patch"):
            continue
        commentable = added_or_context_lines(f["patch"])
        for finding in scan(Path(name), lang):
            if finding["severity"] == "high":
                high_count += 1
            summary.append(f"- `{name}:{finding['line']}` **{finding['severity']}** `{finding['id']}` — {finding['message']}")
            if finding["line"] in commentable:
                comments.append({
                    "path": name, "line": finding["line"], "side": "RIGHT",
                    "body": build_comment(finding),
                })

    if not summary:
        body = "✅ **AI Review** — no issues detected in changed files."
        gh_api(f"/repos/{repo}/issues/{pr}/comments", "POST", {"body": body})
        print(body)
        return 0

    review_body = (
        f"🤖 **AI Review** — {len(summary)} finding(s), {high_count} high severity.\n\n"
        "Inline suggestions are attached where a safe fix is known — click **Apply suggestion** to accept.\n\n"
        "<details><summary>All findings</summary>\n\n" + "\n".join(summary) + "\n\n</details>"
    )
    payload = {"body": review_body, "event": "COMMENT", "comments": comments}
    try:
        gh_api(f"/repos/{repo}/pulls/{pr}/reviews", "POST", payload)
    except subprocess.CalledProcessError as e:
        # Fallback: some inline positions may be rejected; post summary only.
        print("Inline review failed, posting summary comment:", e.stderr.decode(), file=sys.stderr)
        gh_api(f"/repos/{repo}/issues/{pr}/comments", "POST", {"body": review_body})

    print(review_body)
    print(f"Posted {len(comments)} inline comment(s).")

    if os.environ.get("AICR_FAIL_ON_HIGH", "").lower() == "true" and high_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
