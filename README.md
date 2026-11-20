# ThermoLab – Temperature Cooling and Heating Simulator

**Course:** MATH 303 – Real Analysis I  
**Project type:** Full-stack educational web application

ThermoLab is an interactive laboratory for exploring how an object's temperature changes when it is placed in surroundings at a different, constant temperature. It models cooling, heating, and thermal equilibrium with Newton's law and connects the results to topics in Real Analysis.

## Objectives

- Visualize temperature as a continuous function of time.
- Interpret the derivative as an instantaneous rate of temperature change.
- Observe convergence to the surrounding temperature.
- Compare how initial conditions and the rate constant affect the process.
- Export sampled results for further study.

## Features

- Streamlit dashboard with Home, Simulator, Mathematics, Experiments, and About sections.
- Cooling, heating, and equilibrium mode detection.
- Validated simulation controls for temperatures, rate constant, duration, time unit, and graph resolution.
- Three interactive Plotly visualizations: temperature, rate of change, and temperature difference.
- Metrics for initial/final temperatures, ambient temperature, temperature difference, and initial/final rates.
- Full simulation data table and CSV download.
- Side-by-side comparison for the three required scenarios and saved custom experiments.
- Independent FastAPI service with input validation and interactive API documentation.
- Automated mathematical and API tests.

## Mathematical model

Newton's law states that the rate of temperature change is proportional to the difference between the object's temperature and the constant surrounding temperature:

\[
\frac{dT}{dt}=-k(T-T_s)
\]

Its solution is

\[
T(t)=T_s+(T_0-T_s)e^{-kt},
\]

where:

- \(T(t)\) is the object's temperature at elapsed time \(t\), in °C.
- \(T_0\) is the initial object temperature, in °C.
- \(T_s\) is the constant surrounding temperature, in °C.
- \(k>0\) is the rate constant per selected time unit.
- \(t\) is elapsed time in that selected unit.

The instantaneous rate of change is

\[
T'(t)=-k(T_0-T_s)e^{-kt}.
\]

If \(T_0>T_s\), then \(T'(t)<0\) and the object cools. If \(T_0<T_s\), then \(T'(t)>0\) and it heats. If \(T_0=T_s\), the temperature remains constant and the derivative is zero.

### Real Analysis concepts

- **Exponential functions:** \(e^{-kt}\) is the decaying fraction of the initial temperature difference.
- **Continuity and differentiability:** Exponential functions have both properties, and sums and scalar multiples preserve them; therefore \(T(t)\) is continuous and differentiable at every finite time.
- **Limits:** Since \(k>0\), \(e^{-kt}\to0\) as \(t\to\infty\), so
  \[
  \lim_{t\to\infty}T(t)=T_s.
  \]
  The model approaches ambient temperature asymptotically. Except when the object starts at equilibrium, it does not reach that value at a finite time.
- **Sequences and convergence:** Sampling at \(t_n=n\Delta t\), for \(\Delta t>0\), gives
  \[
  T(t_n)-T_s=(T_0-T_s)\left(e^{-k\Delta t}\right)^n\to0,
  \]
  a geometric sequence with ratio strictly between zero and one.

## Technology stack

- **Frontend:** Streamlit, Python, custom CSS, Plotly
- **Backend:** FastAPI, Pydantic
- **Calculations:** NumPy
- **Tables and CSV:** Pandas
- **Testing:** Pytest and FastAPI's TestClient

## Project architecture

The Streamlit interface makes HTTP requests to the independent FastAPI service. API schemas validate requests and responses, service functions connect routes to the mathematical engine, and the engine calculates time-series values with NumPy.

```text
temperature_simulator/
├── app.py
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── math_engine.py
│   ├── schemas.py
│   └── services.py
├── tests/
│   ├── test_api.py
│   └── test_math_engine.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and startup

These commands use PowerShell on Windows. Run them from the project root.

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell prevents script activation, run commands with the environment's executables directly, such as `.\venv\Scripts\python.exe`.

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Start the backend

In the first terminal:

```powershell
uvicorn backend.main:app --reload
```

The API listens at `http://127.0.0.1:8000`. Interactive documentation is at `http://127.0.0.1:8000/docs`.

### 4. Start the frontend

In a second terminal:

```powershell
streamlit run app.py
```

Streamlit opens at `http://localhost:8501`. By default, the frontend connects to `http://127.0.0.1:8000`. Set `API_URL` to the backend base URL when it runs elsewhere. To permit additional browser origins, set `CORS_ORIGINS` to a comma-separated list; the default allows only localhost and 127.0.0.1 on port 8501.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API information and endpoint links |
| `GET` | `/health` | Health check |
| `POST` | `/simulate` | Calculate one temperature time series |
| `POST` | `/compare` | Calculate 2–10 scenarios in one request |
| `GET` | `/docs` | Interactive OpenAPI documentation |

Example request:

```json
{
  "initial_temp": 90,
  "ambient_temp": 25,
  "k": 0.08,
  "duration": 60,
  "points": 121,
  "time_unit": "minutes"
}
```

Temperatures must be at least absolute zero, \(k\) must be positive, duration must be positive, and graph resolution must be between 2 and 1001 points. Extra fields and invalid time units are rejected with a validation response.

## Testing

Run all unit and API tests from the project root:

```powershell
python -m pytest -q
```

The tests cover the three required experiments, the analytical final-temperature and derivative values, heating/cooling/equilibrium, short durations, graph resolution, invalid inputs, and the API routes.

## Required experimental scenarios

The Experiments section preselects these cases for comparison. The rate constant is per minute and duration is in minutes.

| Scenario | Initial \(T_0\) | Surrounding \(T_s\) | \(k\) | Duration |
|---|---:|---:|---:|---:|
| Cooling | 90°C | 25°C | 0.08 min\(^{-1}\) | 60 min |
| Heating | 5°C | 25°C | 0.08 min\(^{-1}\) | 60 min |
| Small temperature difference | 35°C | 25°C | 0.04 min\(^{-1}\) | 60 min |

The model gives the following final temperatures at 60 minutes:

| Scenario | Final temperature |
|---|---:|
| Cooling | 25.535°C |
| Heating | 24.835°C |
| Small temperature difference | 25.907°C |

These values are model calculations, not measured experimental data.

## Assumptions and limitations

- Surrounding temperature and the rate constant remain constant.
- The object has a uniform temperature at each instant.
- Heat transfer follows the idealized Newton cooling/heating law.
- Time and \(k\) must be expressed in consistent units. Changing the selected time unit does not automatically convert \(k\).
- The idealized model approaches equilibrium asymptotically and is not intended for professional thermal-engineering decisions.
- Real systems may be affected by airflow, evaporation, material properties, changing surroundings, and measurement error.

ThermoLab is intended for educational demonstration and mathematical exploration.
