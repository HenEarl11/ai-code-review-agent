import os
from pathlib import Path

import pytest


class MockAnalysisEngine:
    def __init__(self):
        self._cache = {}

    def health_check(self):
        return {"status": "ok", "service": "analysis-engine"}

    def analyze(self, language: str, content: str):
        cache_key = (language, content)
        if cache_key in self._cache:
            return self._cache[cache_key]

        issues = []
        checks = {
            "python": [
                ("API_KEY =", "hardcoded-credentials"),
                ("pickle.loads", "unsafe-deserialization"),
                ("cursor.execute(query)", "sql-injection"),
                ("except:", "bare-except"),
                ("for row in rows", "nested-loop-performance"),
            ],
            "terraform": [
                ('acl    = "public-read"', "public-s3-bucket"),
                ('password                = "hardcoded_db_password"', "hardcoded-db-password"),
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

        for marker, issue_id in checks.get(language, []):
            if marker in content:
                issues.append({"id": issue_id})

        result = {"language": language, "issues": issues}
        self._cache[cache_key] = result
        return result


class MockJiraClient:
    def sync_issues(self, issues, project_key="AICR"):
        return {
            "project": project_key,
            "created": len(issues),
            "issue_keys": [f"{project_key}-{index + 1}" for index, _ in enumerate(issues)],
        }


class MockOllamaClient:
    def review(self, code: str, model: str = "mistral"):
        return {
            "model": model,
            "summary": "Detected multiple review findings",
            "issue_count": max(1, code.count("\n") // 5),
        }


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def analyzer():
    return MockAnalysisEngine()


@pytest.fixture
def jira_client():
    return MockJiraClient()


@pytest.fixture
def ollama_client():
    return MockOllamaClient()


@pytest.fixture
def load_config(monkeypatch):
    def _loader():
        return {
            "backend_url": os.getenv("AICR_BACKEND_URL", "http://localhost:8080"),
            "ollama_url": os.getenv("AICR_OLLAMA_URL", "http://localhost:11434"),
            "jira_project": os.getenv("AICR_JIRA_PROJECT", "AICR"),
            "cache_enabled": os.getenv("AICR_CACHE_ENABLED", "true").lower() == "true",
        }

    return _loader
