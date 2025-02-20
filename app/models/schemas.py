from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DynamicCPULoadRequest(BaseModel):
    start_value: float = Field(..., ge=0, description="Starting load")
    end_value: float = Field(..., ge=0, description="Ending load")
    duration: int = Field(1, ge=1, description="Duration in secondes")
    stop_at_end: bool = Field(
        False, description="Whether to stop load after completion"
    )


class DynamicMemoryLoadRequest(BaseModel):
    start_value: int = Field(..., ge=0, description="Starting load")
    end_value: int = Field(..., ge=0, description="Ending load")
    duration: int = Field(1, ge=1, description="Duration in secondes")
    stop_at_end: bool = Field(
        False, description="Whether to stop load after completion"
    )


class LoadRequest(BaseModel):
    value: float = Field(
        ..., ge=0, description="Load value (CPU cores or MB of memory)"
    )


class ProbeRequest(BaseModel):
    probe: str = Field(..., pattern="^(readiness|liveness)$")
    status: str = Field(..., pattern="^(ok|error)$")


class TerminateRequest(BaseModel):
    seconds: int = Field(0, ge=0, description="Delay before termination in seconds")


class LogResponse(BaseModel):
    status_code: int = Field(..., description="Code HTTP de la réponse")
    detail: str = Field(..., description="Description détaillée de l'erreur")
    trace_id: Optional[str] = Field(None, description="Identifiant unique de la trace")


class LogLevel(str, Enum):
    """Niveaux de log valides"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogFormat(str, Enum):
    """Format options for log output"""

    JSON = "json"
    PLAINTEXT = "plaintext"


class LogRequest(BaseModel):
    """Request schema for log creation"""

    message: str = Field(..., description="Log message")
    level: LogLevel = Field(..., description="Log level")
    service: str | None = Field(None, description="Service name (optional)")
    format: LogFormat = Field(default=LogFormat.JSON, description="Output format")
    interval: int | None = Field(
        None, description="Interval between each log in seconds (optional)"
    )
    duration: int | None = Field(
        None, description="Log sending duration in seconds (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Test log message",
                "level": "info",
                "service": "my-service",
                "format": "json",
                "interval": 5,
                "duration": 60,
            }
        }
