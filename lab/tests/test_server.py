import os
import uuid
os.environ["LAB_API_KEY"] = "test-key"
from fastapi.testclient import TestClient
from lab import server

def test_isolated_sessions(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "DB_PATH", str(tmp_path / "test.sqlite3"))
    client = TestClient(server.app)
    h = {"X-Lab-Key": "test-key"}
    ids = [str(uuid.uuid4()), str(uuid.uuid4())]
    for index, aid in enumerate(ids):
        assert client.post("/heartbeat", json={"agent_id": aid, "label": f"Lab {index}"}, headers=h).status_code == 200
        assert client.post("/events", json={"agent_id": aid, "kind": "test", "message": f"event {index}"}, headers=h).status_code == 200
    assert len(client.get("/agents", headers=h).json()) == 2
    for index, aid in enumerate(ids):
        result = client.get(f"/agents/{aid}/events", headers=h).json()
        assert len(result) == 1
        assert result[0]["message"] == f"event {index}"
    assert client.get("/agents").status_code == 401
