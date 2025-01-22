import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestProbeEndpoints:
    """Integration tests for probe endpoints"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_probe_endpoints(self, client):
        """Test probe endpoints"""
        # Test get all probe statuses
        status_response = client.get("/probes")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "readiness_status" in status_data
        assert "liveness_status" in status_data

        # Test individual probe endpoints
        readiness_response = client.get("/probes/readiness")
        assert readiness_response.status_code == 200

        liveness_response = client.get("/probes/liveness")
        assert liveness_response.status_code == 200

        # Test setting probe status
        set_status_response = client.post(
            "/probes/status", json={"probe": "readiness", "status": "ok"}
        )
        assert set_status_response.status_code == 200
        assert "message" in set_status_response.json()

        # Verify the status was updated
        updated_status = client.get("/probes/readiness")
        assert updated_status.status_code == 200
        assert updated_status.json() == "ok"
