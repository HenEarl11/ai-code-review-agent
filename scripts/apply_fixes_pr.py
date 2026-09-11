#!/usr/bin/env python3
"""Apply safe fixes for files changed in a PR, create a fixes branch, commit and push.

Usage: ./scripts/apply_fixes_pr.py <pr-number>

Requires: gh and git available. Will create branch `fixes/pr-<pr-number>` and push it.
"""
import json
import subprocess
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_SCRIPT = ROOT / "scripts" / "local_scan.py"
SCAN_DIR = ROOT / "scan_results"


def run(cmd):
    return subprocess.check_output(cmd, cwd=ROOT).decode().strip()


def ensure_git_identity():
    try:
        name = run(["git", "config", "user.name"]) or None
        email = run(["git", "config", "user.email"]) or None
    except Exception:
        name = email = None
    if not name:
        run(["git", "config", "user.name", "ai-bot"])
    if not email:
        run(["git", "config", "user.email", "ai-bot@example.com"])


def get_pr_files(pr):
    out = subprocess.check_output(["gh", "pr", "view", pr, "--json", "files"], cwd=ROOT).decode()
    data = json.loads(out)
    return [f["path"] for f in data.get("files", [])]


def apply_fix_to_text(issue, text):
    # conservative textual fixes
    if issue["id"] == "console-log-in-production":
        # handle typical console.log usages
        new = text.replace("console.log(", "// console.log(")
        new = new.replace("console.error(", "// console.error(")
        return new
    if issue["id"] == "hardcoded-db-password":
        return text.replace('password                = "hardcoded_db_password"', 'password = var.db_password')
    if issue["id"] == "single-replica-production":
        return text.replace("replicas = 1", "replicas = 2")
    if issue["id"] == "public-s3-bucket":
        return text.replace('acl    = "public-read"', 'acl = "private"')
    # generic conservative fixes
    if issue["id"] == "bare-except":
        # replace bare except Exception: with except Exception:
        new = text.replace('\nexcept:\n', '\nexcept Exception:\n')
        # also try inline variations
        new = new.replace('except Exception: ', 'except Exception: ')
        return new

    # Post-process: strip trailing whitespace and collapse multiple blank lines
    # (apply to all files but only if the issue suggests changes)
    new = text
    # remove trailing spaces
    new = '\n'.join([ln.rstrip() for ln in new.splitlines()])
    # collapse more than 2 consecutive newlines
    new = re.sub(r"\n{3,}", "\n\n", new)
    return new
    # no change
    return text


def main(argv):
    if len(argv) < 2:
        print("Usage: ./scripts/apply_fixes_pr.py <pr-number>")
        return 2
    pr = argv[1]

    try:
        pr_files = get_pr_files(pr)
    except FileNotFoundError:
        print("gh CLI not installed or not authenticated")
        return 1

    if not pr_files:
        print("No files changed in PR")
        return 0

    print("Scanning PR files:")
    for f in pr_files:
        print(" -", f)

    # run scanner only on PR files
    subprocess.check_call([str(SCAN_SCRIPT)] + pr_files, cwd=ROOT)

    allf = SCAN_DIR / "all_results.json"
    if not allf.exists():
        print("No scan results found")
        return 1
    data = json.loads(allf.read_text(encoding="utf-8"))

    # map file -> issues
    file_issues = {r.get("analysis_data", {}).get("file_path"): r.get("analysis_data", {}).get("issues", []) for r in data}
    changed = set()

    # ensure git identity to allow commits inside container/CI
    ensure_git_identity()

    # create branch
    branch = f"fixes/pr-{pr}"
    try:
        run(["git", "checkout", "-b", branch])
    except Exception:
        # if branch exists, checkout
        run(["git", "checkout", branch])

    # apply fixes
    for fpath, issues in file_issues.items():
        if not issues:
            continue
        target = ROOT / fpath
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8")
        new = text
        for issue in issues:
            new = apply_fix_to_text(issue, new)
        if new != text:
            target.write_text(new, encoding="utf-8")
            changed.add(fpath)

    if changed:
        run(["git", "add"] + sorted(changed))
        run(["git", "commit", "-m", f"Apply AI fixes for PR #{pr}: {', '.join(sorted(changed))}"])
        run(["git", "push", "-u", "origin", branch])
        print(f"Pushed fixes branch: {branch}")
    else:
        print("No automatic fixes applied for PR files")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
