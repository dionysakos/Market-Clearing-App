import pandas as pd
import streamlit as st


def _extract_numeric(series):
    extracted = series.astype(str).str.extract(r"(-?\d+(?:\.\d+)?)")[0]
    return pd.to_numeric(extracted, errors="coerce")


def load_default_nodes():
    """Returns an empty node dataframe for dynamic user entry."""
    return pd.DataFrame(
        {
            "Node": pd.Series(dtype="Int64"),
            "Demand": pd.Series(dtype="float64"),
            "Pmax": pd.Series(dtype="float64"),
            "Cost": pd.Series(dtype="float64"),
        }
    )


def load_default_lines():
    """Returns an empty line dataframe for dynamic user entry."""
    return pd.DataFrame(
        {
            "Line": pd.Series(dtype="Int64"),
            "From": pd.Series(dtype="Int64"),
            "To": pd.Series(dtype="Int64"),
            "Thermal_Limit": pd.Series(dtype="float64"),
            "Reactance": pd.Series(dtype="float64"),
        }
    )


def load_default_ptdf():
    """Returns an empty PTDF matrix."""
    return pd.DataFrame()


def get_default_hub_node(nodes_df=None):
    if nodes_df is None or nodes_df.empty:
        return None
    return int(nodes_df["Node"].iloc[-1])


def normalize_network_data(nodes_df, lines_df, hub_node=None):
    nodes = nodes_df.copy()
    lines = lines_df.copy()

    for column in ["Node", "Demand", "Pmax", "Cost"]:
        if column not in nodes.columns:
            nodes[column] = pd.NA
    nodes = nodes[["Node", "Demand", "Pmax", "Cost"]]
    nodes = nodes.dropna(how="all", subset=["Demand", "Pmax", "Cost", "Node"])
    nodes = nodes.reset_index(drop=True)
    nodes["Node"] = pd.Series(range(1, len(nodes) + 1), dtype="Int64")
    nodes["Demand"] = pd.to_numeric(nodes["Demand"], errors="coerce")
    nodes["Pmax"] = pd.to_numeric(nodes["Pmax"], errors="coerce")
    nodes["Cost"] = pd.to_numeric(nodes["Cost"], errors="coerce")

    for column in ["Line", "From", "To", "Thermal_Limit", "Reactance"]:
        if column not in lines.columns:
            lines[column] = pd.NA
    lines = lines[["Line", "From", "To", "Thermal_Limit", "Reactance"]]
    lines = lines.dropna(how="all", subset=["Line", "From", "To", "Thermal_Limit", "Reactance"])
    lines = lines.reset_index(drop=True)
    lines["Line"] = pd.Series(range(1, len(lines) + 1), dtype="Int64")
    lines["From"] = _extract_numeric(lines["From"]).astype("Int64")
    lines["To"] = _extract_numeric(lines["To"]).astype("Int64")
    lines["Thermal_Limit"] = pd.to_numeric(lines["Thermal_Limit"], errors="coerce")
    lines["Reactance"] = pd.to_numeric(lines["Reactance"], errors="coerce")

    normalized_hub = _extract_numeric(pd.Series([hub_node]))[0] if hub_node is not None else None
    if pd.isna(normalized_hub) or len(nodes) == 0:
        normalized_hub = get_default_hub_node(nodes)
    else:
        normalized_hub = int(normalized_hub)
        if normalized_hub not in nodes["Node"].astype(int).tolist():
            normalized_hub = get_default_hub_node(nodes)

    return nodes, lines, normalized_hub


def initialize_session_state():
    """Initializes the Streamlit session state with default data."""
    if "nodes_df" not in st.session_state:
        st.session_state["nodes_df"] = load_default_nodes()

    if "lines_df" not in st.session_state:
        st.session_state["lines_df"] = load_default_lines()

    if "hub_node" not in st.session_state:
        st.session_state["hub_node"] = get_default_hub_node(st.session_state["nodes_df"])

    try:
        nodes_df, lines_df, hub_node = normalize_network_data(
            st.session_state["nodes_df"],
            st.session_state["lines_df"],
            st.session_state.get("hub_node"),
        )
    except Exception:
        return

    st.session_state["nodes_df"] = nodes_df
    st.session_state["lines_df"] = lines_df
    st.session_state["hub_node"] = hub_node

    if "ptdf_df" not in st.session_state:
        st.session_state["ptdf_df"] = load_default_ptdf()


def validate_network_data(nodes_df, lines_df, hub_node=None):
    """Performs validation on the network data before passing it to the engine."""
    if nodes_df.empty:
        return False, "Error: At least one node must be defined."

    if lines_df.empty:
        return False, "Error: At least one transmission line must be defined."

    if nodes_df[["Demand", "Pmax", "Cost"]].isna().any().any():
        return False, "Error: Every node must have Demand, Pmax, and Cost values."

    if lines_df[["From", "To", "Thermal_Limit", "Reactance"]].isna().any().any():
        return False, "Error: Every line must have From, To, Thermal_Limit, and Reactance values."

    if (lines_df["Thermal_Limit"] < 0).any():
        return False, "Error: Thermal limits cannot be negative."

    if (lines_df["Reactance"] <= 0).any():
        return False, "Error: Line reactance must be greater than zero for DC-OPF physics to work."

    if (nodes_df["Pmax"] < 0).any() or (nodes_df["Demand"] < 0).any():
        return False, "Error: Generation limits and demands must be positive values."

    valid_nodes = set(nodes_df["Node"].dropna().astype(int).tolist())
    if hub_node is not None and int(hub_node) not in valid_nodes:
        return False, "Error: The selected hub node is not part of the node set."

    for row in lines_df.itertuples(index=False):
        if int(row.From) == int(row.To):
            return False, f"Error: Line {int(row.Line)} must connect two different nodes."
        if int(row.From) not in valid_nodes or int(row.To) not in valid_nodes:
            return False, f"Error: Line {int(row.Line)} references an undefined node."

    return True, "Data is valid."
