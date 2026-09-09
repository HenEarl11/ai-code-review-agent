def test_jira_sync_returns_tracking_keys(jira_client):
    issues = [{"id": "xss-risk"}, {"id": "sql-injection"}]
    result = jira_client.sync_issues(issues, project_key="DEMO")

    assert result["project"] == "DEMO"
    assert result["created"] == 2
    assert result["issue_keys"] == ["DEMO-1", "DEMO-2"]
