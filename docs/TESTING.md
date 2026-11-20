# ThermoLab testing record

**Course:** MATH 303 – Real Analysis I  
**Project:** ThermoLab – Temperature Cooling and Heating Simulator

## Scope and method

This record summarizes the automated test suite and the functional checks performed against the current application. Numerical values below were obtained from `backend.math_engine.simulate` and confirmed against the FastAPI `POST /simulate` response. Calculations use the model implemented in the project; the values are not measurements from a physical object.

The test cases use 121 graph samples. Unless noted otherwise, time is in minutes and \(k\) is in \(\text{min}^{-1}\).

## Test case 1 – Cooling

**Purpose:** Confirm that an object initially hotter than its surroundings cools monotonically toward the ambient temperature.

**Inputs**

| Input | Value |
|---|---:|
| Initial temperature, \(T_0\) | 90 °C |
| Surrounding temperature, \(T_s\) | 25 °C |
| Rate constant, \(k\) | 0.08 min\(^{-1}\) |
| Duration, \(t\) | 60 min |
| Graph resolution | 121 points |

**Mathematical calculation**

\[
T(60)=25+(90-25)e^{-(0.08)(60)}
      =25+65e^{-4.8}
      \approx25.534933558186\ ^\circ\mathrm C.
\]

The derivative is \(T'(t)=-0.08(65)e^{-0.08t}\). It starts at \(-5.2\ ^\circ\mathrm C/\mathrm{min}\) and is approximately \(-0.042794684655\ ^\circ\mathrm C/\mathrm{min}\) at 60 minutes.

**Expected output:** Cooling mode; final temperature approximately 25.534934 °C; negative rate that decreases in magnitude over time.

**Actual output:** `mode=cooling`; final temperature **25.534933558186 °C**; initial rate **−5.200000000000 °C/min**; final rate **−0.042794684655 °C/min**.

**Status: PASS.** The object temperature decreases and remains above 25 °C at the end of the finite simulation, consistent with asymptotic convergence.

## Test case 2 – Heating

**Purpose:** Confirm that an object initially colder than its surroundings warms toward the ambient temperature.

**Inputs**

| Input | Value |
|---|---:|
| Initial temperature, \(T_0\) | 5 °C |
| Surrounding temperature, \(T_s\) | 25 °C |
| Rate constant, \(k\) | 0.08 min\(^{-1}\) |
| Duration, \(t\) | 60 min |
| Graph resolution | 121 points |

**Mathematical calculation**

\[
T(60)=25+(5-25)e^{-(0.08)(60)}
      =25-20e^{-4.8}
      \approx24.835405059020\ ^\circ\mathrm C.
\]

The derivative is \(T'(t)=-0.08(-20)e^{-0.08t}\). It starts at \(+1.6\ ^\circ\mathrm C/\mathrm{min}\) and is approximately \(+0.013167595278\ ^\circ\mathrm C/\mathrm{min}\) at 60 minutes.

**Expected output:** Heating mode; final temperature approximately 24.835405 °C; positive rate that tends toward zero.

**Actual output:** `mode=heating`; final temperature **24.835405059020 °C**; initial rate **+1.600000000000 °C/min**; final rate **+0.013167595278 °C/min**.

**Status: PASS.** The temperature rises but remains below 25 °C at 60 minutes.

## Test case 3 – Near equilibrium

**Purpose:** Check a smaller initial temperature difference and a slower rate constant.

**Inputs**

| Input | Value |
|---|---:|
| Initial temperature, \(T_0\) | 35 °C |
| Surrounding temperature, \(T_s\) | 25 °C |
| Rate constant, \(k\) | 0.04 min\(^{-1}\) |
| Duration, \(t\) | 60 min |
| Graph resolution | 121 points |

**Mathematical calculation**

\[
T(60)=25+(35-25)e^{-(0.04)(60)}
      =25+10e^{-2.4}
      \approx25.907179532894\ ^\circ\mathrm C.
\]

The derivative is \(T'(t)=-0.04(10)e^{-0.04t}\). It starts at \(-0.4\ ^\circ\mathrm C/\mathrm{min}\) and is approximately \(-0.036287181316\ ^\circ\mathrm C/\mathrm{min}\) at 60 minutes.

**Expected output:** Cooling mode; final temperature approximately 25.907180 °C; a smaller initial rate magnitude than Test Case 1.

**Actual output:** `mode=cooling`; final temperature **25.907179532894 °C**; initial rate **−0.400000000000 °C/min**; final rate **−0.036287181316 °C/min**.

**Status: PASS, with a rounding note.** The project brief lists 25.907177 °C as an approximate expected value. Direct evaluation of the stated equation gives 25.907179532894 °C, a difference of about 0.000002533 °C. Both values round to 25.90718 °C at five decimal places; the engine and API agree with the equation.

## Equilibrium check

**Purpose:** Verify the special case where the object starts at the surrounding temperature.

| Input | Value |
|---|---:|
| Initial temperature, \(T_0\) | 25 °C |
| Surrounding temperature, \(T_s\) | 25 °C |
| Rate constant, \(k\) | 0.08 min\(^{-1}\) |
| Duration, \(t\) | 60 min |

For \(T_0=T_s\), the difference \(T_0-T_s\) is zero, so \(T(t)=25\ ^\circ\mathrm C\) and \(T'(t)=0\) for the full interval.

**Actual output:** `mode=equilibrium`; initial and final temperatures are 25.000000 °C; initial and final rates are 0.000000 °C/min.

**Status: PASS.** The mathematical engine treats equilibrium explicitly and returns zero rates without a negative-zero display.

## Automated test suite

Run the suite from the project root in PowerShell:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

**Result during this review: 23 passed.** The suite includes:

- The three required scenarios, checked against the analytical temperature and derivative.
- Initial-temperature preservation, heating/cooling direction, equilibrium, and approach toward ambient temperature.
- Very short durations and graph resolutions of 2, 20, 301, and 1001 points.
- Invalid rate constants, temperatures below absolute zero, zero duration, and invalid graph resolution.
- API root and health routes, simulation and comparison responses, and validation responses for invalid inputs.

Python syntax was also checked with:

```powershell
.\venv\Scripts\python.exe -m compileall -q app.py backend tests
```

**Result: passed.**

## Functional checks performed

These are functional checks performed during review; they are not additional persistent pytest test cases.

| Area | Check performed | Result |
|---|---|---|
| Navigation | Rendered Home, Simulator, Mathematics, Experiments, and About using Streamlit AppTest | Pass |
| Frontend/backend | Submitted a simulation through the Streamlit simulator using its configured API URL | Pass |
| Cooling and heating | Checked both modes through the API and Streamlit simulator | Pass |
| Graphs and metrics | Confirmed three Plotly charts and six result metrics appear after a run | Pass |
| Data and CSV | Confirmed the simulation table and CSV download control are present; the generated download URL has a `.csv` suffix | Pass |
| Comparison | Compared the three presets and a saved simulator run; the returned results and comparison chart rendered | Pass |
| Reset | Reset simulator results and reset saved experiments/comparison | Pass |
| API validation | A negative \(k\) request returned HTTP 422; root, health, simulation, and comparison requests returned successful responses | Pass |
| Error handling | With an unavailable API URL, the simulator displayed an actionable connection error without an application exception | Pass |
| Responsive layout | Inspected the rendered page at desktop (1440 × 1000) and narrow (390 × 844) viewport sizes | Pass |

## Validation and units

The API rejects nonpositive \(k\), nonpositive duration, temperatures below absolute zero, unsupported time units, and graph resolutions outside 2–1001. The frontend states that \(k\) is expressed per selected time unit and does not silently convert it when the time unit changes.
