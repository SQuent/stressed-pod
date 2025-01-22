import pytest
import logging
from datetime import datetime, UTC
from app.managers.log_manager import LogManager, JsonFormatter, PlainTextFormatter
from app.models.schemas import LogRequest, LogFormat


class TestLogManager:
    @pytest.fixture
    def log_manager(self):
        """Fixture pour initialiser LogManager"""
        return LogManager()

    # 1. Tests des formatters
    def test_json_formatter(self):
        """Test du formatter JSON"""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=None,
            exc_info=None,
        )
        record.service = "TestService"
        result = formatter.format(record)
        assert '"level": "INFO"' in result
        assert '"service": "TestService"' in result
        assert '"message": "Test message"' in result

    def test_plain_text_formatter(self):
        """Test du formatter en texte brut"""
        formatter = PlainTextFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=None,
            exc_info=None,
        )
        record.service = "TestService"
        result = formatter.format(record)
        assert "| INFO | TestService | Test message" in result

    # 2. Tests d'initialisation
    def test_log_manager_initialization(self, log_manager):
        """Test de l'initialisation de LogManager"""
        assert log_manager.logger.name == "app.managers.log_manager"
        assert log_manager.logger.level == logging.DEBUG
        assert log_manager.current_format == LogFormat.JSON
        assert isinstance(log_manager.json_formatter, JsonFormatter)
        assert isinstance(log_manager.text_formatter, PlainTextFormatter)

    def test_initial_handler_setup(self, log_manager):
        """Test de la configuration initiale du handler"""
        assert len(log_manager.logger.handlers) == 1
        assert isinstance(log_manager.logger.handlers[0].formatter, JsonFormatter)

    # 3. Tests de création de logs
    @pytest.mark.asyncio
    async def test_create_log_json_format(self, log_manager):
        """Test de création de log au format JSON"""
        log_data = LogRequest(
            message="Test log",
            level="info",
            format=LogFormat.JSON,
            service="TestService",
        )
        result = await log_manager.create_log(log_data)
        assert result["message"] == "Test log"
        assert result["level"] == "info"
        assert "timestamp" in result
        assert result["service"] == "TestService"

    @pytest.mark.asyncio
    async def test_create_log_plaintext_format(self, log_manager):
        """Test de création de log au format texte brut"""
        log_data = LogRequest(
            message="Test log",
            level="info",
            format=LogFormat.PLAINTEXT,
            service="TestService",
        )
        result = await log_manager.create_log(log_data)
        assert "| INFO | TestService | Test log" in result

    @pytest.mark.asyncio
    async def test_invalid_log_level(self, log_manager):
        """Test invalid log level"""
        with pytest.raises(ValueError):
            log_data = LogRequest(message="Test log", level="invalid_level")
            await log_manager.create_log(log_data)

    # 4. Tests de changement de format
    @pytest.mark.asyncio
    async def test_format_switching(self, log_manager):
        """Test de basculement entre les formats JSON et texte brut"""
        json_log = LogRequest(
            message="JSON format log",
            level="info",
            format=LogFormat.JSON,
            service="TestService",
        )
        plaintext_log = LogRequest(
            message="Plaintext format log",
            level="info",
            format=LogFormat.PLAINTEXT,
            service="TestService",
        )

        result_json = await log_manager.create_log(json_log)
        assert result_json["message"] == "JSON format log"

        result_plaintext = await log_manager.create_log(plaintext_log)
        assert "| INFO | TestService | Plaintext format log" in result_plaintext

    # 5. Tests de log récurrents
    @pytest.mark.asyncio
    async def test_log_creator(self, log_manager):
        """Test de création de logs récurrents"""
        log_data = LogRequest(
            message="Recurring log",
            level="info",
            format=LogFormat.JSON,
            service="TestService",
        )
        interval = 1
        duration = 3

        start_time = datetime.now(UTC)
        await log_manager.log_creator(log_data, interval, duration)
        end_time = datetime.now(UTC)

        assert (end_time - start_time).total_seconds() >= duration

    # 6. Tests de validation des niveaux de log
    def test_validate_log_level(self, log_manager):
        """Test de validation des niveaux de log"""
        assert log_manager._validate_log_level("info")
        assert not log_manager._validate_log_level("invalid_level")

    @pytest.mark.asyncio
    async def test_recurring_logs_validation(self, log_manager):
        """Test la validation des paramètres de logs récurrents"""
        # Test interval sans duration
        with pytest.raises(ValueError, match="Duration must be set"):
            log_data = LogRequest(message="Test log", level="info", interval=5)
            await log_manager.create_log(log_data)

        # Test duration sans interval
        with pytest.raises(ValueError, match="Interval must be set"):
            log_data = LogRequest(message="Test log", level="info", duration=30)
            await log_manager.create_log(log_data)

        # Test interval négatif
        with pytest.raises(ValueError, match="Interval must be greater"):
            log_data = LogRequest(
                message="Test log", level="info", interval=-1, duration=30
            )
            await log_manager.create_log(log_data)

        # Test duration négative
        with pytest.raises(ValueError, match="Duration must be greater"):
            log_data = LogRequest(
                message="Test log", level="info", interval=5, duration=-1
            )
            await log_manager.create_log(log_data)

        # Test interval > duration
        with pytest.raises(ValueError, match="Interval cannot be greater"):
            log_data = LogRequest(
                message="Test log", level="info", interval=10, duration=5
            )
            await log_manager.create_log(log_data)

    @pytest.mark.asyncio
    async def test_recurring_logs(self, log_manager):
        """Test la création de logs récurrents"""
        log_data = LogRequest(
            message="Test recurring log", level="info", interval=1, duration=3
        )

        result = await log_manager.create_log(log_data)
        assert result["message"] == "Recurring log creation started"
        assert result["interval"] == 1
        assert result["duration"] == 3
