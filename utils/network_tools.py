import numpy as np
import pandas as pd

def calculate_ptdf(nodes_df, lines_df, ref_node=None, ref_node_idx=-1):
    """
    Calculates the Power Transfer Distribution Factor (PTDF) matrix.
    Uses the formula: PTDF = B_line * inv(B_bus_truncated)
    
    :param nodes_df: DataFrame containing the nodes.
    :param lines_df: DataFrame containing the lines (must have 'From', 'To', 'Reactance').
    :param ref_node: Optional node identifier to use as the reference (slack) bus.
    :param ref_node_idx: Index of the reference (slack) bus. Defaults to the last node.
    :return: A pandas DataFrame representing the PTDF matrix.
    """
    nodes = nodes_df['Node'].tolist()
    lines = lines_df['Line'].tolist()
    num_nodes = len(nodes)
    num_lines = len(lines)
    
    # Map node names to their index
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # Initialize M matrix (B_line) : L x N
    M = np.zeros((num_lines, num_nodes))
    # Initialize T matrix (B_bus) : N x N
    T = np.zeros((num_nodes, num_nodes))

    for k, (_, row) in enumerate(lines_df.iterrows()):
        u = node_to_idx[row['From']]
        v = node_to_idx[row['To']]
        
        # Susceptance is 1 / Reactance
        # Fallback to 0.001 if reactance is 0 to avoid DivisionByZero
        x = row.get('Reactance', 0.1)
        x = 0.1 if pd.isna(x) else float(x)
        x = x if x != 0 else 0.001 
        b = 1.0 / x

        # Populate M (Line Susceptance Matrix)
        M[k, u] = b
        M[k, v] = -b

        # Populate T (Bus Susceptance Matrix - Laplacian)
        T[u, u] += b
        T[v, v] += b
        T[u, v] -= b
        T[v, u] -= b

    # Determine reference node index
    if ref_node is not None:
        if ref_node in nodes:
            ref_idx = nodes.index(ref_node)
        elif isinstance(ref_node, int) and 0 <= ref_node < num_nodes:
            ref_idx = ref_node
        else:
            raise ValueError(f"Reference node {ref_node} is not part of the network.")
    else:
        ref_idx = num_nodes - 1 if ref_node_idx == -1 else ref_node_idx
    non_ref_indices = [i for i in range(num_nodes) if i != ref_idx]

    # Truncate matrices by removing the reference node column/row
    T_trunc = T[np.ix_(non_ref_indices, non_ref_indices)]
    M_trunc = M[:, non_ref_indices]

    # Calculate PTDF_trunc = M_trunc @ inv(T_trunc)
    T_inv = np.linalg.inv(T_trunc)
    PTDF_trunc = M_trunc @ T_inv

    # Reconstruct the full PTDF matrix (Reference node column remains 0)
    PTDF = np.zeros((num_lines, num_nodes))
    for i, col_idx in enumerate(non_ref_indices):
        PTDF[:, col_idx] = PTDF_trunc[:, i]

    return pd.DataFrame(PTDF, index=lines, columns=nodes)
