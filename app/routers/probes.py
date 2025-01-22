from fastapi import APIRouter, HTTPException
from ..models.schemas import ProbeRequest
from ..managers.lifecycle_manager import LifecycleManager

router = APIRouter(prefix="/probes", tags=["Health Probes"])
lifecycle_manager = LifecycleManager()


@router.get("")
async def get_probe_statuses():
    """Get all probe statuses"""
    return {
        "readiness_status": lifecycle_manager.readiness_status,
        "liveness_status": lifecycle_manager.liveness_status,
    }


@router.get("/readiness")
async def readiness_probe():
    """Get readiness probe status"""
    return lifecycle_manager.readiness_status


@router.get("/liveness")
async def liveness_probe():
    """Get liveness probe status"""
    return lifecycle_manager.liveness_status


@router.post("/status")
async def set_probe_status(request: ProbeRequest):
    """Set probe status"""
    try:
        lifecycle_manager.set_probe_status(request.probe, request.status)
        return {"message": f"{request.probe} set to {request.status}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
