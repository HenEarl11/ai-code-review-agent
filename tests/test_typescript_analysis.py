def test_typescript_sample_analysis_detects_expected_issues(repo_root, analyzer):
    sample = repo_root / "samples" / "typescript" / "React.tsx"
    result = analyzer.analyze("typescript", sample.read_text(encoding="utf-8"))
    issue_ids = {issue["id"] for issue in result["issues"]}

    assert "xss-risk" in issue_ids
    assert "console-log-in-production" in issue_ids
    assert "useeffect-missing-deps" in issue_ids
    assert "event-listener-leak" in issue_ids
