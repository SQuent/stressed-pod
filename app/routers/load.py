from fastapi import APIRouter, HTTPException
from ..models.schemas import DynamicLoadRequest, LoadRequest
from ..managers.load_manager import LoadManager

router = APIRouter(prefix="/load", tags=["Load Management"])
load_manager = LoadManager()


@router.post("/cpu/dynamic")
async def start_dynamic_cpu_load(request: DynamicLoadRequest):
    """Start a progressive CPU load"""
    try:
        load_manager.dynamic_cpu_load(
            request.start_value,
            request.end_value,
            request.duration,
            request.stop_at_end,
        )
        return {
            "message": f"Progressive CPU load started: {request.start_value}-{request.end_value} over {request.duration} secondes."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cpu/start")
async def add_cpu_load(request: LoadRequest):
    """Add CPU load"""
    try:
        load_manager.add_cpu_load(request.value)
        return {"message": f"CPU load added: {request.value} CPUs"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cpu/stop")
async def stop_cpu_load():
    """Stop CPU load"""
    try:
        load_manager.stop_cpu_load()
        return {"message": "CPU load stopped"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/dynamic")
async def start_dynamic_memory_load(request: DynamicLoadRequest):
    """Start a progressive memory load"""
    try:
        load_manager.dynamic_memory_load(
            request.start_value,
            request.end_value,
            request.duration,
            request.stop_at_end,
        )
        return {
            "message": f"Progressive memory load started: {request.start_value}-{request.end_value} over {request.duration} secondes."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/start")
async def add_memory_load(request: LoadRequest):
    """Add memory load"""
    try:
        load_manager.add_memory_load(request.value)
        return {"message": f"Memory load added: {request.value} MB"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/stop")
async def stop_memory_load():
    """Stop memory load"""
    try:
        load_manager.stop_memory_load()
        return {"message": "Memory load stopped"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_current_load():
    """Get current CPU and memory load"""
    return {
        "cpu_requested": load_manager.cpu_requested,
        "memory_requested": load_manager.memory_requested,
        "cpu_active": bool(load_manager.cpu_processes),
        "memory_active": load_manager.memory_process is not None,
    }
