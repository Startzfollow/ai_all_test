from fastapi.testclient import TestClient
from backend.app.main import app


def test_health():
    client = TestClient(app)
    resp = client.get("/api/system/health")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_gui_plan():
    client = TestClient(app)
    resp = client.post("/api/agent/gui/plan", json={"task": "打开浏览器搜索 RAG", "dry_run": True})
    assert resp.status_code == 200
    assert resp.json()["plan"]
