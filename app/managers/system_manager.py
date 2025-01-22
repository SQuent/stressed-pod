import psutil
from datetime import datetime, timedelta


class SystemManager:
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
