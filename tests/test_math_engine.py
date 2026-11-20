import math

import pytest

from backend.math_engine import simulate, temperature_at_time


@pytest.mark.parametrize(
    ("initial", "ambient", "k", "duration", "expected_mode"),
    [
        (90, 25, 0.08, 60, "cooling"),
        (5, 25, 0.08, 60, "heating"),
        (35, 25, 0.04, 60, "cooling"),
    ],
)
def test_required_scenarios_match_newton_model(initial, ambient, k, duration, expected_mode):
    result = simulate(initial, ambient, k, duration, points=121)
    expected_temperature = ambient + (initial - ambient) * math.exp(-k * duration)
    expected_rate = -k * (initial - ambient) * math.exp(-k * duration)

    assert result["mode"] == expected_mode
    assert math.isclose(result["final_temperature"], expected_temperature, rel_tol=1e-12)
    assert math.isclose(result["final_rate"], expected_rate, rel_tol=1e-12, abs_tol=1e-12)
    assert result["temperature"][0] == initial
    assert result["temperature"][-1] == result["final_temperature"]


def test_temperature_at_zero_is_initial_temperature():
    assert temperature_at_time(90, 25, 0.08, 0) == 90


def test_temperature_approaches_but_does_not_cross_ambient():
    result = simulate(90, 25, 0.08, 1000)
    assert math.isclose(result["final_temperature"], 25, abs_tol=1e-8)
    assert result["final_temperature"] >= 25
    assert result["temperature_difference"][-1] >= 0


def test_heating_moves_upward_toward_ambient():
    result = simulate(5, 25, 0.08, 10)
    assert result["temperature"][-1] > result["temperature"][0]
    assert result["temperature"][-1] < 25
    assert result["initial_rate"] > 0


def test_equilibrium_has_constant_temperature_and_zero_derivative():
    result = simulate(25, 25, 0.08, 60)
    assert result["mode"] == "equilibrium"
    assert all(value == 25 for value in result["temperature"])
    assert all(value == 0 for value in result["rate_of_change"])
    assert result["initial_temperature_difference"] == 0
    assert math.copysign(1, result["initial_rate"]) == 1
    assert all(math.copysign(1, value) == 1 for value in result["rate_of_change"])


@pytest.mark.parametrize("resolution", [2, 20, 301, 1001])
def test_graph_resolution_controls_number_of_samples(resolution):
    result = simulate(90, 25, 0.08, 60, points=resolution)
    assert len(result["time"]) == resolution
    assert len(result["temperature"]) == resolution
    assert len(result["rate_of_change"]) == resolution


def test_very_short_duration_keeps_both_endpoints():
    result = simulate(90, 25, 0.08, 1e-8, points=2)
    assert result["time"] == [0.0, 1e-8]
    assert result["temperature"][0] == 90
    assert 25 < result["temperature"][-1] < 90


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"k": -0.08}, "Rate constant"),
        ({"k": 0}, "Rate constant"),
        ({"initial_temp": -273.16}, "Initial temperature"),
        ({"duration": 0}, "Duration"),
        ({"points": 1}, "Graph resolution"),
        ({"points": 2.5}, "Graph resolution"),
    ],
)
def test_invalid_math_inputs_raise_value_error(kwargs, message):
    inputs = {
        "initial_temp": 90,
        "ambient_temp": 25,
        "k": 0.08,
        "duration": 60,
        "points": 121,
    }
    inputs.update(kwargs)
    with pytest.raises(ValueError, match=message):
        simulate(**inputs)
