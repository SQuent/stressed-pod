import os


class LifecycleManager:
    def __init__(self):
        self.readiness_status = os.getenv("READINESS_STATUS", "SUCCESS")
        self.liveness_status = os.getenv("LIVENESS_STATUS", "SUCCESS")

    def set_probe_status(self, probe, status):
        if probe == "readiness":
            self.readiness_status = status
        elif probe == "liveness":
            self.liveness_status = status
        else:
            raise ValueError("Invalid probe")
