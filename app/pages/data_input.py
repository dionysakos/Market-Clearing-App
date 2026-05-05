import streamlit as st
from utils import initialize_session_state, validate_network_data

st.set_page_config(page_title="Data Input", layout="wide")
st.title("📝 Network Data Input")

# 1. Load defaults safely using our new module
initialize_session_state()

# 2. Render the interactive tables side-by-side
col1, col2 = st.columns(2)

with col1:
    st.subheader("Nodes")
    # ADDED: Unique keys to guarantee stable widget identity across reruns
    edited_nodes = st.data_editor(st.session_state['nodes_df'], num_rows="dynamic", key="nodes_editor")

with col2:
    st.subheader("Lines")
    # ADDED: Unique keys to guarantee stable widget identity across reruns
    edited_lines = st.data_editor(st.session_state['lines_df'], num_rows="dynamic", key="lines_editor")

# 3. Validate and Save
if st.button("Save Configuration"):
    is_valid, msg = validate_network_data(edited_nodes, edited_lines)
    
    if is_valid:
        st.session_state['nodes_df'] = edited_nodes
        st.session_state['lines_df'] = edited_lines
        st.success("Data saved successfully! Go to Results to run the market clearing.")
    else:
        st.error(msg)