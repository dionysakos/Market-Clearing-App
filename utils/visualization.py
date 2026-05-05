import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

def get_node_color(lmp, min_lmp, max_lmp):
    if max_lmp == min_lmp:
        return "#2ECC71" 
    
    norm = (lmp - min_lmp) / (max_lmp - min_lmp)
    
    r = int(255 * norm)
    g = int(255 * (1 - norm))
    b = 0
    return f"#{r:02x}{g:02x}{b:02x}"

def draw_network_graph(nodes_df, lines_df, flow_results, lmps, congestion_prices=None):
    nodes = []
    edges = []
    
    min_lmp = min(lmps.values()) if lmps else 0
    max_lmp = max(lmps.values()) if lmps else 0

    # ----- NODES -----
    for _, row in nodes_df.iterrows():
        node_id = str(row['Node'])
        lmp_val = lmps.get(node_id, 0.0)
        
        demand = row.get('Demand', row.get('Max_Demand', 0))
        
        hover_text = (f"Κόμβος: {node_id}\n"
                      f"LMP: {lmp_val:.2f} €/MWh\n"
                      f"Ζήτηση: {demand} MW")
        
        nodes.append(Node(
            id=node_id,
            label=f"{node_id}\n{lmp_val:.2f}€",
            size=25,
            color=get_node_color(lmp_val, min_lmp, max_lmp),
            title=hover_text,
            shape="dot"
        ))

    # ----- EDGES -----
    for _, row in lines_df.iterrows():
        line_id = str(row['Line'])
        limit = row.get('Thermal_Limit', 9999)
        flow = flow_results.get(line_id, 0.0)
        
        if 'From' in row and 'To' in row:
            from_node, to_node = str(row['From']), str(row['To'])
        else:
            parts = line_id.replace('L_', '').split('_')
            from_node, to_node = parts, parts[2] if len(parts) > 1 else parts

        # we consider a line congested if flow is very close to its limit
        is_congested = abs(flow) >= 0.999 * limit
        
        edge_color = "#FF0000" if is_congested else "#A0A0A0" # Κόκκινο στη συμφόρηση, Γκρι αλλιώς
        edge_width = 4 if is_congested else 2
        
        cong_info = ""
        if congestion_prices and line_id in congestion_prices:
            l_str = congestion_prices[line_id]['lambda_str']
            l_opp = congestion_prices[line_id]['lambda_opp']
            cong_info = f"\nCongestion Cost (+): {l_str:.2f} €\nCongestion Cost (-): {l_opp:.2f} €"

        hover_text = (f"Γραμμή: {line_id}\n"
                      f"Ροή: {flow:.2f} MW\n"
                      f"Όριο: {limit} MW" + cong_info)
        
        edges.append(Edge(
            source=from_node,
            target=to_node,
            label=f"{flow:.1f} MW",
            color=edge_color,
            width=edge_width,
            title=hover_text
        ))

    # --CONFIG OF GRAPH -----
    config = Config(
        width="100%",  
        height=600,
        directed=True, 
        physics=True,          
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False,
        linkLength=150
    )

    return agraph(nodes=nodes, edges=edges, config=config)