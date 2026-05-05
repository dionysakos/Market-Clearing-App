import streamlit as st
import pandas as pd
from utils.engine import run_market_clearing_ptdf_elastic
from utils.visualization import draw_network_graph

st.set_page_config(page_title="Results | LMP Engine", page_icon="📊", layout="wide")
st.title("📊 Market Clearing & LMPs")

if 'nodes_df' not in st.session_state or 'lines_df' not in st.session_state:
    st.warning("Δεν βρέθηκαν δεδομένα. Παρακαλώ μεταβείτε στη σελίδα 'Data Input' για να ορίσετε το δίκτυο.")
    st.stop() 

nodes_df = st.session_state['nodes_df']
lines_df = st.session_state['lines_df']

# --- TEMPORARY PTDF MOCK ---
ptdf_data = {
    'node1': [1/3, 1/3, 2/3],   
    'node2': [-1/3, 2/3, 1/3], 
    'node3': [0.0, 0.0, 0.0]  # Hub node 
}
ptdf_df = pd.DataFrame(ptdf_data, index=['L_12', 'L_23', 'L_13'])
# ---------------------------

if st.button("🚀 Execute Market Clearing", type="primary"):
    with st.spinner("Running market clearing optimization..."):
        # Engine
        status, welfare, gen, demand_res, flows, lmps, congestion = run_market_clearing_ptdf_elastic(
            nodes_df, lines_df, ptdf_df
        )
        
    if status == "Optimal":
        st.success("The problem was solved optimally!")
        
        # KPIs
        total_gen = sum(gen.values())
        total_demand = sum(demand_res.values())
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Social Welfare", f"€ {welfare:,.2f}")
        kpi2.metric("Total Generation", f"{total_gen:,.1f} MW")
        kpi3.metric("Clearing Demand", f"{total_demand:,.1f} MW")
        
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
                res_nodes.append({
                    "Node": n,
                    "LMP (€/MWh)": lmps.get(n, 0),
                    "Generation (MW)": gen.get(n, 0),
                    "Demand Served (MW)": demand_res.get(n, 0)
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