import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

LMP_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "optigrid_lmp",
    ["#0d2f1f", "#157347", "#22c55e", "#f59e0b"],
)


def get_node_color(lmp, min_lmp, max_lmp):
    if max_lmp == min_lmp:
        return LMP_CMAP(0.6)

    norm = (lmp - min_lmp) / (max_lmp - min_lmp)
    return LMP_CMAP(0.12 + 0.8 * norm)


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
    for _, row in nodes_df.iterrows():
        node_id = int(row["Node"])
        graph.add_node(node_id, demand=row.get("Demand", 0.0), lmp=lmps.get(node_id, 0.0))

    for _, row in lines_df.iterrows():
        line_id = int(row["Line"])
        from_node = int(row["From"])
        to_node = int(row["To"])
        flow = float(flow_results.get(line_id, 0.0))
        raw_limit = row.get("Thermal_Limit", pd.NA)
        limit = np.nan if pd.isna(raw_limit) else float(raw_limit)
        graph.add_edge(from_node, to_node, line_id=line_id, flow=flow, limit=limit)

    fig, ax = plt.subplots(figsize=(12, 8), dpi=220)
    fig.patch.set_facecolor("#07110c")
    ax.set_facecolor("#07110c")
    ax.axis("off")

    for node in graph.nodes:
        x, y = positions[node]
        lmp_value = lmps.get(node, 0.0)
        node_color = get_node_color(lmp_value, min_lmp, max_lmp)
        node_size = 2400 if node == hub else 2050

        # Single clean node body.
        ax.scatter(
            x,
            y,
            s=node_size,
            c=[node_color],
            edgecolors="#f8fafc",
            linewidths=1.1,
            alpha=0.85,
            zorder=3,
        )
        ax.text(
            x,
            y,
            f"{node}",
            ha="center",
            va="center",
            fontsize=14.8,
            fontweight="bold",
            fontfamily="DejaVu Sans",
            color="#f8fafc",
            zorder=6,
        )
        ax.text(
            x,
            y - 0.29,
            f"€{lmp_value:.2f}/MWh",
            ha="center",
            va="center",
            fontsize=8.8,
            fontfamily="DejaVu Sans",
            color="#e2e8f0",
            bbox={
                "boxstyle": "round,pad=0.24,rounding_size=0.28",
                "fc": "#10241a",
                "ec": "none",
                "lw": 0.0,
                "alpha": 0.7,
            },
            zorder=5,
        )

    edge_items = list(graph.edges(data=True, keys=True))
    edge_count = len(edge_items)
    for edge_index, (from_node, to_node, _, data) in enumerate(edge_items):
        flow = data["flow"]
        limit = data["limit"]
        has_limit = not pd.isna(limit)
        is_congested = has_limit and limit > 0 and abs(flow) >= 0.999 * limit
        edge_color = "#f97316" if is_congested else "#22c55e"
        base_width = 2.0 if is_congested else 1.6

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

        # Neon halo layers.
        glow_layers = (
            ((10.5, 0.11), (7.0, 0.2), (4.6, 0.34))
            if not is_congested
            else ((8.0, 0.08), (5.2, 0.16), (3.5, 0.25))
        )
        for glow_width, glow_alpha in glow_layers:
            ax.annotate(
                "",
                xy=end,
                xytext=start,
                arrowprops={
                    "arrowstyle": "-",
                    "color": edge_color,
                    "lw": glow_width,
                    "shrinkA": 28,
                    "shrinkB": 28,
                    "alpha": glow_alpha,
                },
                zorder=1,
            )

        # Core directional line.
        ax.annotate(
            "",
            xy=end,
            xytext=start,
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": edge_color,
                    "lw": base_width,
                    "shrinkA": 28,
                    "shrinkB": 28,
                    "mutation_scale": 12.5,
                    "alpha": 1.0,
                },
                zorder=3,
            )
        ax.text(
            label_position[0],
            label_position[1],
            f"{abs(flow):.1f} MW" + (" !" if is_congested else ""),
            ha="center",
            va="center",
            fontsize=8.7,
            fontfamily="DejaVu Sans",
            color="#ffffff",
            zorder=6,
        )

    if nodes:
        xs = [positions[node][0] for node in nodes]
        ys = [positions[node][1] for node in nodes]
        pad = 0.65
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(min(ys) - pad, max(ys) + pad)

    fig.tight_layout()
    return fig
