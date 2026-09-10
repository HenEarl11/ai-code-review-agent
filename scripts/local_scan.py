#!/usr/bin/env python3
"""Simple local scanner that mirrors the MockAnalysisEngine checks and writes scan_results/*.json

This avoids requiring the backend to be running; it's for local-only demos.
"""
import json
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIR = ROOT / "scan_results"
SCAN_DIR.mkdir(exist_ok=True)

CHECKS = {
    "python": [
        ("API_KEY =", "hardcoded-credentials"),
        ("pickle.loads", "unsafe-deserialization"),
        ("cursor.execute(query)", "sql-injection"),
        ("except:", "bare-except"),
        ("for row in rows", "nested-loop-performance"),
    ],
    "terraform": [
        ("acl    = \"public-read\"", "public-s3-bucket"),
        ("password                = \"hardcoded_db_password\"", "hardcoded-db-password"),
        ("storage_encrypted       = false", "unencrypted-rds"),
        ("backup_retention_period = 0", "missing-backup-policy"),
        ("replicas = 1", "single-replica-production"),
    ],
    "typescript": [
        ("dangerouslySetInnerHTML", "xss-risk"),
        ("console.log", "console-log-in-production"),
        ("useEffect(() =>", "useeffect-missing-deps"),
        ("window.addEventListener", "event-listener-leak"),
        ("eval(input)", "unsafe-eval"),
    ],
}


def detect_language(path: Path):
    suffix = path.suffix.lower()
    if suffix in (".py",):
        return "python"
    if suffix in (".tf", ".tfvars"):
        return "terraform"
    if suffix in (".ts", ".tsx", ".js", ".jsx"):
        return "typescript"
    return None


def scan_file(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    lang = detect_language(path)
    if not lang:
        return None

    issues = []
    checks = CHECKS.get(lang, [])
    for marker, issue_id in checks:
        if marker in text:
            # crude line number: first occurrence
            line_no = text.find(marker)
            lineno = text[:line_no].count("\n") + 1
            issues.append({
                "file": str(path.relative_to(ROOT)),
                "line": lineno,
                "message": f"Detected pattern: {marker}",
                "severity": "high" if "hardcoded" in issue_id or "xss" in issue_id or "sql" in issue_id or "unsafe" in issue_id else "low",
                "subtype": issue_id,
                "suggestion": suggestion_for_issue(issue_id),
                "type": "security" if any(x in issue_id for x in ("hardcoded","xss","sql","unsafe")) else "standard",
                "id": issue_id,
            })

    if not issues:
        return None

    result = {
        "analysis_data": {
            "file_path": str(path.relative_to(ROOT)),
            "issues": issues,
            "language": lang,
            "summary": {
                "by_severity": {},
                "by_type": {},
                "total_issues": len(issues),
            },
        },
        "created_at": datetime.utcnow().isoformat(),
        "file_path": str(path.relative_to(ROOT)),
        "language": lang,
    }
    return result


def suggestion_for_issue(issue_id: str) -> str:
    mapping = {
        "hardcoded-credentials": "Review and remove hardcoded credentials",
        "unsafe-deserialization": "Avoid unsafe deserialization; use safe parsers",
        "sql-injection": "Use parameterized queries",
        "bare-except": "Catch specific exceptions",
        "nested-loop-performance": "Consider optimizing nested loops",
        "public-s3-bucket": "Make S3 bucket private or restrict access",
        "hardcoded-db-password": "Replace hardcoded password with var/db secret",
        "unencrypted-rds": "Enable storage_encrypted",
        "missing-backup-policy": "Set a non-zero backup_retention_period",
        "single-replica-production": "Increase replicas for production",
        "xss-risk": "Sanitize HTML before rendering (avoid dangerouslySetInnerHTML)",
        "console-log-in-production": "Remove console.log statements",
        "useeffect-missing-deps": "Add dependency array to useEffect",
        "event-listener-leak": "Add cleanup to remove event listeners",
        "unsafe-eval": "Avoid eval; use safer alternatives",
    }
    return mapping.get(issue_id, "Inspect and apply suggested fix")


def main():
    root = ROOT
    files = list(root.rglob("*.*"))
    results = []
    for f in files:
        if "/.git/" in str(f) or "scan_results" in str(f) or "node_modules" in str(f):
            continue
        r = scan_file(f)
        if r:
            out = SCAN_DIR / (r["analysis_data"]["file_path"].replace("/", "_") + ".json")
            out.write_text(json.dumps(r, indent=2))
            results.append(out)

    # write aggregated all_results.json
    all_results = []
    for p in results:
        all_results.append(json.loads(p.read_text(encoding="utf-8")))
    (SCAN_DIR / "all_results.json").write_text(json.dumps(all_results, indent=2))
    print(f"Wrote {len(results)} report(s) to {SCAN_DIR}")


if __name__ == "__main__":
    main()
