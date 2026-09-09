def test_terraform_sample_analysis_detects_expected_issues(repo_root, analyzer):
    sample = repo_root / "samples" / "terraform" / "main.tf"
    result = analyzer.analyze("terraform", sample.read_text(encoding="utf-8"))
    issue_ids = {issue["id"] for issue in result["issues"]}

    assert "public-s3-bucket" in issue_ids
    assert "hardcoded-db-password" in issue_ids
    assert "unencrypted-rds" in issue_ids
    assert "missing-backup-policy" in issue_ids
    assert "single-replica-production" in issue_ids
