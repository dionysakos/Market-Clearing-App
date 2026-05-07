import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.data_loader import initialize_session_state

st.set_page_config(
    page_title="Clearit",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            font-family: Arial, Helvetica, sans-serif;
        }

        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 20% 0%, #12371f 0%, #0b1a13 45%, #07110c 100%);
        }

        [data-testid="stHeader"] {
            background: rgba(7, 17, 12, 0.55);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d2417 0%, #132f1f 100%);
            border-right: 1px solid rgba(74, 222, 128, 0.22);
        }

        section[data-testid="stSidebar"] * {
            color: #eef2ff;
        }

        [data-testid="stMetric"] {
            background: rgba(34, 197, 94, 0.08);
            border: 1px solid rgba(74, 222, 128, 0.36);
            border-radius: 8px;
            padding: 1rem 1rem 0.85rem;
            text-align: center;
            box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.08), 0 10px 24px rgba(0, 0, 0, 0.22);
        }

        .hero-shell {
            background: linear-gradient(135deg, rgba(12, 32, 21, 0.96), rgba(14, 44, 28, 0.94));
            border: 1px solid rgba(74, 222, 128, 0.25);
            border-radius: 24px;
            padding: 1.5rem 1.5rem 1.2rem;
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.24);
        }

        .hero-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(74, 222, 128, 0.9), transparent);
            margin: 1rem 0 1.25rem;
        }

        .mini-visual {
            border: 1px solid rgba(74, 222, 128, 0.38);
            border-radius: 12px;
            padding: 0.9rem;
            background: linear-gradient(160deg, rgba(22, 55, 36, 0.86), rgba(10, 31, 20, 0.9));
            margin: 0 auto 0.8rem auto;
            text-align: center;
            color: #dcfce7;
            max-width: 430px;
            box-shadow: 0 10px 26px rgba(0, 0, 0, 0.25);
        }

        .heat-glow-line {
            animation: heatPulseLine 1.9s ease-in-out infinite;
            filter: drop-shadow(0 0 3px rgba(251, 191, 36, 0.6)) drop-shadow(0 0 8px rgba(249, 115, 22, 0.5));
        }

        .heat-glow-node {
            animation: heatPulseNode 1.7s ease-in-out infinite;
            filter: drop-shadow(0 0 4px rgba(248, 113, 113, 0.6)) drop-shadow(0 0 9px rgba(239, 68, 68, 0.45));
        }

        @keyframes heatPulseLine {
            0%, 100% {
                opacity: 0.78;
                stroke-width: 3;
            }
            50% {
                opacity: 1;
                stroke-width: 3.6;
            }
        }

        @keyframes heatPulseNode {
            0%, 100% {
                opacity: 0.82;
                transform: scale(1);
                transform-origin: center;
            }
            50% {
                opacity: 1;
                transform: scale(1.06);
                transform-origin: center;
            }
        }

        .feature-bubbles {
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
            margin: 0.6rem 0 1.1rem 0;
        }

        .feature-bubble {
            min-width: 190px;
            padding: 1rem 1.25rem;
            border-radius: 999px;
            border: 1px solid rgba(134, 239, 172, 0.62);
            background: radial-gradient(circle at 30% 25%, rgba(74, 222, 128, 0.42), rgba(12, 32, 21, 0.96));
            color: #ecfdf5;
            text-align: center;
            font-size: 1.02rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.28);
        }

        .assumption-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
        }

        .assumption-chip {
            background: rgba(18, 49, 32, 0.84);
            border: 1px solid rgba(74, 222, 128, 0.4);
            color: #dcfce7;
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            font-size: 0.9rem;
            line-height: 1.3;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize default data in session state so it's ready when the user navigates
initialize_session_state()

def dashboard_overview():
    st.title("⚡ Clearit")
    st.caption("A market clearing app for DC-OPF dispatch, congestion monitoring, and nodal pricing.")

    st.markdown(
        """
        <div class="mini-visual">
            <div style="font-size:0.92rem; margin-bottom:0.55rem;">Nodal pricing </div>
            <svg width="180" height="78" viewBox="0 0 180 78" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Nodal pricing illustration">
                <line x1="28" y1="22" x2="90" y2="39" stroke="#22c55e" stroke-width="3" />
                <line class="heat-glow-line" x1="90" y1="39" x2="152" y2="22" stroke="#f97316" stroke-width="3" />
                <line x1="90" y1="39" x2="90" y2="66" stroke="#22c55e" stroke-width="3" />
                <circle cx="28" cy="22" r="9" fill="#22c55e" stroke="#e2e8f0" stroke-width="1.5" />
                <circle cx="90" cy="39" r="9" fill="#22c55e" stroke="#e2e8f0" stroke-width="1.5" />
                <circle class="heat-glow-node" cx="152" cy="22" r="9" fill="#ef4444" stroke="#e2e8f0" stroke-width="1.5" />
                <circle class="heat-glow-node" cx="90" cy="66" r="9" fill="#ef4444" stroke="#e2e8f0" stroke-width="1.5" />
                <text x="124" y="33" fill="#fdba74" font-size="16" font-weight="700">!</text>
            </svg>
        </div>
        <div class="feature-bubbles">
            <div class="feature-bubble">DC-OPF</div>
            <div class="feature-bubble">LMP / SMP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)

    st.subheader("Model Assumptions")
    assumptions = [
        "DC-OPF linearized constraints with PTDF-based flow equations.",
        "Lossless transmission lines and small-angle approximations.",
        "Demand-side parameters are represented explicitly and can be tuned for elasticity studies.",
        "Generators are dispatched within Pmin/Pmax limits and linear marginal costs.",
        "Thermal limits are enforced symmetrically on each transmission line.",
    ]

    assumption_html = "".join([f"<span class='assumption-chip'>{assumption}</span>" for assumption in assumptions])
    st.markdown(f"<div class='assumption-grid'>{assumption_html}</div>", unsafe_allow_html=True)

    st.markdown("<div class='hero-divider'></div>", unsafe_allow_html=True)
    st.info("Design your grid. Break the limits. Clear the market. Use **Network Configuration** settings to define the grid and **Market Analytics** to run the optimization and inspect results.")


pages = [
    st.Page(dashboard_overview, title="Dashboard Overview"),
    st.Page("pages/data_input.py", title="Network Configuration"),
    st.Page("pages/results.py", title="Market Analytics"),
]

navigation = st.navigation(pages)
navigation.run()
