"""Numerical implementation of Newton's law of cooling and heating."""

from __future__ import annotations

import math
from numbers import Integral, Real
from typing import Literal

import numpy as np


TimeUnit = Literal["seconds", "minutes", "hours"]


def _validate_temperature(name: str, value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite number.")
    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError(f"{name} must be finite.")
    if numeric_value < -273.15 or numeric_value > 10000:
        raise ValueError(f"{name} must be between -273.15°C and 10000°C.")
    return numeric_value


def temperature_at_time(
    initial_temp: float,
    ambient_temp: float,
    k: float,
    time: float,
) -> float:
    """Return T(t) = Ts + (T0 - Ts)e^(-kt) for a nonnegative time."""
    initial = _validate_temperature("Initial temperature", initial_temp)
    ambient = _validate_temperature("Surrounding temperature", ambient_temp)
    if isinstance(k, bool) or not isinstance(k, Real) or not math.isfinite(float(k)) or k <= 0:
        raise ValueError("Rate constant k must be a finite positive number.")
    if isinstance(time, bool) or not isinstance(time, Real) or not math.isfinite(float(time)) or time < 0:
        raise ValueError("Time must be a finite nonnegative number.")
    return float(ambient + (initial - ambient) * math.exp(-float(k) * float(time)))


def simulate(
    initial_temp: float,
    ambient_temp: float,
    k: float,
    duration: float,
    points: int = 121,
    time_unit: TimeUnit = "minutes",
) -> dict:
    """Calculate temperature, derivative, and ambient difference over time."""
    initial = _validate_temperature("Initial temperature", initial_temp)
    ambient = _validate_temperature("Surrounding temperature", ambient_temp)
    if isinstance(k, bool) or not isinstance(k, Real) or not math.isfinite(float(k)) or not 0 < k <= 10:
        raise ValueError("Rate constant k must be greater than 0 and no greater than 10.")
    if (
        isinstance(duration, bool)
        or not isinstance(duration, Real)
        or not math.isfinite(float(duration))
        or not 0 < duration <= 100000
    ):
        raise ValueError("Duration must be greater than 0 and no greater than 100000.")
    if isinstance(points, bool) or not isinstance(points, Integral) or not 2 <= points <= 1001:
        raise ValueError("Graph resolution must be an integer from 2 to 1001.")
    if time_unit not in {"seconds", "minutes", "hours"}:
        raise ValueError("Time unit must be seconds, minutes, or hours.")

    times = np.linspace(0.0, float(duration), int(points))
    difference = initial - ambient
    exponential = np.exp(-float(k) * times)
    temperatures = ambient + difference * exponential
    rates = np.zeros_like(times) if difference == 0 else -float(k) * difference * exponential
    temperature_difference = temperatures - ambient

    return {
        "time": times.tolist(),
        "temperature": temperatures.tolist(),
        "rate_of_change": rates.tolist(),
        "temperature_difference": temperature_difference.tolist(),
        "final_temperature": float(temperatures[-1]),
        "initial_rate": float(rates[0]),
        "final_rate": float(rates[-1]),
        "mode": (
            "cooling" if initial > ambient
            else "heating" if initial < ambient
            else "equilibrium"
        ),
        "ambient_temperature": ambient,
        "initial_temperature": initial,
        "initial_temperature_difference": abs(difference),
        "cooling_constant": float(k),
        "duration": float(duration),
        "time_unit": time_unit,
    }
