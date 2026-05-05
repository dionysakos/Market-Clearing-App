import pandas as pd
import streamlit as st

def load_default_nodes():
    """Returns the default dataframe for the 3-bus network nodes."""
    return pd.DataFrame({
        'Node': ['node1', 'node2', 'node3'],
        'Max_Demand': [0.0, 100.0, 200.0],
        'Bid_Price': [0.0, 500.0, 500.0], # €/MWh consumers are willing to pay
        'Pmax': [400.0, 400.0, 400.0],
        'Cost': [40.0, 80.0, 140.0]       # €/MWh generation cost
    })

def load_default_lines():
    """Returns the default dataframe for the 3-bus network lines."""
    return pd.DataFrame({
        'Line': ['L_12', 'L_23', 'L_13'],
        'From': ['node1', 'node2', 'node1'],
        'To': ['node2', 'node3', 'node3'],
        'Thermal_Limit': [50.0, 50.0, 50.0],
        'Reactance': [0.2, 0.05, 0.2]     # X values
    })

def load_default_ptdf():
    """
    Returns the default PTDF matrix for the 3-bus system.
    Note: node3 is considered the hub node.
    """
    ptdf_data = {
        'node1': [1/3, 1/3, 2/3],   # Shift factors for injection at node1
        'node2': [-1/3, 2/3, 1/3],  # Shift factors for injection at node2
        'node3': [0.0, 0.0, 0.0]    # Hub node
    }
    return pd.DataFrame(ptdf_data, index=['L_12', 'L_23', 'L_13'])

def initialize_session_state():
    """
    Initializes the Streamlit session state with default data
    """
    if 'nodes_df' not in st.session_state:
        st.session_state['nodes_df'] = load_default_nodes()
        
    if 'lines_df' not in st.session_state:
        st.session_state['lines_df'] = load_default_lines()
        
    if 'ptdf_df' not in st.session_state:
        st.session_state['ptdf_df'] = load_default_ptdf()

def validate_network_data(nodes_df, lines_df):
    """
    Performs basic validation on the user-edited data before passing it to the engine.
    Checks include:
    - No negative thermal limits on lines
    - No negative generation limits or demand on nodes
    - Lines must reference existing nodes
    """
    # negative thermal limits
    if (lines_df['Thermal_Limit'] < 0).any():
        return False, "Error: Thermal limits cannot be negative."
    
    # negative generation limits or demand
    if (nodes_df['Pmax'] < 0).any() or (nodes_df['Max_Demand'] < 0).any():
        return False, "Error: Generation limits and Demands must be positive values."
        
    # lines reference non-existent nodes
    valid_nodes = set(nodes_df['Node'])
    for _, row in lines_df.iterrows():
        if row['From'] not in valid_nodes or row['To'] not in valid_nodes:
            return False, f"Error: Line {row['Line']} references an undefined node."

    return True, "Data is valid."