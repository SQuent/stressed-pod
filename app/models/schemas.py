from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DynamicLoadRequest(BaseModel):
    start_value: int = Field(..., ge=0, description="Starting load")
    end_value: int = Field(..., ge=0, description="Ending load")
    duration: int = Field(1, ge=1, description="Duration in secondes")
    stop_at_end: bool = Field(
        False, description="Whether to stop load after completion"
    )


class LoadRequest(BaseModel):
    value: int = Field(..., ge=0, description="Load value (CPU cores or MB of memory)")


class ProbeRequest(BaseModel):
    probe: str = Field(..., pattern="^(readiness|liveness)$")
    status: str = Field(..., pattern="^(ok|error)$")


class TerminateRequest(BaseModel):
    seconds: int = Field(0, ge=0, description="Delay before termination in seconds")


# Nouveaux schémas pour les logs
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
    """Schéma de requête pour la création de logs"""

    message: str = Field(..., description="Message de log")
    level: LogLevel = Field(..., description="Niveau de log")
    service: str | None = Field(None, description="Nom du service (optionnel)")
    format: LogFormat = Field(default=LogFormat.JSON, description="Format de sortie")
    interval: int | None = Field(
        None, description="Intervalle entre chaque log en secondes (optionnel)"
    )
    duration: int | None = Field(
        None, description="Durée d'envoi des logs en secondes (optionnel)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Test log message",
                "level": "info",
                "service": "my-service",  # optionnel
                "format": "json",  # optionnel, défaut: "json"
                "interval": 5,  # optionnel
                "duration": 60,  # optionnel
            }
        }
