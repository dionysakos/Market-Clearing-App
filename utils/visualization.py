import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

NODE_CMAP = mpl.colormaps["PuBuGn"]


def get_node_color(lmp, min_lmp, max_lmp):
    if max_lmp == min_lmp:
        return NODE_CMAP(0.6)

    norm = (lmp - min_lmp) / (max_lmp - min_lmp)
    # Keep nodal shading informative without yellow tones.
    return NODE_CMAP(0.25 + 0.65 * norm)


def _build_fixed_positions(nodes, hub_node=None):
    positions = {}
    if not nodes:
        return positions

    ordered_nodes = list(nodes)
    radius = 1.9
    angle_step = 2 * math.pi / len(ordered_nodes)
    start_angle = -math.pi / 2

    for index, node in enumerate(ordered_nodes):
        angle = start_angle + index * angle_step
        positions[node] = (radius * math.cos(angle), radius * math.sin(angle))

    return positions

def draw_network_graph(nodes_df, lines_df, flow_results, lmps, congestion_prices=None, hub_node=None):
    graph = nx.MultiDiGraph()
    nodes = list(nodes_df["Node"].astype(int))
    hub = hub_node if hub_node in nodes else (nodes[-1] if nodes else None)
    positions = _build_fixed_positions(nodes, hub_node=hub)

    min_lmp = min(lmps.values()) if lmps else 0.0
    max_lmp = max(lmps.values()) if lmps else 1.0
    norm = mpl.colors.Normalize(vmin=min_lmp, vmax=max_lmp if max_lmp != min_lmp else min_lmp + 1.0)

    for _, row in nodes_df.iterrows():
        node_id = int(row["Node"])
        graph.add_node(node_id, demand=row.get("Demand", 0.0), lmp=lmps.get(node_id, 0.0))

    for _, row in lines_df.iterrows():
        line_id = int(row["Line"])
        from_node = int(row["From"])
        to_node = int(row["To"])
        flow = float(flow_results.get(line_id, 0.0))
        limit = float(row.get("Thermal_Limit", 0.0))
        graph.add_edge(from_node, to_node, line_id=line_id, flow=flow, limit=limit)

    fig, ax = plt.subplots(figsize=(12, 8), dpi=220)
    fig.patch.set_facecolor("#0b1020")
    ax.set_facecolor("#0b1020")
    ax.axis("off")

    for node in graph.nodes:
        x, y = positions[node]
        lmp_value = lmps.get(node, 0.0)
        node_color = get_node_color(lmp_value, min_lmp, max_lmp)
        node_size = 2600 if node == hub else 2200
        # Soft halo to make nodes pop against the dark background.
        ax.scatter(
            x,
            y,
            s=node_size + 440,
            c=["#7dd3fc"],
            edgecolors="none",
            alpha=0.13,
            zorder=2,
        )
        ax.scatter(
            x,
            y,
            s=node_size,
            c=[node_color],
            edgecolors="#e2e8f0",
            linewidths=2.2,
            zorder=3,
        )
        ax.text(
            x,
            y + 0.12,
            f"{node}",
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
            color="#ffffff",
            zorder=4,
        )
        ax.text(
            x,
            y - 0.28,
            f"€{lmp_value:.2f}/MWh",
            ha="center",
            va="center",
            fontsize=9,
            color="#f8fafc",
            bbox={"boxstyle": "round,pad=0.28", "fc": "#0f172a", "ec": "#334155", "lw": 0.7, "alpha": 0.94},
            zorder=4,
        )

    edge_items = list(graph.edges(data=True, keys=True))
    edge_count = len(edge_items)
    for edge_index, (from_node, to_node, _, data) in enumerate(edge_items):
        flow = data["flow"]
        limit = data["limit"]
        is_congested = limit > 0 and abs(flow) >= 0.999 * limit
        edge_color = "#f97316" if is_congested else "#22c55e"
        edge_width = 2.6 if abs(flow) >= 0.999 * limit else 1.8

        actual_from = from_node if flow >= 0 else to_node
        actual_to = to_node if flow >= 0 else from_node
        start = np.array(positions[actual_from])
        end = np.array(positions[actual_to])
        vector = end - start
        distance = np.linalg.norm(vector) or 1.0
        unit = vector / distance
        spread = ((edge_index % 3) - 1) * 0.08 if edge_count > 1 else 0.0
        label_offset = np.array([-unit[1], unit[0]]) * (0.12 + spread)
        label_position = (start + end) / 2 + label_offset

        ax.annotate(
            "",
            xy=end,
            xytext=start,
            arrowprops={
                "arrowstyle": "-|>",
                "color": edge_color,
                "lw": edge_width,
                "shrinkA": 28,
                "shrinkB": 28,
                "mutation_scale": 14,
                "alpha": 0.95,
            },
            zorder=2,
        )
        ax.text(
            label_position[0],
            label_position[1],
            f"{abs(flow):.1f} MW",
            ha="center",
            va="center",
            fontsize=9,
            color="#f8fafc",
            bbox={"boxstyle": "round,pad=0.22", "fc": "#0f172a", "ec": "#334155", "lw": 0.65, "alpha": 0.93},
            zorder=5,
        )

    if nodes:
        xs = [positions[node][0] for node in nodes]
        ys = [positions[node][1] for node in nodes]
        pad = 0.65
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(min(ys) - pad, max(ys) + pad)

    sm = mpl.cm.ScalarMappable(cmap=NODE_CMAP, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.028, pad=0.02)
    cbar.set_label("LMP (€/MWh)", color="#e5eefc")
    cbar.ax.yaxis.set_tick_params(color="#e5eefc")
    plt.setp(cbar.ax.get_yticklabels(), color="#e5eefc")

    fig.tight_layout()
    return fig
