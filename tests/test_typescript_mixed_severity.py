def test_typescript_mixed_severity_detects_high_and_low(repo_root, analyzer):
    """Ensure TypeScript sample returns both high (XSS) and low (console logs) issues."""
    sample = repo_root / "samples" / "typescript" / "React.tsx"
    result = analyzer.analyze("typescript", sample.read_text(encoding="utf-8"))
    issue_ids = {issue["id"] for issue in result["issues"]}

    # High-severity (security) example
    assert "xss-risk" in issue_ids

    # Low-severity / quality example
    assert "console-log-in-production" in issue_ids
