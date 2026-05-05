import streamlit as st
import pandas as pd
from utils.network_tools import calculate_ptdf
from utils.engine import run_market_clearing  
from utils.visualization import draw_network_graph

st.title("Market Analytics")
st.caption("Solve the market clearing problem and inspect system-wide and nodal pricing outputs.")

if 'nodes_df' not in st.session_state or 'lines_df' not in st.session_state:

    st.warning("No data found. Please navigate to the Network Configuration page to define your network.")
    st.stop() 

nodes_df = st.session_state['nodes_df']
lines_df = st.session_state['lines_df']
hub_node = st.session_state.get("hub_node", nodes_df["Node"].iloc[-1])

# Dynamically calculate PTDF based on the user's grid topology
try:
    ptdf_df = calculate_ptdf(nodes_df, lines_df, ref_node=hub_node)
except Exception as e:
    st.error(f"Error calculating PTDF matrix. Please check your network topology and Reactances. Details: {e}")
    st.stop()

if st.button("🚀 Execute Market Clearing", type="primary"):
    with st.spinner("Running market clearing optimization..."):
        
        status, cost, gen, flows, lmps, congestion, system_lambda = run_market_clearing(
            nodes_df, lines_df, ptdf_df
        )
        
    if status == "Optimal":
        st.success("The problem was solved optimally!")
        
        total_gen = sum(gen.values())
        total_demand = nodes_df['Demand'].sum() 
        
        summary_metrics = [
            ("Optimization Status", status),
            ("System λ (SMP)", f"€ {system_lambda:,.2f}/MWh"),
            ("Total Generation Cost", f"€ {cost:,.2f}"),
            ("Total Generation", f"{total_gen:,.1f} MW"),
            ("Total Demand", f"{total_demand:,.1f} MW"),
        ]

        st.subheader("Executive Metrics")
        for start in range(0, len(summary_metrics), 4):
            metric_cols = st.columns(min(4, len(summary_metrics) - start))
            for column, metric in zip(metric_cols, summary_metrics[start:start + 4]):
                with column:
                    st.metric(metric[0], metric[1])
        
        st.divider()
        
        st.subheader("Nodal Pricing")
        st.caption("Each node card shows the locational marginal price and its dispatch/demand snapshot.")
        for start in range(0, len(nodes_df), 4):
            node_columns = st.columns(min(4, len(nodes_df) - start))
            for column, (_, row) in zip(node_columns, nodes_df.iloc[start:start + 4].iterrows()):
                node_id = int(row["Node"])
                with column:
                    st.metric(
                        f"Node {node_id}",
                        f"€ {lmps.get(node_id, 0):,.2f}/MWh",
                        help=f"Generation: {gen.get(node_id, 0):,.1f} MW\nDemand: {row['Demand']:.1f} MW",
                    )
        
        st.divider()
        
        st.subheader("Transmission Line Flows")
        st.caption("Static flow labels keep the inspection view stable and readable.")

        for start in range(0, len(lines_df), 4):
            line_columns = st.columns(min(4, len(lines_df) - start))
            for column, (_, row) in zip(line_columns, lines_df.iloc[start:start + 4].iterrows()):
                line_id = int(row["Line"])
                flow_value = flows.get(line_id, 0)
                line_limit = float(row["Thermal_Limit"])
                with column:
                    st.metric(
                        f"Line {line_id}",
                        f"{flow_value:.1f} MW",
                        help=f"From: {int(row['From'])} -> To: {int(row['To'])}\nLimit: {line_limit:.1f} MW\nλ(+): {congestion.get(line_id, {}).get('lambda_str', 0):.2f}\nλ(-): {congestion.get(line_id, {}).get('lambda_opp', 0):.2f}",
                    )

        st.divider()

        st.subheader("Network Topology")
        st.caption("The graph is static and uses fixed coordinates so labels and flow values remain legible.")
        st.pyplot(
            draw_network_graph(nodes_df, lines_df, flows, lmps, congestion, hub_node=hub_node),
            use_container_width=True,
        )

        st.divider()

        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.write("Node Summary")
            res_nodes = []
            for n in nodes_df['Node']:
                res_nodes.append({
                    "Node": int(n),
                    "LMP (€/MWh)": lmps.get(n, 0),
                    "Generation (MW)": gen.get(n, 0),
                    "Demand (MW)": float(nodes_df.loc[nodes_df['Node'] == n, 'Demand'].iloc[0]),
                })
            st.dataframe(pd.DataFrame(res_nodes), use_container_width=True)
            
        with col_res2:
            st.write("Line Summary")
            res_lines = []
            for l in lines_df['Line']:
                res_lines.append({
                    "Line": int(l),
                    "Flow (MW)": flows.get(l, 0),
                    "Congestion Cost (+)": congestion.get(l, {}).get('lambda_str', 0),
                    "Congestion Cost (-)": congestion.get(l, {}).get('lambda_opp', 0)
                })
            st.dataframe(pd.DataFrame(res_lines), use_container_width=True)

    else:
        st.error(f"The optimization failed. Solver Status: {status}")