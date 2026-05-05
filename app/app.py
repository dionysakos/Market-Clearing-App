import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.data_loader import initialize_session_state

st.set_page_config(
    page_title="Nodal Pricing & Market Clearing Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            font-family: Arial, Helvetica, sans-serif;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #070b14 0%, #111827 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.12);
        }

        section[data-testid="stSidebar"] * {
            color: #eef2ff;
        }

        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 8px;
            padding: 1rem 1rem 0.85rem;
        }

        .hero-shell {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.94));
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 24px;
            padding: 1.5rem 1.5rem 1.2rem;
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.24);
        }

        .hero-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.9), transparent);
            margin: 1rem 0 1.25rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize default data in session state so it's ready when the user navigates
initialize_session_state()

def dashboard_overview():
    st.title("Nodal Pricing & Market Clearing Engine")
    st.caption("A professional DC-OPF dashboard for network configuration, market clearing, and locational pricing analysis.")

    left_col, right_col = st.columns([1.45, 0.95], vertical_alignment="top")

    with left_col:
        st.markdown(
            """
            <div class="hero-shell">
                <h3 style="margin-top:0; margin-bottom:0.75rem;">Executive Summary</h3>
                <p style="margin:0; line-height:1.65; color:#dbe4f0;">
                    This application solves a linearized DC optimal power flow problem to determine the least-cost
                    dispatch, system lambda, congestion components, and nodal market prices for a transmission network.
                    Use the navigation on the left to define the grid topology, assign generator and demand parameters,
                    and then run the market clearing engine.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        with st.container(border=True):
            st.metric("Model", "DC-OPF")
            st.metric("Pricing Output", "LMP / SMP")
            st.metric("Network Representation", "Static Topology View")

    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)

    st.subheader("Model Assumptions")
    assumption_left, assumption_right = st.columns(2)
    assumptions = [
        "DC-OPF linearized constraints with PTDF-based flow equations.",
        "Lossless transmission lines and small-angle approximations.",
        "Demand-side parameters are represented explicitly and can be tuned for elasticity studies.",
        "Generators are dispatched within Pmax limits and linear marginal costs.",
        "Thermal limits are enforced symmetrically on each transmission line.",
        "The selected hub node acts as the slack/reference bus for the PTDF basis.",
    ]

    for index, assumption in enumerate(assumptions):
        target_column = assumption_left if index % 2 == 0 else assumption_right
        with target_column:
            st.markdown(f"- {assumption}")

    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)
    st.info("Use **Network Configuration** to define the grid and **Market Analytics** to run the optimization and inspect results.")


pages = [
    st.Page(dashboard_overview, title="Dashboard Overview"),
    st.Page("pages/data_input.py", title="Network Configuration"),
    st.Page("pages/results.py", title="Market Analytics"),
]

navigation = st.navigation(pages)
navigation.run()
