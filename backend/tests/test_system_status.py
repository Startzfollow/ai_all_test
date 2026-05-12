from fastapi.testclient import TestClient

from backend.app.main import app


def test_system_status_contract():
    client = TestClient(app)
    resp = client.get("/api/system/status")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    assert "rag_store" in payload
    assert "yolo" in payload
