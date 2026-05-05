import streamlit as st
import pandas as pd
from utils.network_tools import calculate_ptdf
from utils.engine import run_market_clearing  
from utils.visualization import draw_network_graph

st.set_page_config(page_title="Results | LMP Engine", page_icon="📊", layout="wide")
st.title("📊 Market Clearing & LMPs")

if 'nodes_df' not in st.session_state or 'lines_df' not in st.session_state:

    st.warning("No data found. Please navigate to the 'Data Input' page to define your network.")
    st.stop() 

nodes_df = st.session_state['nodes_df']
lines_df = st.session_state['lines_df']

# Dynamically calculate PTDF based on the user's grid topology
try:
    ptdf_df = calculate_ptdf(nodes_df, lines_df)
except Exception as e:
    st.error(f"Error calculating PTDF matrix. Please check your network topology and Reactances. Details: {e}")
    st.stop()

if st.button("🚀 Execute Market Clearing", type="primary"):
    with st.spinner("Running market clearing optimization..."):
        
        status, cost, gen, flows, lmps, congestion = run_market_clearing(
            nodes_df, lines_df, ptdf_df
        )
        
    if status == "Optimal":
        st.success("The problem was solved optimally!")
        
        # KPIs
        total_gen = sum(gen.values())
        # FIXED: Since demand is inelastic, we simply sum the user's input 'Demand' column
        total_demand = nodes_df['Demand'].sum() 
        
        kpi1, kpi2, kpi3 = st.columns(3)
        # FIXED: Changed from Welfare to Total Generation Cost
        kpi1.metric("Total Generation Cost", f"€ {cost:,.2f}") 
        kpi2.metric("Total Generation", f"{total_gen:,.1f} MW")
        kpi3.metric("Total Demand", f"{total_demand:,.1f} MW")
        
        st.divider()
        
        # Visualization
        st.subheader("🗺️ Network Graph")
        st.caption("Nodes are colored according to their LMP. Red lines indicate congestion.")
        draw_network_graph(nodes_df, lines_df, flows, lmps, congestion)
        
        st.divider()
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.write("📌 **Results Nodes (LMPs & Allocation)**")
            res_nodes = []
            for n in nodes_df['Node']:
                
                node_demand = nodes_df.loc[nodes_df['Node'] == n, 'Demand'].values
                
                res_nodes.append({
                    "Node": n,
                    "LMP (€/MWh)": lmps.get(n, 0),
                    "Generation (MW)": gen.get(n, 0),
                    "Demand (MW)": node_demand 
                })
            st.dataframe(pd.DataFrame(res_nodes), use_container_width=True)
            
        with col_res2:
            st.write("📌 **Results Lines (Flows & Congestion)**")
            res_lines = []
            for l in lines_df['Line']:
                res_lines.append({
                    "Line": l,
                    "Flow (MW)": flows.get(l, 0),
                    "Congestion Cost (+)": congestion.get(l, {}).get('lambda_str', 0),
                    "Congestion Cost (-)": congestion.get(l, {}).get('lambda_opp', 0)
                })
            st.dataframe(pd.DataFrame(res_lines), use_container_width=True)

    else:
        st.error(f"The optimization failed. Solver Status: {status}")