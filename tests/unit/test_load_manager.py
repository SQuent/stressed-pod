import os
import pytest
from app.managers.load_manager import LoadManager
import psutil


class TestLoadManager:
    @pytest.fixture
    def load_manager(self):
        """Initialize LoadManager with clean environment"""
        os.environ.update(
            {
                "CPU_REQUESTED": "0",
                "MEMORY_REQUESTED": "0",
                "INITIAL_MEMORY_LOAD": "50",
                "FINAL_MEMORY_LOAD": "100",
                "MEMORY_LOAD_DURATION": "60",
                "STOP_MEMORY_LOAD_AT_END": "true",
                "ENABLE_DYNAMIC_MEMORY_LOAD": "false",
                "ENABLE_DYNAMIC_CPU_LOAD": "false",
                "INITIAL_CPU_LOAD": "0",
                "FINAL_CPU_LOAD": "1",
                "CPU_LOAD_DURATION": "60",
                "STOP_CPU_LOAD_AT_END": "true",
            }
        )
        return LoadManager()

    # 1. Initialization tests
    def test_initialization_with_defaults(self, load_manager):
        """Test initialization with default environment variables"""
        assert load_manager.cpu_requested == 0
        assert load_manager.memory_requested == 0
        assert load_manager.memory_at_start == 50
        assert load_manager.memory_at_end == 100
        assert load_manager.memory_duration == 60
        assert load_manager.stop_memory_at_end is True
        assert load_manager.cpu_at_start == 0
        assert load_manager.cpu_at_end == 1
        assert load_manager.cpu_duration == 60
        assert load_manager.stop_cpu_at_end is True

    def test_initialization_with_env_vars(self, monkeypatch):
        """Test initialization with specific environment variables"""
        monkeypatch.setenv("CPU_REQUESTED", "0.5")
        monkeypatch.setenv("MEMORY_REQUESTED", "40")
        monkeypatch.setenv("ENABLE_DYNAMIC_CPU_LOAD", "false")
        monkeypatch.setenv("ENABLE_DYNAMIC_MEMORY_LOAD", "false")

        manager = LoadManager()
        assert manager.cpu_requested == 0.5
        assert manager.memory_requested == 40

    # 2. CPU methods tests
    def test_add_cpu_load(self, load_manager):
        """Test CPU load setting"""
        value = 0.5
        load_manager.add_cpu_load(value)
        assert load_manager.cpu_requested == value
        assert len(load_manager.cpu_processes) > 0

    def test_add_cpu_load_with_invalid_values(self, load_manager):
        """Test invalid CPU load values"""
        with pytest.raises(ValueError):
            load_manager.add_cpu_load(-1)

    def test_stop_cpu_load(self, load_manager):
        """Test stopping CPU load"""
        load_manager.add_cpu_load(1)
        load_manager.stop_cpu_load()
        assert load_manager.cpu_requested == 0
        assert not load_manager.cpu_processes

    def test_stop_cpu_load_no_processes(self, load_manager):
        """Test stopping CPU load with no active processes"""
        load_manager.stop_cpu_load()
        assert load_manager.cpu_requested == 0
        assert not load_manager.cpu_processes

    def test_dynamic_cpu_load(self, load_manager):
        """Test dynamic CPU load"""
        load_manager.dynamic_cpu_load(0.1, 1, 1, True)
        assert load_manager.cpu_requested >= 0.1
        assert load_manager.cpu_requested <= 1

    def test_dynamic_cpu_load_invalid_duration(self, load_manager):
        """Test invalid duration for dynamic CPU load"""
        # Test with zero duration
        with pytest.raises(ValueError, match="Duration must be between 1 and"):
            load_manager.dynamic_cpu_load(0, 1, 0, False)

        # Test with negative duration
        with pytest.raises(ValueError, match="Duration must be between 1 and"):
            load_manager.dynamic_cpu_load(0, 1, -1, False)

        # Test with excessive duration
        with pytest.raises(ValueError, match="Duration must be between 1 and"):
            load_manager.dynamic_cpu_load(0, 1, 3601, False)

    def test_dynamic_cpu_load_zero_duration(self, load_manager):
        """Test dynamic CPU load with minimum duration"""
        # Changed from 0 to 1 second as minimum duration
        load_manager.dynamic_cpu_load(0, 1, 1, False)
        assert load_manager.cpu_requested >= 0
        assert load_manager.cpu_requested <= 1

    # 3. Memory methods tests
    def test_add_memory_load(self, load_manager):
        """Test memory load setting"""
        value = 100
        load_manager.add_memory_load(value)
        assert load_manager.memory_requested == value
        assert load_manager.memory_process is not None

    def test_add_memory_load_with_invalid_values(self, load_manager):
        """Test invalid memory load values"""
        with pytest.raises(ValueError):
            load_manager.add_memory_load(-1)

    def test_stop_memory_load(self, load_manager):
        """Test stopping memory load"""
        load_manager.add_memory_load(50)
        load_manager.stop_memory_load()
        assert load_manager.memory_requested == 0
        assert load_manager.memory_process is None

    def test_stop_memory_load_no_processes(self, load_manager):
        """Test stopping memory load with no active processes"""
        load_manager.stop_memory_load()
        assert load_manager.memory_requested == 0
        assert load_manager.memory_process is None

    def test_dynamic_memory_load(self, load_manager):
        """Test dynamic memory load"""
        load_manager.dynamic_memory_load(100, 200, 1, False)
        assert load_manager.memory_requested >= 100
        assert load_manager.memory_requested <= 200

    def test_dynamic_memory_load_invalid_duration(self, load_manager):
        """Test invalid duration for dynamic memory load"""
        with pytest.raises(ValueError):
            load_manager.dynamic_memory_load(-1, 200, -1, True)

    def test_dynamic_memory_load_zero_duration(self, load_manager):
        """Test dynamic memory load with minimum duration"""
        # Changed from duration 0 to minimum duration 1
        load_manager.dynamic_memory_load(100, 256, 1, False)
        assert load_manager.memory_requested >= 100
        assert load_manager.memory_requested <= 256

    # 4. Combined and other tests
    def test_stop_all_loads(self, load_manager):
        """Test stopping all loads"""
        load_manager.add_cpu_load(1)
        load_manager.add_memory_load(100)
        load_manager.stop_cpu_load()
        load_manager.stop_memory_load()
        assert load_manager.cpu_requested == 0
        assert load_manager.memory_requested == 0
        assert not load_manager.cpu_processes
        assert load_manager.memory_process is None

    def test_add_cpu_load_script_missing(self, load_manager, monkeypatch):
        """Test failure when cpu_stress.py is missing"""
        def mock_exists(path):
            return False

        monkeypatch.setattr("os.path.exists", mock_exists)
        with pytest.raises(RuntimeError, match="CPU stress script is missing"):
            load_manager.add_cpu_load(0.5)

    def test_add_memory_load_script_missing(self, load_manager, monkeypatch):
        """Test failure when memory_stress.py is missing"""

        def mock_exists(path):
            return False

        monkeypatch.setattr("os.path.exists", mock_exists)
        with pytest.raises(RuntimeError):
            load_manager.add_memory_load(50)

    @pytest.mark.asyncio
    async def test_edge_cases_cpu_load(self, load_manager):
        """Test edge cases for CPU load"""
        # Test with maximum allowed value
        max_cpus = os.cpu_count()
        load_manager.add_cpu_load(max_cpus)
        assert load_manager.cpu_requested == max_cpus

        # Test with value exceeding CPU count
        with pytest.raises(ValueError, match="CPU load cannot exceed"):
            load_manager.add_cpu_load(max_cpus + 1)

        # Test with decimal value close to 0
        load_manager.add_cpu_load(0.01)
        assert load_manager.cpu_requested == 0.01

        # Test with high but valid decimal value
        load_manager.add_cpu_load(0.99)
        assert load_manager.cpu_requested == 0.99

    @pytest.mark.asyncio
    async def test_edge_cases_memory_load(self, load_manager):
        """Test edge cases for memory load"""
        # Test with value close to system memory limit
        total_memory = psutil.virtual_memory().total // (1024 * 1024)  # Convert to MB
        with pytest.raises(ValueError, match="Memory load cannot exceed"):
            load_manager.add_memory_load(total_memory + 100)

        # Test with very small memory value
        load_manager.add_memory_load(1)
        assert load_manager.memory_requested == 1

        # Test with zero value
        with pytest.raises(ValueError, match="Memory load must be greater than 0"):
            load_manager.add_memory_load(0)

    @pytest.mark.asyncio
    async def test_edge_cases_dynamic_load(self, load_manager):
        """Test edge cases for dynamic load changes"""
        # Test with equal start and end values
        load_manager.dynamic_cpu_load(0.5, 0.5, 10, True)
        assert load_manager.cpu_requested == 0.5

        # Test with very short duration
        load_manager.dynamic_memory_load(100, 200, 1, True)
        assert load_manager.memory_requested >= 100
        assert load_manager.memory_requested <= 200

        # Test with reversed values
        with pytest.raises(ValueError, match="End value must be greater than"):
            load_manager.dynamic_cpu_load(0.8, 0.2, 10, True)

        # Test with maximum duration
        with pytest.raises(ValueError, match="Duration must be between 1 and"):
            load_manager.dynamic_memory_load(100, 200, 3601, True)  # Duration exceeds max_duration
