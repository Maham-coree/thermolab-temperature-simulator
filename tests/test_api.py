import math

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)
SCENARIOS = [
    {"initial_temp": 90, "ambient_temp": 25, "k": 0.08, "duration": 60, "time_unit": "minutes"},
    {"initial_temp": 5, "ambient_temp": 25, "k": 0.08, "duration": 60, "time_unit": "minutes"},
    {"initial_temp": 35, "ambient_temp": 25, "k": 0.04, "duration": 60, "time_unit": "minutes"},
]


def test_root_and_health_endpoints():
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["docs"] == "/docs"
    assert client.get("/health").json()["status"] == "healthy"


def test_simulate_returns_structured_result_and_expected_value():
    response = client.post("/simulate", json=SCENARIOS[0])
    assert response.status_code == 200
    result = response.json()
    expected = 25 + 65 * math.exp(-0.08 * 60)
    assert result["mode"] == "cooling"
    assert math.isclose(result["final_temperature"], expected, rel_tol=1e-12)
    assert result["time_unit"] == "minutes"
    assert len(result["time"]) == 121


def test_compare_returns_each_scenario_in_order():
    response = client.post("/compare", json={"scenarios": SCENARIOS})
    assert response.status_code == 200
    results = response.json()["results"]
    assert [result["mode"] for result in results] == ["cooling", "heating", "cooling"]
    assert len(results) == 3


def test_invalid_api_requests_return_validation_errors():
    negative_rate = {**SCENARIOS[0], "k": -0.08}
    assert client.post("/simulate", json=negative_rate).status_code == 422
    assert client.post("/simulate", json={"initial_temp": 90}).status_code == 422
    assert client.post("/simulate", json={**SCENARIOS[0], "points": 1}).status_code == 422


def test_compare_requires_at_least_two_scenarios():
    response = client.post("/compare", json={"scenarios": SCENARIOS[:1]})
    assert response.status_code == 422
