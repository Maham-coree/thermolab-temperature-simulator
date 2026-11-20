"""Streamlit dashboard for ThermoLab."""

import os
from copy import deepcopy

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


st.set_page_config(
    page_title="ThermoLab | Temperature simulator",
    page_icon=":material/device_thermostat:",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
TIME_UNITS = ("seconds", "minutes", "hours")
TIME_TO_MINUTES = {"seconds": 1 / 60, "minutes": 1.0, "hours": 60.0}
TIME_SINGULAR = {"seconds": "second", "minutes": "minute", "hours": "hour"}
NAV_ICONS = {
    "Home": "home",
    "Simulator": "thermostat",
    "Mathematics": "functions",
    "Experiments": "science",
    "About": "info",
}
DEFAULT_INPUTS = {
    "input_initial_temp": 90.0,
    "input_ambient_temp": 25.0,
    "input_k": 0.08,
    "input_duration": 60.0,
    "input_time_unit": "minutes",
    "input_points": 121,
}
PRESET_SCENARIOS = [
    {
        "name": "Hot drink cooling",
        "initial_temp": 90.0,
        "ambient_temp": 25.0,
        "k": 0.08,
        "duration": 60.0,
        "time_unit": "minutes",
        "points": 121,
    },
    {
        "name": "Cold object warming",
        "initial_temp": 5.0,
        "ambient_temp": 25.0,
        "k": 0.08,
        "duration": 60.0,
        "time_unit": "minutes",
        "points": 121,
    },
    {
        "name": "Small temperature difference",
        "initial_temp": 35.0,
        "ambient_temp": 25.0,
        "k": 0.04,
        "duration": 60.0,
        "time_unit": "minutes",
        "points": 121,
    },
]

st.markdown(
    """
    <style>
    .stApp { background: #f4f7fb; }
    .block-container { max-width: 1480px; padding-top: 1.5rem; padding-bottom: 3rem; }
    .thermo-hero {
          padding: 2rem 2.2rem; border-radius: 22px; color: #fff; margin-bottom: 1rem;
          min-height: 232px; display: flex; flex-direction: column; justify-content: center;
      background: linear-gradient(118deg, #10243d 0%, #174467 62%, #167a7c 100%);
      box-shadow: 0 14px 34px rgba(16, 36, 61, .14);
    }
    .thermo-hero h1 { color: #fff; font-size: clamp(2rem, 4vw, 2.8rem); margin: .25rem 0 .35rem; }
    .thermo-hero p { color: #d7e8ef; margin: 0; max-width: 740px; font-size: 1rem; }
    .thermo-eyebrow { color: #91e1d0; font-size: .73rem; font-weight: 750; letter-spacing: .14em; }
        .page-heading { padding: .3rem 0 1rem; }
        .section-kicker { color: #167a7c; font-size: .72rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
        .page-heading h2 { color: #18324d; margin: .22rem 0 .3rem; font-size: clamp(1.55rem, 2.8vw, 2rem); }
        .page-heading p { color: #66758a; margin: 0; max-width: 850px; }
        .brand-lockup { display: flex; align-items: center; gap: .75rem; margin: .15rem 0 .7rem; }
        .brand-mark {
          display: grid; place-items: center; width: 2.5rem; height: 2.5rem; border-radius: .8rem;
          color: white; font: 800 1.15rem/1 Arial, sans-serif;
          background: linear-gradient(140deg, #167a7c, #16476a);
          box-shadow: 0 6px 16px rgba(22, 122, 124, .2);
        }
        .brand-name { color: #18324d; font-size: 1.15rem; font-weight: 800; letter-spacing: -.02em; }
        .brand-caption { color: #758398; font-size: .62rem; font-weight: 700; letter-spacing: .12em; }
        .st-key-run_simulation button, .st-key-home_open button {
          min-height: 2.8rem; font-weight: 700; transition: transform 160ms ease, box-shadow 160ms ease;
        }
        .st-key-run_simulation button:hover, .st-key-home_open button:hover {
          transform: translateY(-1px); box-shadow: 0 7px 16px rgba(22, 122, 124, .18);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
          border-radius: 17px; background: rgba(255, 255, 255, .94);
          box-shadow: 0 5px 18px rgba(16, 36, 61, .035);
          transition: transform 170ms ease, box-shadow 170ms ease, border-color 170ms ease;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
          transform: translateY(-2px); border-color: #b9d4db;
          box-shadow: 0 10px 24px rgba(16, 36, 61, .075);
        }
    div[data-testid="stMetric"] {
      background: #fff; border: 1px solid #e3eaf1; border-radius: 15px;
      padding: .8rem 1rem; box-shadow: 0 4px 14px rgba(16, 36, 61, .035);
    }
        @media (max-width: 700px) {
          .block-container { padding: 1rem 1rem 2rem; }
          .thermo-hero { min-height: 190px; padding: 1.5rem; border-radius: 18px; }
          .page-heading { padding-bottom: .65rem; }
        }
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_post(endpoint: str, payload: dict) -> dict:
    """Send a request to the API and turn transport/validation errors into useful messages."""
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=20)
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach the ThermoLab API at {API_URL}. "
            "Start the backend and check API_URL."
        ) from exc

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        if isinstance(detail, list):
            detail = "; ".join(
                f"{item.get('loc', ['input'])[-1]}: {item.get('msg', 'invalid value')}"
                for item in detail
            )
        raise RuntimeError(f"API request failed ({response.status_code}): {detail}")

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("The API returned an unreadable response.") from exc


def reset_simulation() -> None:
    """Restore simulator controls and clear the active result."""
    for key, value in DEFAULT_INPUTS.items():
        st.session_state[key] = value
    st.session_state.result = None
    st.session_state.last_inputs = None


def clear_experiments() -> None:
    """Clear saved scenarios and their latest comparison."""
    st.session_state.experiments = []
    st.session_state.comparison = None


def navigate_to(page: str) -> None:
    st.session_state.page = page


def make_chart(title: str, x_title: str, y_title: str) -> go.Figure:
    """Create a consistently styled responsive Plotly figure."""
    figure = go.Figure()
    figure.update_layout(
        title=dict(text=title, font=dict(size=17, color="#18324d")),
        height=390,
        margin=dict(l=18, r=18, t=55, b=24),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color="#526176"),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.12, x=0),
        xaxis_title=x_title,
        yaxis_title=y_title,
    )
    figure.update_xaxes(showgrid=True, gridcolor="#edf1f5", zeroline=False)
    figure.update_yaxes(showgrid=True, gridcolor="#edf1f5", zeroline=False)
    return figure


def show_hero() -> None:
    st.markdown(
        """
        <div class="thermo-hero">
          <div class="thermo-eyebrow">MATH 303 · REAL ANALYSIS I</div>
          <h1>ThermoLab</h1>
          <p>A scientific workspace for exploring how temperature changes over
          time and converges toward thermal equilibrium.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_section_heading(eyebrow: str, title: str, description: str) -> None:
    """Render a consistent title block for each workspace section."""
    st.markdown(
        f"""
        <div class="page-heading">
          <div class="section-kicker">{eyebrow}</div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_home() -> None:
    hero, model = st.columns([1.25, 0.85], gap="large")
    with hero:
        show_hero()
        st.button(
            "Launch the simulator",
            type="primary",
            icon=":material/play_arrow:",
            key="home_open",
            on_click=navigate_to,
            args=("Simulator",),
        )
    with model:
        with st.container(border=True):
            st.markdown('<div class="section-kicker">MODEL AT A GLANCE</div>', unsafe_allow_html=True)
            st.subheader("Newton's law")
            st.latex(r"T(t)=T_s+(T_0-T_s)e^{-kt}")
            st.write(
                "The temperature difference decays exponentially. For positive "
                "$k$, the object approaches the surrounding temperature "
                "asymptotically."
            )
            st.caption("A continuous-time model with an interpretable rate.")

    show_section_heading(
        "A focused learning tool",
        "From thermal change to mathematical insight",
        "Explore a model, inspect its behavior, and connect the visualization to core ideas in Real Analysis.",
    )
    features = st.columns(3)
    feature_content = [
        (
            "Run a simulation",
            "Set initial and ambient conditions, choose a rate and time scale, then calculate the full temperature profile.",
            ":material/tune:",
        ),
        (
            "Study the mathematics",
            "Interpret the derivative, continuity, exponential decay, and the limit at thermal equilibrium.",
            ":material/functions:",
        ),
        (
            "Visualize and compare",
            "Explore responsive Plotly charts, save scenarios, and export the underlying samples as CSV.",
            ":material/monitoring:",
        ),
    ]
    for column, (title, description, icon) in zip(features, feature_content):
        with column:
            with st.container(border=True):
                st.subheader(title, icon=icon)
                st.write(description)

    show_section_heading(
        "Two directions, one model",
        "Cooling and heating",
        "The sign of the initial temperature difference determines the direction of change.",
    )
    processes = st.columns(2)
    with processes[0]:
        with st.container(border=True):
            st.subheader("Cooling", icon=":material/south:")
            st.latex(r"T_0>T_s\quad\Longrightarrow\quad T'(t)<0")
            st.write("A hotter object releases heat and its temperature decreases toward the surroundings.")
    with processes[1]:
        with st.container(border=True):
            st.subheader("Heating", icon=":material/north:")
            st.latex(r"T_0<T_s\quad\Longrightarrow\quad T'(t)>0")
            st.write("A colder object gains heat and its temperature increases toward the surroundings.")


def current_payload() -> dict:
    return {
        "initial_temp": st.session_state.input_initial_temp,
        "ambient_temp": st.session_state.input_ambient_temp,
        "k": st.session_state.input_k,
        "duration": st.session_state.input_duration,
        "time_unit": st.session_state.input_time_unit,
        "points": st.session_state.input_points,
    }


def render_results(result: dict, payload: dict) -> None:
    time_unit = result["time_unit"]
    unit_label = TIME_SINGULAR[time_unit]
    mode_display = {
        "cooling": ("Cooling", "blue", ":material/south:"),
        "heating": ("Heating", "orange", ":material/north:"),
        "equilibrium": ("Thermal equilibrium", "green", ":material/check_circle:"),
    }
    mode_explanations = {
        "cooling": "The object starts warmer than its surroundings and cools toward the ambient temperature.",
        "heating": "The object starts colder than its surroundings and warms toward the ambient temperature.",
        "equilibrium": "The object and surroundings start at the same temperature, so the temperature remains constant.",
    }
    mode_name, mode_color, mode_icon = mode_display[result["mode"]]
    show_section_heading(
        "Simulation output",
        f"{mode_name} profile",
        "Read the key values first, then inspect how temperature and its rate evolve over time.",
    )
    with st.container(horizontal=True):
        st.badge(mode_name, color=mode_color, icon=mode_icon)
        st.caption(mode_explanations[result["mode"]])
    st.caption(
        "Temperatures are in °C. The rate constant is expressed per "
        f"{unit_label}; changing the time unit changes its meaning, not its value."
    )

    metric_columns = st.columns(3)
    metric_columns[0].metric("Initial temperature", f"{result['initial_temperature']:.3f} °C", border=True)
    metric_columns[1].metric("Final temperature", f"{result['final_temperature']:.3f} °C", border=True)
    metric_columns[2].metric("Surrounding temperature", f"{result['ambient_temperature']:.3f} °C", border=True)
    rate_columns = st.columns(3)
    rate_columns[0].metric(
        "Initial temperature gap",
        f"{result['initial_temperature_difference']:.3f} °C",
        border=True,
    )
    rate_columns[1].metric(
        "Initial rate",
        f"{result['initial_rate']:.4f} °C/{unit_label}",
        border=True,
    )
    rate_columns[2].metric(
        "Final rate",
        f"{result['final_rate']:.4f} °C/{unit_label}",
        border=True,
    )

    temperature_chart = make_chart(
        "Temperature vs. time",
        f"Elapsed time ({time_unit})",
        "Temperature (°C)",
    )
    temperature_chart.add_trace(
        go.Scatter(
            x=result["time"],
            y=result["temperature"],
            mode="lines",
            name="Object temperature",
            line=dict(color="#168b9a", width=3),
            fill="tozeroy",
            fillcolor="rgba(22,139,154,.08)",
            hovertemplate=(
                f"%{{x:.3f}} {time_unit}<br>%{{y:.3f}} °C"
                "<extra>%{fullData.name}</extra>"
            ),
        )
    )
    temperature_chart.add_trace(
        go.Scatter(
            x=result["time"],
            y=[result["ambient_temperature"]] * len(result["time"]),
            mode="lines",
            name="Surrounding temperature",
            line=dict(color="#e69a42", width=2, dash="dash"),
            hovertemplate=(
                f"%{{x:.3f}} {time_unit}<br>%{{y:.3f}} °C"
                "<extra>%{fullData.name}</extra>"
            ),
        )
    )
    rate_chart = make_chart(
        "Instantaneous rate of temperature change",
        f"Elapsed time ({time_unit})",
        f"Rate (°C/{unit_label})",
    )
    rate_chart.add_trace(
        go.Scatter(
            x=result["time"],
            y=result["rate_of_change"],
            mode="lines",
            name="T'(t)",
            line=dict(color="#5267bd", width=3),
            hovertemplate=(
                f"%{{x:.3f}} {time_unit}<br>%{{y:.4f}} °C/{unit_label}"
                "<extra>%{fullData.name}</extra>"
            ),
        )
    )
    difference_chart = make_chart(
        "Temperature difference from surroundings",
        f"Elapsed time ({time_unit})",
        "T(t) − Ts (°C)",
    )
    difference_chart.add_trace(
        go.Scatter(
            x=result["time"],
            y=result["temperature_difference"],
            mode="lines",
            name="T(t) − Ts",
            line=dict(color="#d28a3d", width=3),
            fill="tozeroy",
            fillcolor="rgba(210,138,61,.08)",
            hovertemplate=(
                f"%{{x:.3f}} {time_unit}<br>%{{y:.3f}} °C"
                "<extra>%{fullData.name}</extra>"
            ),
        )
    )

    temperature_tab, rate_tab, difference_tab = st.tabs(
        ["Temperature", "Rate of change", "Temperature difference"]
    )
    with temperature_tab:
        st.plotly_chart(
            temperature_chart,
            width="stretch",
            config={"responsive": True},
            key="temperature_chart",
        )
    with rate_tab:
        st.plotly_chart(
            rate_chart,
            width="stretch",
            config={"responsive": True},
            key="rate_chart",
        )
    with difference_tab:
        st.plotly_chart(
            difference_chart,
            width="stretch",
            config={"responsive": True},
            key="difference_chart",
        )

    show_section_heading(
        "Data export",
        "Simulation samples",
        "Review the complete time series or download these values for further analysis.",
    )
    table = pd.DataFrame(
        {
            f"Time ({time_unit})": result["time"],
            "Temperature (°C)": result["temperature"],
            "Difference from surroundings (°C)": result["temperature_difference"],
            f"Rate (°C/{unit_label})": result["rate_of_change"],
        }
    )
    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        alt="Full simulation time series with temperature and rate values",
    )
    st.download_button(
        "Download simulation data (CSV)",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name="thermolab_simulation.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    if st.button(
        "Save scenario for comparison",
        icon=":material/bookmark_add:",
        key="save_scenario",
    ):
        experiment_number = len(st.session_state.experiments) + 1
        st.session_state.experiments.append(
            {
                "name": f"Saved experiment {experiment_number}",
                "payload": deepcopy(payload),
                "result": deepcopy(result),
            }
        )
        st.success("Scenario saved. Open Experiments to compare it.")


def show_simulator() -> None:
    show_section_heading(
        "Interactive model",
        "Temperature simulator",
        "Set the thermal conditions and observe cooling, heating, or equilibrium under Newton's law.",
    )

    for key, value in DEFAULT_INPUTS.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("last_inputs", None)
    st.session_state.setdefault("experiments", [])

    with st.form("simulation_form"):
        with st.container(border=True):
            st.subheader("Thermal conditions", icon=":material/device_thermostat:")
            temperature_columns = st.columns(2)
            with temperature_columns[0]:
                st.number_input(
                    "Initial object temperature (°C)",
                    min_value=-273.15,
                    max_value=10000.0,
                    step=1.0,
                    key="input_initial_temp",
                    help="The object's uniform temperature at time t = 0.",
                )
            with temperature_columns[1]:
                st.number_input(
                    "Surrounding temperature (°C)",
                    min_value=-273.15,
                    max_value=10000.0,
                    step=1.0,
                    key="input_ambient_temp",
                    help="Assumed constant throughout the experiment.",
                )

        with st.container(border=True):
            st.subheader("Simulation settings", icon=":material/settings:")
            setting_columns = st.columns(3)
            with setting_columns[0]:
                st.number_input(
                    "Rate constant, k",
                    min_value=0.0001,
                    max_value=10.0,
                    step=0.01,
                    format="%.4f",
                    key="input_k",
                    help="Must be positive and measured per selected time unit.",
                )
            with setting_columns[1]:
                st.number_input(
                    "Simulation duration",
                    min_value=0.001,
                    max_value=100000.0,
                    step=5.0,
                    key="input_duration",
                    help="How long to simulate, in the selected time unit.",
                )
                st.selectbox("Time unit", TIME_UNITS, key="input_time_unit")
            with setting_columns[2]:
                st.slider(
                    "Graph resolution (sample points)",
                    min_value=2,
                    max_value=1001,
                    step=1,
                    key="input_points",
                    help="More points make smoother plots and a larger data export.",
                )

        st.caption(
            "Keep units consistent: k is per selected time unit (for example, "
            "min⁻¹ when time is measured in minutes). Changing the time unit does "
            "not automatically convert k."
        )
        run_column, reset_column, _ = st.columns([1.25, 1.25, 3])
        with run_column:
            run = st.form_submit_button(
                "Run simulation",
                type="primary",
                icon=":material/play_arrow:",
                key="run_simulation",
            )
        with reset_column:
            st.form_submit_button(
                "Reset simulator",
                icon=":material/restart_alt:",
                on_click=reset_simulation,
            )

    selected_payload = current_payload()
    if run:
        try:
            with st.spinner("Calculating the temperature profile..."):
                result = api_post("/simulate", selected_payload)
            st.session_state.result = result
            st.session_state.last_inputs = selected_payload
        except RuntimeError as exc:
            st.error(str(exc))

    result = st.session_state.result
    status_inputs = st.session_state.last_inputs if result else selected_payload
    status_mode = (
        "cooling" if status_inputs["initial_temp"] > status_inputs["ambient_temp"]
        else "heating" if status_inputs["initial_temp"] < status_inputs["ambient_temp"]
        else "equilibrium"
    )
    status_details = {
        "cooling": ("Cooling", "blue", ":material/south:", "The object is warmer than the surroundings."),
        "heating": ("Heating", "orange", ":material/north:", "The object is colder than the surroundings."),
        "equilibrium": ("Thermal equilibrium", "green", ":material/check_circle:", "Object and surrounding temperatures are equal."),
    }
    status_name, status_color, status_icon, status_description = status_details[status_mode]
    with st.container(horizontal=True, border=True):
        st.badge(status_name, color=status_color, icon=status_icon)
        st.caption(
            f"{status_description} "
            f"Showing {'the latest successful run' if result else 'the selected conditions'}."
        )

    if result is None:
        st.info("Run the simulation to calculate the temperature and rate profiles.")
        return
    render_results(result, st.session_state.last_inputs or selected_payload)


def show_mathematics() -> None:
    show_section_heading(
        "MATH 303 · REAL ANALYSIS I",
        "The mathematics behind the model",
        "Newton's law gives a differentiable exponential solution whose limit is the surrounding temperature.",
    )
    with st.container(border=True):
        st.subheader("Newton's law of cooling and heating")
        st.latex(r"\frac{dT}{dt}=-k(T-T_s)")
        st.latex(r"T(t)=T_s+(T_0-T_s)e^{-kt}")
        st.write(
            "$T_0$ is the initial object temperature, $T_s$ is the constant "
            "surrounding temperature, $t$ is elapsed time, and $k>0$ is the "
            "rate constant per selected time unit. The differential equation "
            "says that the rate is proportional to the current temperature "
            "difference from the surroundings."
        )

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("Derivative and direction")
            st.latex(r"T'(t)=-k(T_0-T_s)e^{-kt}")
            st.write(
                "Because $k>0$ and $e^{-kt}>0$, the sign of $T'(t)$ is opposite "
                "the sign of $T_0-T_s$. A hotter object cools ($T'<0$), a colder "
                "object warms ($T'>0$), and equal temperatures give equilibrium "
                "with $T'(t)=0$. The derivative is the instantaneous rate of "
                "temperature change."
            )
    with right:
        with st.container(border=True):
            st.subheader("Continuity and differentiability")
            st.write(
                "The exponential function is continuous and differentiable on "
                "the real line. Sums, scalar multiples, and compositions of such "
                "functions preserve these properties, so $T(t)$ is continuous "
                "and differentiable for every finite time."
            )
            st.latex(r"T(0)=T_0,\qquad T'(0)=-k(T_0-T_s)")

    with st.container(border=True):
        st.subheader("Limit and asymptotic equilibrium")
        st.latex(
            r"\lim_{t\to\infty}T(t)"
            r"=T_s+(T_0-T_s)\lim_{t\to\infty}e^{-kt}=T_s"
        )
        st.write(
            "For $k>0$, $-kt$ decreases without bound as $t$ grows, and the "
            "exponential $e^{-kt}$ tends to zero. Therefore the temperature "
            "difference tends to zero and the limit is the surrounding "
            "temperature. In this idealized model the exponential is positive "
            "at every finite time, so equilibrium is approached asymptotically "
            "rather than attained in finite time (unless the object starts at "
            "equilibrium)."
        )

    with st.container(border=True):
        st.subheader("Sequences and convergence")
        st.write(
            "Sampling the function at equally spaced times $t_n=n\\Delta t$ "
            "produces a sequence. For any fixed $\\Delta t>0$, its temperature "
            "difference is a geometric sequence with ratio $e^{-k\\Delta t}$, "
            "which lies strictly between 0 and 1."
        )
        st.latex(
            r"T(t_n)-T_s=(T_0-T_s)\left(e^{-k\Delta t}\right)^n"
            r"\longrightarrow 0"
        )
        st.write(
            "This is the discrete counterpart of the continuous-time limit and "
            "explains why the plotted sample values converge to $T_s$."
        )


def show_experiments() -> None:
    show_section_heading(
        "Scenario lab",
        "Experiments and comparison",
        "Compare the required cooling, heating, and near-equilibrium cases, or add scenarios saved from the simulator.",
    )
    st.session_state.setdefault("experiments", [])
    st.session_state.setdefault("comparison", None)
    selected_payloads = []
    selected_names = []

    scenario_columns = st.columns(3)
    for index, (column, scenario) in enumerate(zip(scenario_columns, PRESET_SCENARIOS)):
        with column:
            with st.container(border=True):
                initial = scenario["initial_temp"]
                ambient = scenario["ambient_temp"]
                if initial > ambient:
                    mode_name, mode_color, mode_icon = "Cooling", "blue", ":material/south:"
                elif initial < ambient:
                    mode_name, mode_color, mode_icon = "Heating", "orange", ":material/north:"
                else:
                    mode_name, mode_color, mode_icon = "Equilibrium", "green", ":material/check_circle:"
                st.subheader(scenario["name"])
                st.badge(mode_name, color=mode_color, icon=mode_icon)
                st.markdown(f"**{initial:g}°C** → **{ambient:g}°C**")
                st.caption(
                    f"k = {scenario['k']:g} min⁻¹ · "
                    f"{scenario['duration']:g} minutes"
                )
                checked = st.checkbox(
                    "Include in comparison",
                    value=True,
                    key=f"preset_scenario_{index}",
                )
                if checked:
                    selected_payloads.append(
                        {key: value for key, value in scenario.items() if key != "name"}
                    )
                    selected_names.append(scenario["name"])

    if st.session_state.experiments:
        show_section_heading(
            "Saved from the simulator",
            "Custom scenarios",
            "Choose saved runs to compare alongside the required experiments.",
        )
        for start in range(0, len(st.session_state.experiments), 3):
            batch = st.session_state.experiments[start : start + 3]
            saved_columns = st.columns(len(batch))
            for offset, (column, experiment) in enumerate(zip(saved_columns, batch)):
                index = start + offset
                with column:
                    with st.container(border=True):
                        payload = experiment["payload"]
                        result = experiment["result"]
                        st.subheader(experiment["name"])
                        st.badge(
                            result["mode"].capitalize(),
                            color={"cooling": "blue", "heating": "orange", "equilibrium": "green"}[
                                result["mode"]
                            ],
                        )
                        st.markdown(
                            f"**{payload['initial_temp']:g}°C** → "
                            f"**{payload['ambient_temp']:g}°C**"
                        )
                        st.caption(
                            f"k = {payload['k']:g} per {TIME_SINGULAR[payload['time_unit']]} · "
                            f"{payload['duration']:g} {payload['time_unit']}"
                        )
                        checked = st.checkbox(
                            "Include in comparison",
                            value=True,
                            key=f"saved_scenario_{index}",
                        )
                        if checked:
                            selected_payloads.append(payload)
                            selected_names.append(experiment["name"])
    else:
        st.caption("Save a simulation to add a custom experiment.")

    controls = st.columns([1.2, 1.2, 3])
    compare_clicked = controls[0].button(
        "Compare selected",
        type="primary",
        icon=":material/compare_arrows:",
        key="compare_selected",
    )
    controls[1].button(
        "Reset experiments",
        icon=":material/delete_sweep:",
        on_click=clear_experiments,
        key="reset_experiments",
    )

    if compare_clicked:
        if len(selected_payloads) < 2:
            st.warning("Select at least two scenarios to compare.")
        elif len(selected_payloads) > 10:
            st.warning("Select no more than 10 scenarios for one comparison.")
        else:
            try:
                with st.spinner("Comparing scenarios..."):
                    response = api_post("/compare", {"scenarios": selected_payloads})
                st.session_state.comparison = {
                    "names": selected_names,
                    "results": response["results"],
                }
            except RuntimeError as exc:
                st.error(str(exc))

    comparison = st.session_state.comparison
    if comparison:
        show_section_heading(
            "Comparison results",
            "Temperature trajectories",
            "Time is normalized to minutes in the comparison chart; the original rate units remain in the table.",
        )
        results = comparison["results"]
        figure = make_chart(
            "Scenario temperature comparison",
            "Elapsed time (minutes)",
            "Temperature (°C)",
        )
        colors = ["#168b9a", "#e69a42", "#5267bd", "#b35f8e", "#59966a", "#a46d39"]
        rows = []
        for index, (name, result) in enumerate(zip(comparison["names"], results)):
            scale = TIME_TO_MINUTES[result["time_unit"]]
            figure.add_trace(
                go.Scatter(
                    x=[time * scale for time in result["time"]],
                    y=result["temperature"],
                    mode="lines",
                    name=name,
                    line=dict(color=colors[index % len(colors)], width=2.5),
                    hovertemplate="%{x:.3f} min<br>%{y:.3f}°C<extra>%{fullData.name}</extra>",
                )
            )
            rows.append(
                {
                    "Scenario": name,
                    "Mode": result["mode"].capitalize(),
                    "Initial temperature (°C)": result["initial_temperature"],
                    "Ambient temperature (°C)": result["ambient_temperature"],
                    "Final temperature (°C)": result["final_temperature"],
                    "Initial rate (°C / selected unit)": result["initial_rate"],
                    "Rate unit": result["time_unit"],
                }
            )
        st.plotly_chart(
            figure,
            width="stretch",
            config={"responsive": True},
            key="comparison_chart",
        )
        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
            alt="Summary table comparing selected temperature scenarios",
        )


def show_about() -> None:
    show_section_heading(
        "Project overview",
        "About ThermoLab",
        "An educational digital laboratory connecting a thermal model to mathematical analysis.",
    )
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("Objectives and method")
            st.markdown(
                """
                - Explore cooling, heating, and thermal equilibrium.
                - Relate an exponential solution to its differential equation.
                - Interpret derivatives as instantaneous rates.
                - Observe convergence to the ambient-temperature limit.
                - Compare scenarios by changing initial conditions and $k$.
                """
            )
    with right:
        with st.container(border=True):
            st.subheader("Technology")
            st.markdown(
                """
                - **Frontend:** Streamlit, Plotly, custom CSS
                - **Backend:** FastAPI and Pydantic
                - **Calculations:** NumPy
                - **Tables and exports:** Pandas
                - **Testing:** Pytest
                """
            )
    with st.container(border=True):
        st.subheader("Assumptions and limitations")
        st.markdown(
            """
            - Surrounding temperature and the positive rate constant remain fixed.
            - The object is treated as having a uniform temperature at every instant.
            - Heat exchange follows the idealized Newton cooling/heating law.
            - Real airflow, evaporation, material properties, and changing ambient
              conditions can alter measured temperatures.
            - Results are for education, not thermal-engineering decisions.
            """
        )
        st.caption(
            "Time and k must use consistent units. The app does not convert k "
            "when the selected time unit changes."
        )


with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
          <div class="brand-mark">T</div>
          <div>
            <div class="brand-name">ThermoLab</div>
            <div class="brand-caption">SIMULATION STUDIO</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("MATH 303 · Real Analysis I")
    st.radio(
        "Workspace",
        ["Home", "Simulator", "Mathematics", "Experiments", "About"],
        format_func=lambda page: f":material/{NAV_ICONS[page]}: {page}",
        key="page",
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(f"API endpoint: `{API_URL}`")

page = st.session_state.page
if page == "Home":
    show_home()
elif page == "Simulator":
    show_simulator()
elif page == "Mathematics":
    show_mathematics()
elif page == "Experiments":
    show_experiments()
else:
    show_about()
