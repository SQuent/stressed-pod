from fastapi import APIRouter, HTTPException
from ..models.schemas import TerminateRequest
from ..managers.lifecycle_manager import LifecycleManager
import os

router = APIRouter(tags=["System"])
lifecycle_manager = LifecycleManager()


@router.get("/")
async def get_pod_info():
    """Get pod information and probe statuses"""
    return {
        "pod_info": {
            "pod_name": os.getenv("POD_NAME", "unknown"),
            "namespace": os.getenv("POD_NAMESPACE", "unknown"),
            "node_name": os.getenv("NODE_NAME", "unknown"),
            "host_ip": os.getenv("HOST_IP", "unknown"),
            "pod_ip": os.getenv("POD_IP", "unknown"),
        },
        "readiness_status": lifecycle_manager.readiness_status,
        "liveness_status": lifecycle_manager.liveness_status,
    }


@router.post("/terminate")
async def terminate_app(request: TerminateRequest):
    """Terminate the application"""
    try:
        lifecycle_manager.terminate_app(request.seconds)
        return {"message": f"Application will terminate in {request.seconds} seconds."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
