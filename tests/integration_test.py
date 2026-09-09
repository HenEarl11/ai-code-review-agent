def test_end_to_end_analysis_flow(repo_root, analyzer, jira_client, ollama_client):
    python_file = repo_root / "samples" / "python" / "vulnerable_api.py"
    code = python_file.read_text(encoding="utf-8")

    analysis = analyzer.analyze("python", code)
    llm_review = ollama_client.review(code, model="mistral")
    jira_result = jira_client.sync_issues(analysis["issues"])

    assert analysis["issues"]
    assert llm_review["model"] == "mistral"
    assert jira_result["created"] == len(analysis["issues"])


def test_analysis_cache_hit(repo_root, analyzer):
    ts_file = repo_root / "samples" / "typescript" / "React.tsx"
    code = ts_file.read_text(encoding="utf-8")

    first = analyzer.analyze("typescript", code)
    second = analyzer.analyze("typescript", code)

    assert first is second
