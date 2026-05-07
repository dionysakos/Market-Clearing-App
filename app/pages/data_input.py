import pandas as pd
import streamlit as st
from utils import initialize_session_state, validate_network_data
from utils.data_loader import normalize_network_data
from utils.network_tools import calculate_ptdf

st.title("Network Configuration")

initialize_session_state()


def _mark_hub_manual_selection():
    st.session_state["hub_user_selected"] = True


def _display_optional_limit(value, lower=False):
    if pd.isna(value):
        return "0" if lower else "∞"
    text = str(value).strip()
    if text == "":
        return "0" if lower else "∞"
    lowered = text.lower()
    if lowered in {"∞", "+∞", "inf", "+inf", "infinity", "+infinity"}:
        return "0" if lower else "∞"
    if lower and lowered in {"-∞", "-inf", "-infinity"}:
        return "0"
    return f"{float(text):g}"


def _prepare_optional_limit_series(series, lower=False):
    return series.apply(lambda x: _display_optional_limit(x, lower=lower)).astype("string")


def _prepare_nodes_for_editor(df):
    nodes = df.copy()
    for column in ["Node", "Demand", "Pmin", "Pmax", "Cost"]:
        if column not in nodes.columns:
            nodes[column] = pd.NA
    nodes = nodes[["Node", "Demand", "Pmin", "Pmax", "Cost"]].reset_index(drop=True)
    nodes["Node"] = pd.Series(range(1, len(nodes) + 1), dtype="Int64")
    nodes["Pmin"] = _prepare_optional_limit_series(nodes["Pmin"], lower=True)
    nodes["Pmax"] = _prepare_optional_limit_series(nodes["Pmax"], lower=False)
    return nodes


def _prepare_lines_for_editor(df):
    lines = df.copy()
    for column in ["Line", "From", "To", "Thermal_Limit", "Reactance"]:
        if column not in lines.columns:
            lines[column] = pd.NA
    lines = lines[["Line", "From", "To", "Thermal_Limit", "Reactance"]].reset_index(drop=True)
    lines["Line"] = pd.Series(range(1, len(lines) + 1), dtype="Int64")
    lines["Thermal_Limit"] = _prepare_optional_limit_series(lines["Thermal_Limit"], lower=False)
    return lines


if "draft_nodes_df" not in st.session_state:
    st.session_state["draft_nodes_df"] = _prepare_nodes_for_editor(st.session_state["nodes_df"])
if "draft_lines_df" not in st.session_state:
    st.session_state["draft_lines_df"] = _prepare_lines_for_editor(st.session_state["lines_df"])
if "nodes_row_count_snapshot" not in st.session_state:
    st.session_state["nodes_row_count_snapshot"] = len(st.session_state["draft_nodes_df"])
if "lines_row_count_snapshot" not in st.session_state:
    st.session_state["lines_row_count_snapshot"] = len(st.session_state["draft_lines_df"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("Nodes")
    edited_nodes = st.data_editor(
        st.session_state["draft_nodes_df"],
        num_rows="dynamic",
        key="nodes_editor",
        hide_index=True,
        disabled=["Node"],
        column_config={
            "Node": st.column_config.NumberColumn("Node", format="%d", help="Auto-incremented as rows are added."),
            "Demand": st.column_config.NumberColumn("Demand (MW)", min_value=0.0, step=1.0),
            "Pmin": st.column_config.TextColumn(
                "Pmin (MW)",
                default="0",
                help="Use a non-negative number. Leave blank to use 0.",
                validate=r"^\s*$|^\d+(\.\d+)?$",
            ),
            "Pmax": st.column_config.TextColumn(
                "Pmax (MW)",
                default="∞",
                help="Use a number, leave blank, or set ∞ for relaxed upper bound.",
                validate=r"^\s*$|^-?\d+(\.\d+)?$|^[+]?∞$|^[+]?inf(inity)?$",
            ),
            "Cost": st.column_config.NumberColumn("Cost (€/MWh)", min_value=0.0, step=1.0),
        },
    )

with col2:
    st.subheader("Transmission Lines")
    edited_lines = st.data_editor(
        st.session_state["draft_lines_df"],
        num_rows="dynamic",
        key="lines_editor",
        hide_index=True,
        disabled=["Line"],
        column_config={
            "Line": st.column_config.NumberColumn("Line", format="%d", help="Auto-renumbered on save."),
            "From": st.column_config.NumberColumn("From Node", min_value=1, step=1),
            "To": st.column_config.NumberColumn("To Node", min_value=1, step=1),
            "Thermal_Limit": st.column_config.TextColumn(
                "Thermal Limit (MW)",
                default="∞",
                help="Use a number, leave blank, or set ∞ for unconstrained flow.",
                validate=r"^\s*$|^\d+(\.\d+)?$|^[+]?∞$|^[+]?inf(inity)?$",
            ),
            "Reactance": st.column_config.NumberColumn("Reactance (p.u.)", min_value=0.0001, step=0.01, format="%.4f"),
        },
    )

prepared_nodes = _prepare_nodes_for_editor(edited_nodes)
prepared_lines = _prepare_lines_for_editor(edited_lines)
node_row_count = len(edited_nodes)
line_row_count = len(edited_lines)
rows_changed = (
    node_row_count != st.session_state.get("nodes_row_count_snapshot", node_row_count)
    or line_row_count != st.session_state.get("lines_row_count_snapshot", line_row_count)
)
st.session_state["nodes_row_count_snapshot"] = node_row_count
st.session_state["lines_row_count_snapshot"] = line_row_count
if rows_changed:
    st.session_state["draft_nodes_df"] = prepared_nodes
    st.session_state["draft_lines_df"] = prepared_lines
    st.rerun()

node_options = list(range(1, len(prepared_nodes) + 1))
if "hub_user_selected" not in st.session_state:
    st.session_state["hub_user_selected"] = False

previous_node_count = st.session_state.get("node_count_snapshot")
current_node_count = len(node_options)
if (
    previous_node_count is None
    or (current_node_count != previous_node_count and not st.session_state["hub_user_selected"])
):
    st.session_state["hub_selector"] = node_options[-1] if node_options else None

if node_options and st.session_state.get("hub_selector") not in node_options:
    st.session_state["hub_selector"] = node_options[-1]

st.session_state["node_count_snapshot"] = current_node_count

if node_options:
    st.selectbox(
        "Hub / Slack Node",
        options=node_options,
        index=node_options.index(st.session_state["hub_selector"]),
        help="The hub node is used as the PTDF reference bus and defaults to the last node entered.",
        key="hub_selector",
        on_change=_mark_hub_manual_selection,
    )
else:
    st.info("Add at least one node to enable hub/slack node selection.")

if st.button("Save Configuration", type="primary"):
    selected_hub = st.session_state.get("hub_selector", node_options[-1] if node_options else None)
    normalized_nodes, normalized_lines, normalized_hub = normalize_network_data(
        prepared_nodes,
        prepared_lines,
        selected_hub,
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
            st.session_state["draft_nodes_df"] = _prepare_nodes_for_editor(normalized_nodes)
            st.session_state["draft_lines_df"] = _prepare_lines_for_editor(normalized_lines)
            st.session_state["nodes_row_count_snapshot"] = len(st.session_state["draft_nodes_df"])
            st.session_state["lines_row_count_snapshot"] = len(st.session_state["draft_lines_df"])
            st.session_state["hub_node"] = normalized_hub
            st.session_state["network_revision"] = st.session_state.get("network_revision", 0) + 1
            st.session_state.pop("market_result", None)
            st.success("Configuration saved successfully. Go to Market Analytics to run the market clearing engine.")
    else:
        st.error(msg)
