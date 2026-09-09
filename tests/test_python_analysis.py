def test_python_sample_analysis_detects_expected_issues(repo_root, analyzer):
    sample = repo_root / "samples" / "python" / "vulnerable_api.py"
    result = analyzer.analyze("python", sample.read_text(encoding="utf-8"))
    issue_ids = {issue["id"] for issue in result["issues"]}

    assert "hardcoded-credentials" in issue_ids
    assert "unsafe-deserialization" in issue_ids
    assert "sql-injection" in issue_ids
    assert "bare-except" in issue_ids
    assert "nested-loop-performance" in issue_ids
