# ThermoLab: Temperature Cooling and Heating Simulator

**Course:** MATH 303 – Real Analysis I  
**Project type:** Educational full-stack web application

## 1. Project title

**ThermoLab – Temperature Cooling and Heating Simulator**

## 2. Abstract

ThermoLab is an interactive educational application for exploring how the temperature of an object changes when it is placed in surroundings at a different constant temperature. The project implements Newton's law of cooling and heating as an exponential function and presents the resulting temperature and rate profiles through an interactive web interface.

The project connects the physical model to Real Analysis topics including exponential functions, limits, continuity, derivatives, and convergence of sampled sequences. A Streamlit frontend communicates with an independent FastAPI backend. NumPy performs the calculations, Plotly displays the graphs, and Pandas prepares the results table and CSV export. Tests verify the three required experiments, equilibrium, input validation, and the API behavior.

## 3. Introduction

Temperature changes are often modeled by relating the rate of change to the difference between an object's temperature and the temperature of its surroundings. Newton's law gives a simple first-order model of this process. Its solution is exponential, which makes the model useful for studying both a practical phenomenon and mathematical behavior over time.

ThermoLab lets a user specify the initial temperature, surrounding temperature, rate constant, duration, time unit, and graph resolution. It identifies cooling, heating, or equilibrium, calculates the temperature profile, displays the instantaneous rate, and provides an option to compare scenarios.

## 4. Problem statement

The project addresses the following question:

> Given an object's initial temperature and a constant surrounding temperature, how does the object's temperature change with time under Newton's law, and how can the change be analyzed using concepts from Real Analysis?

A complete response requires a mathematically correct function, its derivative and limit, a way to compare cooling and heating cases, and clear explanations of the assumptions that restrict the model.

## 5. Project objectives

- Implement Newton's law of cooling and heating in a separate mathematical engine.
- Represent cooling, heating, and equal-temperature equilibrium.
- Display temperature, rate of change, and temperature difference as interactive graphs.
- Explain the mathematical model and its relation to Real Analysis.
- Compare the required classroom scenarios and saved simulator runs.
- Provide a readable data table and CSV export.
- Validate inputs and communicate errors without hiding backend failures.

## 6. Practical applications

Newton's law is useful as a first approximation for classroom demonstrations of a hot drink cooling, a cold object warming, or a sample approaching room temperature. The model also introduces a common method used in elementary thermal and differential-equation analyses: describing a changing quantity through a rate proportional to its difference from an equilibrium value.

ThermoLab is an educational simulator, not a sensor or a calibrated engineering tool. It does not collect physical measurements or predict a particular real-world object without experimentally determined parameters.

## 7. Mathematical model

The temperature function used by the application is

\[
T(t)=T_s+(T_0-T_s)e^{-kt}.
\]

The variables and units are:

| Symbol | Meaning | Unit in the required scenarios |
|---|---|---|
| \(T(t)\) | Object temperature at elapsed time \(t\) | °C |
| \(T_0\) | Object's initial temperature, \(T(0)\) | °C |
| \(T_s\) | Constant surrounding (ambient) temperature | °C |
| \(t\) | Elapsed time | minutes |
| \(k\) | Positive rate constant | min\(^{-1}\) |

The app also supports seconds and hours. If a different time unit is selected, \(k\) must be expressed per that same unit. The frontend explains this requirement and does not silently convert \(k\).

At \(t=0\), \(e^0=1\), so \(T(0)=T_0\). The temperature difference from the surroundings is

\[
T(t)-T_s=(T_0-T_s)e^{-kt}.
\]

This form makes the direction of change and the limiting value visible.

## 8. Newton's law of cooling and heating

Newton's law states that the instantaneous rate of temperature change is proportional to the difference between the object and its surroundings [1]:

\[
\frac{dT}{dt}=-k(T-T_s),\qquad k>0.
\]

The negative sign means the temperature difference shrinks over time. Solving this differential equation with \(T(0)=T_0\) gives the model in Section 7. If \(T_0=T_s\), the difference is zero for all time and the object remains in equilibrium. This special case does not require division by the initial temperature difference.

The rate constant controls the speed of the change: with the same initial and surrounding temperatures, a larger \(k\) causes the difference to decay more quickly. Its units are inverse time, so \(kt\) is dimensionless in the exponential.

## 9. Real Analysis concepts

### Exponential functions

The factor \(e^{-kt}\) is positive and decreases as \(t\) increases because \(k>0\). It scales the initial difference \(T_0-T_s\). In the simulator, the object temperature therefore moves monotonically toward \(T_s\) unless it starts there.

### Limits and thermal equilibrium

Since \(k>0\), \(-kt\to-\infty\) as \(t\to\infty\), and hence \(e^{-kt}\to0\). Therefore,

\[
\lim_{t\to\infty}T(t)
=T_s+(T_0-T_s)\lim_{t\to\infty}e^{-kt}
=T_s.
\]

The limit is the equilibrium temperature. For a nonzero initial difference, \(e^{-kt}\) is positive at every finite time, so the model approaches \(T_s\) asymptotically rather than reaching it at a finite time. If \(T_0=T_s\), the temperature is already at equilibrium.

### Continuity

The exponential function is continuous, and sums and scalar multiples of continuous functions remain continuous [2]. Thus \(T(t)\) is continuous for every finite \(t\). This means there are no jumps in the idealized temperature curve.

### Derivatives and rate of temperature change

Differentiating the model gives

\[
T'(t)=-k(T_0-T_s)e^{-kt}.
\]

For time measured in minutes, \(T'(t)\) is measured in °C/min. Since \(k>0\) and \(e^{-kt}>0\):

- If \(T_0>T_s\), then \(T'(t)<0\): the object cools.
- If \(T_0<T_s\), then \(T'(t)>0\): the object heats.
- If \(T_0=T_s\), then \(T'(t)=0\): the temperature is constant.

The derivative is the instantaneous rate at a particular time. Its magnitude decreases as the temperature difference shrinks. The exponential function is differentiable, so the resulting temperature function is differentiable for every finite time.

### Sampled sequences

The application samples the continuous function at a finite set of points for plotting and export. If equally spaced times are extended as \(t_n=n\Delta t\), where \(\Delta t>0\), then

\[
T(t_n)-T_s
=(T_0-T_s)\left(e^{-k\Delta t}\right)^n\longrightarrow0.
\]

The ratio \(e^{-k\Delta t}\) is between zero and one, so this is a convergent geometric sequence. In the application, the graph resolution produces a finite approximation to the continuous curve; it does not change the underlying model.

## 10. System architecture

ThermoLab keeps the presentation, API, and mathematical calculation in separate layers:

```text
User
  │
  ▼
Streamlit frontend (app.py)
  │  HTTP requests through requests
  ▼
FastAPI routes (backend/main.py)
  │  Pydantic request/response validation
  ▼
Application services (backend/services.py)
  │
  ▼
NumPy mathematical engine (backend/math_engine.py)
  │
  └── JSON result returned to Streamlit
        ├── Plotly charts and metric cards
        └── Pandas table and CSV download
```

The API provides `GET /`, `GET /health`, `POST /simulate`, and `POST /compare`; interactive API documentation is available at `/docs`. The comparison endpoint accepts between two and ten scenarios. The frontend uses session state for the latest result and saved comparison scenarios. The application does not use a database.

## 11. Technologies used

The project files use the following technologies:

- **Python** for the frontend, backend, and tests.
- **Streamlit** for the user interface and session state.
- **Plotly** for interactive temperature, derivative, difference, and comparison charts.
- **FastAPI** for HTTP endpoints.
- **Pydantic** for API request and response validation.
- **NumPy** for time samples and exponential calculations.
- **Pandas** for simulation tables and CSV data.
- **Requests** for frontend-to-backend HTTP communication.
- **Pytest** and FastAPI's `TestClient` for automated tests.
- **Custom CSS** and Streamlit theme configuration for the visual design.

The official framework and library documentation is listed in References [3]–[8].

## 12. Frontend and backend implementation

### Frontend

The Streamlit app in `app.py` provides five navigation sections:

- **Home:** introduces the model and the cooling and heating processes, with an action to open the simulator.
- **Simulator:** collects temperatures, \(k\), duration, time unit, and graph resolution. It displays the detected mode, six result metrics, three Plotly chart views, a data table, and a CSV download. Reset controls clear the active simulation or saved experiments.
- **Mathematics:** explains the equation, derivative, continuity, asymptotic limit, equilibrium, and sampled sequences.
- **Experiments:** presents the three required preset scenarios, accepts saved runs, and compares selected cases with a chart and summary table.
- **About:** describes the educational purpose, technologies, assumptions, and limitations.

The frontend reads the backend base URL from `API_URL`, defaulting to `http://127.0.0.1:8000`. Connection and API validation errors are presented to the user.

### Backend

`backend/main.py` defines the FastAPI routes. `backend/schemas.py` limits and validates request values, including temperatures, positive \(k\), duration, time unit, and graph resolution. `backend/services.py` passes validated requests to `backend/math_engine.py`. The mathematical engine returns the sampled time, temperature, derivative, ambient difference, mode, and summary values.

The simulation accepts temperatures from absolute zero through 10,000 °C, \(0<k\leq10\), a positive duration up to 100,000 selected time units, and 2–1001 graph points. The constant ambient-temperature model and the selected time unit are stated in the interface and documentation.

## 13. Testing methodology

Testing combines unit tests for the mathematical engine, API tests using FastAPI's `TestClient`, and functional checks of the Streamlit interface. The automated tests verify the three required cases against the analytical formula and derivative, equilibrium, heating/cooling direction, short-duration behavior, graph resolutions, invalid inputs, and API routes.

During the final review, the existing suite completed with **23 passing tests**. Additional Streamlit AppTest checks rendered all five sections and exercised simulation, charts, the CSV download control, resets, comparison, and backend-unavailable error handling. The required cases were also run directly through the engine and API. The full test record and exact outputs are in [`TESTING.md`](./TESTING.md).

## 14. Three experimental results

Each result below uses a 60-minute duration. Temperatures and rates are the outputs of the current application model.

| Scenario | \(T_0\) | \(T_s\) | \(k\) | Mode | Final temperature at 60 min | Initial rate | Final rate |
|---|---:|---:|---:|---|---:|---:|---:|
| Cooling | 90 °C | 25 °C | 0.08 min\(^{-1}\) | Cooling | 25.534933558186 °C | −5.200000000000 °C/min | −0.042794684655 °C/min |
| Heating | 5 °C | 25 °C | 0.08 min\(^{-1}\) | Heating | 24.835405059020 °C | +1.600000000000 °C/min | +0.013167595278 °C/min |
| Near equilibrium | 35 °C | 25 °C | 0.04 min\(^{-1}\) | Cooling | 25.907179532894 °C | −0.400000000000 °C/min | −0.036287181316 °C/min |

For the near-equilibrium case, the project brief gives 25.907177 °C as an approximate expected value. Direct substitution into the stated model gives 25.907179532894 °C. The verified application output follows the equation; the small discrepancy is noted in [`TESTING.md`](./TESTING.md).

When \(T_0=T_s=25\ ^\circ\mathrm C\), the application reports equilibrium: the temperature remains 25 °C and both rates are zero.

## 15. Discussion and interpretation

In the cooling case, the initial difference is 65 °C. It falls to about 0.534934 °C after one hour, and the negative rate is much smaller in magnitude than its initial value. In the heating case, the initial difference is −20 °C; the object warms but remains slightly below the ambient temperature at 60 minutes. These outputs demonstrate the derivative's sign and the limit's asymptotic behavior.

The near-equilibrium case begins only 10 °C from the surroundings and uses a smaller \(k\). It therefore starts with a smaller rate magnitude than the main cooling case. Across all non-equilibrium examples, the temperature moves toward \(T_s\), while the absolute rate decreases. The equal-temperature case is constant and has no temperature change.

## 16. Assumptions and limitations

- The surrounding temperature \(T_s\) is constant throughout the simulation.
- The rate constant \(k\) remains constant and represents the same physical conditions over the full interval.
- The object is treated as having a uniform temperature at each instant; internal temperature gradients are not modeled.
- The model assumes heat transfer is proportional to the temperature difference. Real heat transfer may also depend on airflow, geometry, material properties, evaporation, radiation, and contact conditions.
- The application has no physical sensors, experimental calibration, or uncertainty analysis. Its results are model predictions for education.
- Changing the selected time unit does not automatically convert \(k\); the user must enter a consistent inverse-time value.
- Finite simulation samples approximate a continuous function. Increasing graph resolution adds plotted and exported sample points but does not alter the equation.

## 17. Conclusion

ThermoLab implements Newton's law as a functional simulator and uses it to demonstrate how exponential behavior connects to derivatives, continuity, limits, and convergence. The application distinguishes cooling, heating, and equilibrium, provides interactive graphs and scenario comparisons, and exposes the calculation through an independent API. Verification confirmed that the required outputs agree with the implemented equation and that the interface and API tests pass.

The model's simplicity makes the mathematical relationships clear, but it also limits its physical accuracy. Its results should be interpreted as an idealized educational demonstration rather than measurements or engineering predictions.

## 18. References

1. Boyce, William E., Richard C. DiPrima, and Douglas B. Meade. *Elementary Differential Equations and Boundary Value Problems*. 11th ed., Wiley, 2017.
2. Abbott, Stephen. *Understanding Analysis*. 2nd ed., Springer, 2015.
3. Streamlit documentation. https://docs.streamlit.io/
4. FastAPI documentation. https://fastapi.tiangolo.com/
5. Pydantic documentation. https://docs.pydantic.dev/
6. NumPy documentation. https://numpy.org/doc/
7. Plotly Python documentation. https://plotly.com/python/
8. Pandas documentation. https://pandas.pydata.org/docs/
