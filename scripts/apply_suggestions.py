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

    branch = f"ai-suggestions/{git(['rev-parse','--short','HEAD'])}"
    git(["checkout", "-b", branch])

    changed_files = set()
    for issue in issues_flat:
        if apply_fix_for_issue(issue):
            changed_files.add(issue["file"])

    if changed_files:
        git(["add", "."])
        git(["commit", "-m", f"Apply AI suggestions: {', '.join(sorted(changed_files))}"])
        print(f"Created branch {branch} with changes to: {', '.join(sorted(changed_files))}")
    else:
        print("No automatic fixes applied")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
