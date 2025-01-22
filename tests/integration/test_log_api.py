from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_log_success():
    response = client.post(
        "/log/",
        json={
            "message": "Test log",
            "level": "info",
            "service": "test_service",
            "format": "json",
            "interval": 5,
            "duration": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Recurring log creation started"
    assert data["interval"] == 5
    assert data["duration"] == 30


def test_create_log_missing_message():
    response = client.post("/log/", json={"level": "info"})
    assert response.status_code == 422  # Attendre une erreur de validation


def test_create_log_missing_level():
    response = client.post("/log/", json={"message": "Test log"})
    assert response.status_code == 422  # Attendre une erreur de validation


def test_create_log_invalid_level():
    response = client.post(
        "/log/",
        json={"message": "Test log", "level": "invalid_level"},  # Niveau invalide
    )
    assert response.status_code == 422  # Attendre une erreur de validation


def test_create_log_format_types():
    # Test JSON format
    response = client.post(
        "/log/", json={"message": "Test log", "level": "info", "format": "json"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert "level" in data
    assert "timestamp" in data

    # Test plaintext format
    response = client.post(
        "/log/", json={"message": "Test log", "level": "info", "format": "plaintext"}
    )
    assert response.status_code == 200
    data = response.text  # Utiliser .text au lieu de .json()
    assert isinstance(data, str)
    assert "INFO" in data


def test_create_log_with_interval_and_duration():
    response = client.post(
        "/log/",
        json={
            "message": "Test log",
            "level": "info",
            "service": "test_service",
            "format": "json",
            "interval": 5,
            "duration": 15,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Recurring log creation started"
    assert data["interval"] == 5
    assert data["duration"] == 15
