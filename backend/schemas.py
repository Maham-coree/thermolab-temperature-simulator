"""Pydantic request and response models for the simulation API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SimulationRequest(BaseModel):
    """A Newton cooling/heating simulation configuration."""

    model_config = ConfigDict(extra="forbid")

    initial_temp: float = Field(
        ge=-273.15, le=10000, allow_inf_nan=False,
        description="Initial object temperature in degrees Celsius.",
    )
    ambient_temp: float = Field(
        ge=-273.15, le=10000, allow_inf_nan=False,
        description="Constant surrounding temperature in degrees Celsius.",
    )
    k: float = Field(
        gt=0, le=10, allow_inf_nan=False,
        description="Positive rate constant per selected time unit.",
    )
    duration: float = Field(
        gt=0, le=100000, allow_inf_nan=False,
        description="Positive simulation duration in the selected time unit.",
    )
    points: int = Field(default=121, ge=2, le=1001)
    time_unit: Literal["seconds", "minutes", "hours"] = "minutes"


class SimulationResponse(BaseModel):
    """Calculated series and summary values for one scenario."""

    mode: Literal["cooling", "heating", "equilibrium"]
    time: list[float]
    temperature: list[float]
    rate_of_change: list[float]
    temperature_difference: list[float]
    initial_temperature: float
    ambient_temperature: float
    final_temperature: float
    initial_temperature_difference: float
    initial_rate: float
    final_rate: float
    cooling_constant: float
    duration: float
    time_unit: Literal["seconds", "minutes", "hours"]


class CompareRequest(BaseModel):
    """A bounded collection of scenarios to compare."""

    model_config = ConfigDict(extra="forbid")

    scenarios: list[SimulationRequest] = Field(min_length=2, max_length=10)


class CompareResponse(BaseModel):
    """Simulation results corresponding to the submitted scenarios."""

    results: list[SimulationResponse]
