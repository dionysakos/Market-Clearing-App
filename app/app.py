import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.data_loader import initialize_session_state

st.set_page_config(
    page_title="LMP Market Clearing Engine", 
    page_icon="⚡", 
    layout="wide"
)

# Initialize default data in session state so it's ready when the user navigates
initialize_session_state()

st.title("⚡ Nodal Pricing & Market Clearing Engine")
st.markdown("""
Welcome to the **DC-OPF Market Clearing Simulator**. This application calculates the optimal economic dispatch and Locational Marginal Prices (LMPs) for a transmission network.

### How to use this tool:
1. 👈 **Go to `Data Input`** (in the sidebar) to define your grid topology. You can add nodes, set nodal demand, generation costs, and define transmission line reactances ($X$) and thermal limits.
2. 👈 **Go to `Results`** to execute the optimization. The engine will:
    * Automatically calculate the **PTDF Matrix** based on your line reactances.
    * Run a **Linear Program (PuLP)** to minimize total generation cost.
    * Extract **LMPs** and **Congestion Costs** from the constraint shadow prices.
    * Generate an interactive, physics-based network graph.

*This mathematical model is based on standard Independent System Operator (ISO) DC-OPF formulations using Power Transfer Distribution Factors (PTDFs).*
""")

st.info("💡 **Tip:** Use the sidebar on the left to navigate to the Data Input page and start building your network!")