"""FastAPI routes for the ThermoLab temperature simulator."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import CompareRequest, CompareResponse, SimulationRequest, SimulationResponse
from backend.services import compare_simulations, run_simulation


app = FastAPI(
    title="ThermoLab API",
    description="Educational API for Newton's law of cooling and heating.",
    version="1.1.0",
)

default_origins = "http://localhost:8501,http://127.0.0.1:8501"
allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", default_origins).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def root():
    """Return basic API information and useful documentation links."""
    return {
        "name": "ThermoLab API",
        "description": "Newton's law of cooling and heating simulation service.",
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
        "endpoints": ["/simulate", "/compare"],
    }


@app.get("/health")
def health():
    """Report that the API process is responsive."""
    return {"status": "healthy", "service": "thermolab-api"}


@app.post("/simulate", response_model=SimulationResponse)
def simulate(request: SimulationRequest):
    """Calculate one temperature time series."""
    return run_simulation(request)


@app.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest):
    """Calculate several scenarios for side-by-side comparison."""
    return compare_simulations(request.scenarios)
