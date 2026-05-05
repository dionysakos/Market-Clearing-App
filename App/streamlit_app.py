import streamlit as st
import pandas as pd
from utils.engine import run_market_clearing
from utils.visualization import draw_network_graph

st.set_page_config(layout="wide", page_title="LMP Market Dashboard")
st.title("⚡ Nodal Pricing Market Clearing Engine")


if st.button("Run Market Clearing"):
    with st.spinner("Solving DC-OPF..."):
        # Backend 
        status, cost, gen, flow, lmps, congestion = run_market_clearing(
            nodes_df, lines_df, ptdf_df
        )
        
    if status == "Optimal":
        st.success(f"Optimal -> Total Cost / Welfare: {cost:,.2f} €")
        
        #Frontend
        draw_network_graph(nodes_df, lines_df, flow, lmps, congestion)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("LMP Results by Node")
            st.dataframe(pd.DataFrame(list(lmps.items()), columns=["Node", "LMP (€/MWh)"]))
        with col2:
            st.write("Power Flow Results")
            st.dataframe(pd.DataFrame(list(flow.items()), columns=["Line", "Flow (MW)"]))
    else:
        st.error(f"The problem is {status}. Please check the input data and try again.")