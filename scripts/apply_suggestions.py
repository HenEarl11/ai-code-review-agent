#!/usr/bin/env python3
"""Apply simple suggestions automatically and create a git branch with changes.

This script is intentionally conservative and only performs safe textual fixes for demo purposes.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIR = ROOT / "scan_results"


def apply_fix_for_issue(issue):
    file_path = ROOT / issue["file"]
    if not file_path.exists():
        return False
    text = file_path.read_text(encoding="utf-8")
    changed = False

    if issue["id"] == "console-log-in-production":
        new = text.replace("console.log(", "// console.log(")
        if new != text:
            file_path.write_text(new, encoding="utf-8")
            changed = True

    if issue["id"] == "hardcoded-db-password":
        new = text.replace('password                = "hardcoded_db_password"', 'password = var.db_password')
        if new != text:
            file_path.write_text(new, encoding="utf-8")
            changed = True

    if issue["id"] == "single-replica-production":
        new = text.replace("replicas = 1", "replicas = 2")
        if new != text:
            file_path.write_text(new, encoding="utf-8")
            changed = True

    if issue["id"] == "public-s3-bucket":
        new = text.replace('acl    = "public-read"', 'acl = "private"')
        if new != text:
            file_path.write_text(new, encoding="utf-8")
            changed = True

    return changed


def git(cmd):
    return subprocess.check_output(["git"] + cmd, cwd=ROOT).decode().strip()


def main():
    # load aggregated results
    allf = SCAN_DIR / "all_results.json"
    if not allf.exists():
        print("No scan results found (run scripts/local_scan.py first)")
        return 1
    data = json.loads(allf.read_text(encoding="utf-8"))
    issues_flat = []
    for r in data:
        issues_flat.extend(r.get("analysis_data", {}).get("issues", []))

    if not issues_flat:
        print("No issues to apply")
        return 0

    # ensure git user identity is set (use repository-local config if not global)
    try:
        git(["config", "user.email"])
    except subprocess.CalledProcessError:
        subprocess.check_call(["git", "config", "user.email", "ai-bot@example.com"], cwd=ROOT)
        subprocess.check_call(["git", "config", "user.name", "AI Suggestion Bot"], cwd=ROOT)

    branch = f"ai-suggestions/{git(['rev-parse','--short','HEAD'])}"
    # if branch exists locally, checkout it; otherwise create it
    existing = git(["branch", "--list", branch])
    if existing:
        git(["checkout", branch])
    else:
        git(["checkout", "-b", branch])

    changed_files = []
    for issue in issues_flat:
        if apply_fix_for_issue(issue):
            if issue["file"] not in changed_files:
                changed_files.append(issue["file"])

    # remove embedded/cloned repos from index if they exist to avoid submodule warnings
    for embedded in [".scan_tmp", "test_repos"]:
        emb_path = ROOT / embedded
        if emb_path.exists():
            try:
                git(["rm", "--cached", "-r", embedded])
            except subprocess.CalledProcessError:
                # ignore if not in index
                pass

    if changed_files:
        # add only the changed files
        for f in changed_files:
            git(["add", f])
        git(["commit", "-m", f"Apply AI suggestions: {', '.join(sorted(changed_files))}"])
        print(f"Created branch {branch} with changes to: {', '.join(sorted(changed_files))}")
    else:
        print("No automatic fixes applied")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
