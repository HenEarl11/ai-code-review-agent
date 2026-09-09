def test_config_loading_defaults(load_config):
    config = load_config()
    assert config["backend_url"] == "http://localhost:8080"
    assert config["ollama_url"] == "http://localhost:11434"
    assert config["jira_project"] == "AICR"
    assert config["cache_enabled"] is True


def test_config_loading_overrides(load_config, monkeypatch):
    monkeypatch.setenv("AICR_BACKEND_URL", "http://localhost:9000")
    monkeypatch.setenv("AICR_OLLAMA_URL", "http://localhost:11434")
    monkeypatch.setenv("AICR_JIRA_PROJECT", "HACK")
    monkeypatch.setenv("AICR_CACHE_ENABLED", "false")

    config = load_config()
    assert config["backend_url"] == "http://localhost:9000"
    assert config["jira_project"] == "HACK"
    assert config["cache_enabled"] is False
