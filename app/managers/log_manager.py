import logging
import json
from datetime import datetime, UTC
from ..models.schemas import LogRequest, LogFormat
import asyncio
import time


class JsonFormatter(logging.Formatter):
    """Formatter personnalisé pour les logs JSON"""

    def format(self, record):
        return json.dumps(
            {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "service": getattr(record, "service", "-"),
                "message": record.getMessage(),
            }
        )


class PlainTextFormatter(logging.Formatter):
    """Formatter personnalisé pour le texte plat"""

    def format(self, record):
        return f"{self.formatTime(record)} | {record.levelname} | {getattr(record, 'service', '-')} | {record.getMessage()}"


class LogManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.text_formatter = PlainTextFormatter()
        self.json_formatter = JsonFormatter()

        self._setup_handler(LogFormat.JSON)

        self.current_format = LogFormat.JSON

    def _setup_handler(self, format_type: LogFormat):
        """Configure un nouveau handler avec le format spécifié"""
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.DEBUG)

        formatter = (
            self.json_formatter
            if format_type == LogFormat.JSON
            else self.text_formatter
        )
        self.handler.setFormatter(formatter)

        self.logger.addHandler(self.handler)

    def _validate_interval_duration(self, interval: int | None, duration: int | None):
        """check parameters"""
        if interval is not None and duration is None:
            raise ValueError("Duration must be set when interval is provided")

        if duration is not None and interval is None:
            raise ValueError("Interval must be set when duration is provided")

        if interval is not None and interval < 1:
            raise ValueError("Interval must be greater than 0")

        if duration is not None and duration < 1:
            raise ValueError("Duration must be greater than 0")

        if interval and duration and interval > duration:
            raise ValueError("Interval cannot be greater than duration")

    async def create_log(self, log_data: LogRequest) -> dict | str:
        """Create log"""
        level = getattr(logging, log_data.level.upper())

        self._validate_interval_duration(log_data.interval, log_data.duration)

        if log_data.interval and log_data.duration:
            asyncio.create_task(
                self._create_recurring_logs(
                    log_data, log_data.interval, log_data.duration
                )
            )
            return {
                "message": "Recurring log creation started",
                "interval": log_data.interval,
                "duration": log_data.duration,
            }

        return await self._create_single_log(log_data, level)

    async def _create_recurring_logs(
        self, log_data: LogRequest, interval: int, duration: int
    ):
        """Crée des logs de manière récurrente"""
        end_time = time.time() + duration
        while time.time() < end_time:
            await self._create_single_log(
                log_data, getattr(logging, log_data.level.upper())
            )
            await asyncio.sleep(interval)

    async def _create_single_log(self, log_data: LogRequest, level: int) -> dict | str:
        """Crée un seul log"""
        try:
            timestamp = datetime.now(UTC).isoformat()

            if log_data.format != self.current_format:
                self._setup_handler(log_data.format)
                self.current_format = log_data.format

            self.logger.log(
                level,
                log_data.message,
                extra={"service": log_data.service or "-", "timestamp": timestamp},
            )

            if log_data.format == LogFormat.PLAINTEXT:
                service_part = log_data.service if log_data.service else "-"
                return f"{timestamp} | {log_data.level.upper()} | {service_part} | {log_data.message}"

            return {
                "message": log_data.message,
                "level": log_data.level,
                "timestamp": timestamp,
                "service": log_data.service,
            }
        except Exception as e:
            return f"Error creating log: {e}"

    def _validate_log_level(self, level: str) -> bool:
        """Validate if the log level is correct"""
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        return level.lower() in valid_levels

    async def log_creator(self, log_data: LogRequest, interval: int, duration: int):
        """Ffunction to create multiple log log"""
        end_time = time.time() + duration
        while time.time() < end_time:
            await self.create_log(log_data)
            await asyncio.sleep(interval)
