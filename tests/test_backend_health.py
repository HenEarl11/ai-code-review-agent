def test_backend_health_check(analyzer):
    result = analyzer.health_check()
    assert result["status"] == "ok"
    assert result["service"] == "analysis-engine"
