from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_pod_info():
    """Test the root endpoint that returns pod info"""
    response = client.get("/system/")
    assert response.status_code == 200
    data = response.json()
    assert "pod_info" in data
    assert "readiness_status" in data
    assert "liveness_status" in data


def test_probe_endpoints():
    """Test all probe-related endpoints"""
    # Test get all probe statuses
    response = client.get("/probes")
    assert response.status_code == 200
    data = response.json()
    assert "readiness_status" in data
    assert "liveness_status" in data

    # Test individual probe endpoints
    response = client.get("/probes/readiness")
    assert response.status_code == 200

    response = client.get("/probes/liveness")
    assert response.status_code == 200

    # Test setting probe status
    response = client.post(
        "/probes/status", json={"probe": "readiness", "status": "ok"}
    )
    assert response.status_code == 200


def test_load_endpoints():
    """Test all load-related endpoints"""
    # Test get current load
    response = client.get("/load")
    assert response.status_code == 200
    data = response.json()
    assert all(
        key in data
        for key in ["cpu_requested", "memory_requested", "cpu_active", "memory_active"]
    )

    # Test CPU operations
    response = client.post(
        "/load/cpu/dynamic",
        json={
            "start_value": 0.1,
            "end_value": 0.3,
            "duration": 20,
            "stop_at_end": True,
        },
    )
    assert response.status_code == 200

    response = client.post("/load/cpu/start", json={"value": 0.5})
    assert response.status_code == 200

    response = client.post("/load/cpu/stop")
    assert response.status_code == 200

    # Test Memory operations
    response = client.post(
        "/load/memory/dynamic",
        json={
            "start_value": 100,
            "end_value": 256,
            "duration": 20,
            "stop_at_end": True,
        },
    )
    assert response.status_code == 200

    response = client.post("/load/memory/start", json={"value": 100})
    assert response.status_code == 200

    response = client.post("/load/memory/stop")
    assert response.status_code == 200
