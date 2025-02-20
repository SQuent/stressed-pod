from fastapi import FastAPI
from .routers import load_router, probes_router, system_router, log_router

app = FastAPI(
    title="Stressed API",
    description="simulates controlled workloads and failures to stress-test a system",
    version="1.0.0",
)


app.include_router(system_router)
app.include_router(load_router)
app.include_router(probes_router)
app.include_router(log_router.router)
