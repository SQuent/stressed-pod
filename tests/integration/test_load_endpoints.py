import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestLoadEndpoints:
    """Integration tests for load endpoints"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_cpu_load_endpoints(self, client):
        """Test CPU load endpoints"""
        # Test start CPU load
        response = client.post("/load/cpu/start", json={"value": 30})
        assert response.status_code == 200

        # Test stop CPU load
        response = client.post("/load/cpu/stop")
        assert response.status_code == 200

    def test_memory_load_endpoints(self, client):
        """Test memory load endpoints"""
        # Test start memory load
        response = client.post("/load/memory/start", json={"value": 50})
        assert response.status_code == 200

        # Test stop memory load
        response = client.post("/load/memory/stop")
        assert response.status_code == 200

    def test_dynamic_load_endpoints(self, client):
        """Test dynamic load endpoints"""
        # Test dynamic CPU load
        cpu_response = client.post(
            "/load/cpu/dynamic",
            json={
                "start_value": 10,
                "end_value": 20,
                "duration": 60,
                "stop_at_end": True,
            },
        )
        assert cpu_response.status_code == 200
        assert "message" in cpu_response.json()

        # Test dynamic memory load
        memory_response = client.post(
            "/load/memory/dynamic",
            json={
                "start_value": 100,
                "end_value": 200,
                "duration": 60,
                "stop_at_end": True,
            },
        )
        assert memory_response.status_code == 200
        assert "message" in memory_response.json()

        # Test get load status after starting dynamic loads
        status_response = client.get("/load")
        assert status_response.status_code == 200
        load_status = status_response.json()
        assert "cpu_requested" in load_status
        assert "memory_requested" in load_status
        assert "cpu_active" in load_status
        assert "memory_active" in load_status

    def test_get_current_load(self, client):
        """Test get current load endpoint"""
        response = client.get("/load")
        assert response.status_code == 200
        data = response.json()
        assert all(
            key in data
            for key in [
                "cpu_requested",
                "memory_requested",
                "cpu_active",
                "memory_active",
            ]
        )
