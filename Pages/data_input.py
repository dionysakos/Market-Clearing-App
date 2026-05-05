import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Input | LMP Engine", page_icon="📝", layout="wide")

st.title("📝 Data Input for Market Clearing Engine")
st.markdown("Define the nodes (demand, supply) and lines (limits, connectivity) of the system.")

if 'nodes_df' not in st.session_state:
    st.session_state['nodes_df'] = pd.DataFrame({
        'Node': ['node1', 'node2', 'node3'],
        'Max_Demand': [0.0, 100.0, 200.0],
        'Bid_Price': [0.0, 500.0, 500.0], 
        'Pmax': [400.0, 400.0, 400.0],
        'Cost': [40.0, 80.0, 140.0]
    })

if 'lines_df' not in st.session_state:
    st.session_state['lines_df'] = pd.DataFrame({
        'Line': ['L_12', 'L_23', 'L_13'],
        'From': ['node1', 'node2', 'node1'],
        'To': ['node2', 'node3', 'node3'],
        'Thermal_Limit': [50.0, 50.0, 50.0],
        'Reactance': [0.2, 0.05, 0.2] 
    })

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Nodes")
    # The num_rows="dynamic" allows adding/removing rows
    edited_nodes = st.data_editor(st.session_state['nodes_df'], num_rows="dynamic", key="editor_nodes")

with col2:
    st.subheader("🔌 Lines")
    edited_lines = st.data_editor(st.session_state['lines_df'], num_rows="dynamic", key="editor_lines")

# 3. Save Changes
if st.button("💾 Save Data", type="primary"):
    st.session_state['nodes_df'] = edited_nodes
    st.session_state['lines_df'] = edited_lines
    st.success("Data saved successfully! Navigate to the 'Results' page.")