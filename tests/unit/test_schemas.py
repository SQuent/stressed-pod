import pytest
from pydantic import ValidationError
from app.models.schemas import LogRequest, LogResponse, LogFormat


class TestSchemas:
    def test_log_request_validation(self):
        """Tests de validation du schéma LogRequest"""
        # Test création valide
        log_request = LogRequest(message="Test message", level="info")
        assert log_request.message == "Test message"
        assert log_request.level == "info"
        assert log_request.format == LogFormat.JSON  # Valeur par défaut

        # Test avec format plaintext
        log_request = LogRequest(
            message="Test message", level="info", format=LogFormat.PLAINTEXT
        )
        assert log_request.format == LogFormat.PLAINTEXT

        # Test avec service
        log_request = LogRequest(
            message="Test message", level="info", service="test-service"
        )
        assert log_request.service == "test-service"

        # Test message manquant
        with pytest.raises(ValidationError):
            LogRequest(level="info")

        # Test niveau manquant
        with pytest.raises(ValidationError):
            LogRequest(message="Test message")

    def test_log_response_validation(self):
        """Tests de validation du schéma LogResponse"""
        # Test création valide
        response = LogResponse(status_code=500, detail="Error message")
        assert response.status_code == 500
        assert response.detail == "Error message"
        assert response.trace_id is None

        # Test avec trace_id
        response = LogResponse(status_code=404, detail="Not found", trace_id="abc-123")
        assert response.trace_id == "abc-123"

        # Test status_code manquant
        with pytest.raises(ValidationError):
            LogResponse(detail="Error")

        # Test detail manquant
        with pytest.raises(ValidationError):
            LogResponse(status_code=500)
