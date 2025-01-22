import pytest
from app.managers.system_manager import SystemManager
from app.models.schemas import TerminateRequest


class TestSystemManager:
    """Unit tests for SystemManager"""

    @pytest.fixture
    def system_manager(self):
        return SystemManager()

    def test_get_system_info(self, system_manager):
        """Test system information retrieval"""
        info = system_manager.get_system_info()

        # Verify system info structure
        assert "cpu_count" in info
        assert "memory_total" in info
        assert "memory_available" in info
        assert isinstance(info["cpu_count"], int)
        assert info["cpu_count"] > 0

    @pytest.mark.asyncio
    async def test_terminate_system(self, system_manager):
        """Test system termination request"""
        request = TerminateRequest(seconds=0)
        result = await system_manager.terminate(request)

        assert result["status"] == "scheduled"
        assert "termination_time" in result
