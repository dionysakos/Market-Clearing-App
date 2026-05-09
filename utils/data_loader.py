import pandas as pd
import streamlit as st


def _extract_numeric(series):
    extracted = series.astype(str).str.extract(r"(-?\d+(?:\.\d+)?)")[0]
    return pd.to_numeric(extracted, errors="coerce")


def assign_default_node_ids(node_series):
    numeric_nodes = pd.to_numeric(node_series, errors="coerce")
    assigned = []
    max_existing = 0

    for value in numeric_nodes:
        if pd.notna(value) and float(value).is_integer() and int(value) >= 1:
            node_id = int(value)
            assigned.append(node_id)
            if node_id > max_existing:
                max_existing = node_id
        else:
            max_existing += 1
            assigned.append(max_existing)

    return pd.Series(assigned, dtype="Int64")


def _normalize_optional_limit(value, lower_unbounded_symbol=False):
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if text == "":
        return pd.NA
    lowered = text.lower()
    if lowered in {"∞", "+∞", "inf", "+inf", "infinity", "+infinity"}:
        return pd.NA
    if lower_unbounded_symbol and lowered in {"-∞", "-inf", "-infinity"}:
        return pd.NA
    return pd.to_numeric(text, errors="coerce")


def load_default_nodes():
    """Returns an empty node dataframe for dynamic user entry."""
    return pd.DataFrame(
        {
            "Node": pd.Series(dtype="Int64"),
            "Demand": pd.Series(dtype="float64"),
            "Pmin": pd.Series(dtype="float64"),
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

    for column in ["Node", "Demand", "Pmin", "Pmax", "Cost"]:
        if column not in nodes.columns:
            nodes[column] = pd.NA
    nodes = nodes[["Node", "Demand", "Pmin", "Pmax", "Cost"]]
    nodes = nodes.dropna(how="all", subset=["Demand", "Pmin", "Pmax", "Cost", "Node"])
    nodes = nodes.reset_index(drop=True)
    nodes["Node"] = assign_default_node_ids(nodes["Node"])
    nodes["Demand"] = pd.to_numeric(nodes["Demand"], errors="coerce")
    nodes["Pmin"] = nodes["Pmin"].apply(lambda x: _normalize_optional_limit(x, lower_unbounded_symbol=True)).fillna(0.0)
    nodes["Pmax"] = nodes["Pmax"].apply(_normalize_optional_limit)
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
    lines["Thermal_Limit"] = lines["Thermal_Limit"].apply(_normalize_optional_limit)
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

    if nodes_df[["Demand", "Cost"]].isna().any().any():
        return False, "Error: Every node must have Demand and Cost values."

    if lines_df[["From", "To", "Reactance"]].isna().any().any():
        return False, "Error: Every line must have From, To, and Reactance values."

    thermal_defined = lines_df["Thermal_Limit"].dropna()
    if (thermal_defined < 0).any():
        return False, "Error: Thermal limits cannot be negative."

    if (lines_df["Reactance"] <= 0).any():
        return False, "Error: Line reactance must be greater than zero for DC-OPF physics to work."

    if (nodes_df["Demand"] < 0).any():
        return False, "Error: Demands must be non-negative values."
    pmin_defined = nodes_df["Pmin"].dropna()
    pmax_defined = nodes_df["Pmax"].dropna()
    if (pmax_defined < 0).any():
        return False, "Error: Pmax must be non-negative when provided."
    if (pmin_defined < 0).any():
        return False, "Error: Pmin must be non-negative when provided."
    comparable_bounds = nodes_df["Pmin"].notna() & nodes_df["Pmax"].notna()
    if (nodes_df.loc[comparable_bounds, "Pmin"] > nodes_df.loc[comparable_bounds, "Pmax"]).any():
        return False, "Error: Pmin must be less than or equal to Pmax for every node."

    valid_nodes = set(nodes_df["Node"].dropna().astype(int).tolist())
    if hub_node is not None and int(hub_node) not in valid_nodes:
        return False, "Error: The selected hub node is not part of the node set."

    for row in lines_df.itertuples(index=False):
        if int(row.From) == int(row.To):
            return False, f"Error: Line {int(row.Line)} must connect two different nodes."
        if int(row.From) not in valid_nodes or int(row.To) not in valid_nodes:
            return False, f"Error: Line {int(row.Line)} references an undefined node."

    return True, "Data is valid."
