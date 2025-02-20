import psutil
from datetime import datetime, timedelta
import os


class SystemManager:
    def __init__(self):
        if os.getenv("ENABLE_AUTO_TERMINATION", "false").lower() == "true":
            delay = int(os.getenv("AUTO_TERMINATION_DELAY", "300"))
            self.terminate(delay)

    def get_system_info(self):
        """Get system information"""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
        }

    async def terminate(self, request):
        """Schedule system termination"""
        termination_time = datetime.now() + timedelta(seconds=request.seconds)

        return {"status": "scheduled", "termination_time": termination_time.isoformat()}
