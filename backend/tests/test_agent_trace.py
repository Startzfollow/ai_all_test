from fastapi.testclient import TestClient

from backend.app.main import app


def test_gui_agent_returns_trace():
    client = TestClient(app)
    resp = client.post("/api/agent/gui/plan", json={"task": "打开浏览器搜索 RAG", "dry_run": True})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["plan"]
    assert payload["trace"]
    assert payload["trace"][0]["stage"] == "observe"
    assert any(event["stage"] == "safety" for event in payload["trace"])
