from .load import router as load_router
from .probes import router as probes_router
from .system import router as system_router

# This makes imports cleaner in main.py
__all__ = ["load_router", "probes_router", "system_router"]
