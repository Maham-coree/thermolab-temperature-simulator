"""Application services shared by the API endpoints."""

from backend.math_engine import simulate
from backend.schemas import SimulationRequest


def run_simulation(request: SimulationRequest) -> dict:
    """Translate a validated API request into a mathematical result."""
    return simulate(
        initial_temp=request.initial_temp,
        ambient_temp=request.ambient_temp,
        k=request.k,
        duration=request.duration,
        points=request.points,
        time_unit=request.time_unit,
    )


def compare_simulations(scenarios: list[SimulationRequest]) -> dict:
    """Calculate a collection of independently configured scenarios."""
    return {"results": [run_simulation(scenario) for scenario in scenarios]}
