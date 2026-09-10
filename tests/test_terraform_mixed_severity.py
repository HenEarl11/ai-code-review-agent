def test_terraform_mixed_severity_detects_high_and_low(repo_root, analyzer):
    """Ensure Terraform sample returns a mix of high and low severity issue IDs."""
    sample = repo_root / "samples" / "terraform" / "main.tf"
    result = analyzer.analyze("terraform", sample.read_text(encoding="utf-8"))
    issue_ids = {issue["id"] for issue in result["issues"]}

    # High-severity (security/critical) example
    assert "hardcoded-db-password" in issue_ids

    # Low/operational example
    assert "single-replica-production" in issue_ids
