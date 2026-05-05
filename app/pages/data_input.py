import streamlit as st
from utils import initialize_session_state, validate_network_data
from utils.data_loader import normalize_network_data
from utils.network_tools import calculate_ptdf

st.title("Network Configuration")
st.caption("Define nodes and transmission lines using integer indexing. The hub node defaults to the last node entered.")

initialize_session_state()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Nodes")
    edited_nodes = st.data_editor(
        st.session_state["nodes_df"],
        num_rows="dynamic",
        key="nodes_editor",
        hide_index=True,
        disabled=["Node"],
        column_config={
            "Node": st.column_config.NumberColumn("Node", format="%d", help="Auto-renumbered on save."),
            "Demand": st.column_config.NumberColumn("Demand (MW)", min_value=0.0, step=1.0),
            "Pmax": st.column_config.NumberColumn("Pmax (MW)", min_value=0.0, step=1.0),
            "Cost": st.column_config.NumberColumn("Cost (€/MWh)", min_value=0.0, step=1.0),
        },
    )

node_options = list(range(1, max(len(edited_nodes), 1) + 1))
default_hub = st.session_state.get("hub_node", node_options[-1])
if default_hub not in node_options:
    default_hub = node_options[-1]
hub_index = node_options.index(default_hub)

with col2:
    st.subheader("Transmission Lines")
    edited_lines = st.data_editor(
        st.session_state["lines_df"],
        num_rows="dynamic",
        key="lines_editor",
        hide_index=True,
        disabled=["Line"],
        column_config={
            "Line": st.column_config.NumberColumn("Line", format="%d", help="Auto-renumbered on save."),
            "From": st.column_config.NumberColumn("From Node", min_value=1, step=1),
            "To": st.column_config.NumberColumn("To Node", min_value=1, step=1),
            "Thermal_Limit": st.column_config.NumberColumn("Thermal Limit (MW)", min_value=0.0, step=1.0),
            "Reactance": st.column_config.NumberColumn("Reactance (p.u.)", min_value=0.0001, step=0.01, format="%.4f"),
        },
    )

st.selectbox(
    "Hub / Slack Node",
    options=node_options,
    index=hub_index,
    help="The hub node is used as the PTDF reference bus and defaults to the last node entered.",
    key="hub_selector",
)

if st.button("Save Configuration", type="primary"):
    normalized_nodes, normalized_lines, normalized_hub = normalize_network_data(
        edited_nodes,
        edited_lines,
        st.session_state.get("hub_selector", default_hub),
    )
    is_valid, msg = validate_network_data(normalized_nodes, normalized_lines, normalized_hub)

    if is_valid:
        try:
            st.session_state["ptdf_df"] = calculate_ptdf(normalized_nodes, normalized_lines, ref_node=normalized_hub)
        except Exception as exc:
            st.error(f"The PTDF matrix could not be computed. Please check the network topology. Details: {exc}")
        else:
            st.session_state["nodes_df"] = normalized_nodes
            st.session_state["lines_df"] = normalized_lines
            st.session_state["hub_node"] = normalized_hub
            st.success("Configuration saved successfully. Go to Market Analytics to run the market clearing engine.")
    else:
        st.error(msg)