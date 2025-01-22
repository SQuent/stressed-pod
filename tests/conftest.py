import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import signal
import psutil


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def load_manager():
    from app.managers.load_manager import LoadManager

    return LoadManager()


@pytest.fixture
def log_manager():
    from app.managers.log_manager import LogManager

    return LogManager()


def kill_stress_processes():
    """Kill all stress test processes"""
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # Chercher les processus python qui exécutent cpu_stress.py ou memory_stress.py
            if proc.info["cmdline"] and "python" in proc.info["cmdline"][0]:
                cmdline = " ".join(proc.info["cmdline"])
                if "cpu_stress.py" in cmdline or "memory_stress.py" in cmdline:
                    print(f"Killing process {proc.info['pid']}: {cmdline}")
                    os.kill(proc.info["pid"], signal.SIGTERM)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Fixture pour nettoyer après chaque test"""
    yield
    kill_stress_processes()
