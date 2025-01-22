from fastapi import APIRouter
from app.models.schemas import LogRequest
from app.managers.log_manager import LogManager

router = APIRouter()
log_manager = LogManager()


@router.post("/log/")
async def create_log(log_data: LogRequest):
    """Create Log"""
    return await log_manager.create_log(log_data)
