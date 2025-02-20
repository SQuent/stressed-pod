import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestSystemEndpoints:
    """Integration tests for system endpoints"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_get_system_info(self, client):
        """Test getting system information"""
        response = client.get("/system/")
        assert response.status_code == 200
        data = response.json()

        # Check pod info structure
        assert "pod_info" in data
        pod_info = data["pod_info"]
        expected_fields = ["pod_name", "namespace", "node_name", "host_ip", "pod_ip"]
        for field in expected_fields:
            assert field in pod_info

        # Check probe statuses
        assert "readiness_status" in data
        assert "liveness_status" in data
