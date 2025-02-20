import os
import signal
import subprocess
from threading import Timer
import psutil


class LoadManager:
    def __init__(self):
        self.cpu_script_path = os.path.join(os.getcwd(), "app/scripts/cpu_stress.py")
        self.memory_script_path = os.path.join(
            os.getcwd(), "app/scripts/memory_stress.py"
        )

        self.cpu_requested = float(os.getenv("CPU_REQUESTED", 0))
        self.memory_requested = int(os.getenv("MEMORY_REQUESTED", 0))
        self.cpu_processes = []
        self.cpu_timers = []
        self.memory_timers = []
        self.memory_process = None

        self.memory_at_start = int(os.getenv("INITIAL_MEMORY_LOAD", 50))
        self.memory_at_end = int(os.getenv("FINAL_MEMORY_LOAD", 256))
        self.memory_duration = int(os.getenv("MEMORY_LOAD_DURATION", 60))
        self.stop_memory_at_end = os.getenv("STOP_MEMORY_LOAD_AT_END", "true") == "true"

        self.cpu_at_start = float(os.getenv("INITIAL_CPU_LOAD", 0))
        self.cpu_at_end = float(os.getenv("FINAL_CPU_LOAD", 1))
        self.cpu_duration = int(os.getenv("CPU_LOAD_DURATION", 60))
        self.stop_cpu_at_end = os.getenv("STOP_CPU_LOAD_AT_END", "true") == "true"

        self.max_duration = 3600
        self.system_memory = psutil.virtual_memory().total // (1024 * 1024)
        self.system_cpus = os.cpu_count()

        if os.getenv("ENABLE_DYNAMIC_MEMORY_LOAD", "false") == "true":
            self.dynamic_memory_load(
                self.memory_at_start,
                self.memory_at_end,
                self.memory_duration,
                self.stop_memory_at_end,
            )

        if os.getenv("ENABLE_DYNAMIC_CPU_LOAD", "false") == "true":
            self.dynamic_cpu_load(
                self.cpu_at_start,
                self.cpu_at_end,
                self.cpu_duration,
                self.stop_cpu_at_end,
            )

    def __del__(self):
        self.stop_cpu_load()
        self.stop_memory_load()

    def stop_cpu_load(self):
        for process in self.cpu_processes:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait()
            except Exception as e:
                raise RuntimeError(f"Failed to terminate process {process.pid}: {e}")
        self.cpu_processes.clear()
        for timer in self.cpu_timers:
            timer.cancel()
        self.cpu_timers.clear()
        self.cpu_requested = 0

    def add_cpu_load(self, value: float):
        """Add CPU load with validation"""
        if value <= 0:
            raise ValueError("CPU load must be greater than 0")
        if value > self.system_cpus:
            raise ValueError(
                f"CPU load cannot exceed system CPU count ({self.system_cpus})"
            )

        if not os.path.exists(self.cpu_script_path):
            raise RuntimeError("CPU stress script is missing")

        self.stop_cpu_load()
        command = ["python3", self.cpu_script_path, str(value)]
        try:
            process = subprocess.Popen(command, preexec_fn=os.setsid)
            self.cpu_processes.append(process)
            self.cpu_requested = value
        except Exception as e:
            raise RuntimeError(f"Failed to start CPU stress: {e}")

    def stop_memory_load(self):
        if self.memory_process:
            try:
                self.memory_process.terminate()
                self.memory_process = None

                for timer in self.memory_timers:
                    timer.cancel()
                self.memory_timers.clear()
                self.memory_requested = 0
            except Exception as e:
                raise RuntimeError(f"Failed to terminate memory stress: {e}")

    def add_memory_load(self, value: int):
        """Add memory load with validation"""
        if value <= 0:
            raise ValueError("Memory load must be greater than 0")
        if value > self.system_memory:
            raise ValueError(
                f"Memory load cannot exceed system memory ({self.system_memory}MB)"
            )

        if not os.path.exists(self.memory_script_path):
            raise RuntimeError("Memory stress script is missing")

        self.stop_memory_load()
        command = ["python3", self.memory_script_path, str(value)]
        try:
            self.memory_process = subprocess.Popen(command)
            self.memory_requested = value
        except Exception as e:
            raise RuntimeError(f"Failed to start memory stress: {e}")

    def dynamic_memory_load(
        self, start_value: int, end_value: int, duration: int, stop_at_end: bool = False
    ):
        """Dynamic memory load with validation"""
        if duration <= 0 or duration > self.max_duration:
            raise ValueError(
                f"Duration must be between 1 and {self.max_duration} seconds"
            )
        if end_value < start_value:
            raise ValueError("End value must be greater than start value")

        try:
            start_value = start_value
            end_value = end_value
            duration = duration
        except ValueError as e:
            raise ValueError(
                "Arguments 'start_value', 'end_value', 'duration' have to be integers."
            ) from e
        num_intervals = duration // 10

        if num_intervals < 1:
            num_intervals = 1
        increment = (end_value - start_value) / num_intervals
        global memory_requested
        memory_requested = start_value

        def apply_dynamic_memory_load(interval_num):
            global memory_requested
            current_memory = min(
                start_value + increment * (interval_num + 1), end_value
            )
            self.add_memory_load(int(current_memory))

            if interval_num + 1 < num_intervals:
                timer = Timer(10, apply_dynamic_memory_load, [interval_num + 1])
                self.memory_timers.append(timer)
                timer.start()
            elif stop_at_end:
                stop_timer = Timer(10, self.stop_memory_load)
                stop_timer.start()

        apply_dynamic_memory_load(0)

    def dynamic_cpu_load(
        self,
        start_value: float,
        end_value: float,
        duration: int,
        stop_at_end: bool = False,
    ):
        """Dynamic CPU load with validation"""
        if duration <= 0 or duration > self.max_duration:
            raise ValueError(
                f"Duration must be between 1 and {self.max_duration} seconds"
            )
        if end_value < start_value:
            raise ValueError("End value must be greater than start value")

        try:
            start_value = start_value
            end_value = end_value
            duration = duration
        except ValueError as e:
            raise ValueError(
                "Arguments 'start_value', 'end_value', 'duration'have to be integers."
            ) from e

        num_intervals = duration // 10

        if num_intervals < 1:
            num_intervals = 1
        increment = (end_value - start_value) / num_intervals
        global cpu_requested
        cpu_requested = start_value

        def apply_dynamic_cpu_load(interval_num):
            global cpu_requested
            current_cpu = min(start_value + increment * (interval_num + 1), end_value)
            self.add_cpu_load(current_cpu)

            if interval_num + 1 < num_intervals:
                timer = Timer(10, apply_dynamic_cpu_load, [interval_num + 1])
                self.cpu_timers.append(timer)
                timer.start()

            elif stop_at_end:
                stop_timer = Timer(10, self.stop_cpu_load)
                stop_timer.start()

        apply_dynamic_cpu_load(0)
