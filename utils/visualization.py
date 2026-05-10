import math

import pandas as pd
import plotly.graph_objects as go


def _build_fixed_positions(nodes):
    if not nodes:
        return {}

    radius = 1.9
    angle_step = 2 * math.pi / len(nodes)
    start_angle = -math.pi / 2
    return {
        node: (
            radius * math.cos(start_angle + index * angle_step),
            radius * math.sin(start_angle + index * angle_step),
        )
        for index, node in enumerate(nodes)
    }


def _node_orb_color(lmp, min_lmp, max_lmp):
    if max_lmp <= min_lmp:
        return "#45c970"
    ratio = max(0.0, min(1.0, (float(lmp) - min_lmp) / (max_lmp - min_lmp)))
    if ratio < 0.35:
        return "#28b36f"
    if ratio < 0.7:
        return "#46d47a"
    return "#f6a637"


def draw_network_graph(
    nodes_df,
    lines_df,
    flow_results,
    lmps,
    generation_results=None,
    congestion_prices=None,
    hub_node=None,
    system_lambda=None,
):
    del hub_node  # Reserved for future layout variants.
    del congestion_prices  # Reserved for future line hover details.
    del system_lambda  # Reserved for future decomposition display.

    nodes = list(dict.fromkeys(nodes_df["Node"].astype(int).tolist()))
    positions = _build_fixed_positions(nodes)
    demand_by_node = nodes_df.groupby("Node", sort=False)["Demand"].sum().astype(float).to_dict()

    min_lmp = min(lmps.values()) if lmps else 0.0
    max_lmp = max(lmps.values()) if lmps else 1.0

    fig = go.Figure()

    for line_index, (_, row) in enumerate(lines_df.iterrows()):
        from_node = int(row["From"])
        to_node = int(row["To"])
        flow = float(flow_results.get(int(row["Line"]), 0.0))
        raw_limit = row.get("Thermal_Limit", pd.NA)
        has_limit = not pd.isna(raw_limit)
        limit = float(raw_limit) if has_limit else None
        is_congested = bool(has_limit and limit > 0 and abs(flow) >= 0.999 * limit)
        line_color = "#ff7a00" if is_congested else "#00e676"

        x0, y0 = positions[from_node]
        x1, y1 = positions[to_node]

        for glow_width, glow_opacity in ((18, 0.06), (11, 0.12), (7, 0.2)):
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line={"color": line_color, "width": glow_width},
                    opacity=glow_opacity,
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line={"color": line_color, "width": 4},
                opacity=1.0,
                hoverinfo="skip",
                showlegend=False,
            )
        )

        dx = x1 - x0
        dy = y1 - y0
        length = math.hypot(dx, dy)
        if length > 0:
            ux = dx / length
            uy = dy / length
            mid_x = 0.5 * (x0 + x1)
            mid_y = 0.5 * (y0 + y1)
            side = 1 if line_index % 2 == 0 else -1
            label_offset = 0.2
            label_x = mid_x - uy * label_offset * side
            label_y = mid_y + ux * label_offset * side
            fig.add_annotation(
                x=label_x,
                y=label_y,
                text=f"{flow:.1f} MW",
                showarrow=False,
                xanchor="center",
                yanchor="middle",
                font={
                    "family": "Inter, Roboto Mono, Arial, sans-serif",
                    "size": 10,
                    "color": "#f8fafc",
                },
                bgcolor="rgba(5, 26, 18, 0.9)",
                bordercolor="rgba(148, 163, 184, 0.25)",
                borderwidth=1,
                borderpad=2,
            )

        arrow_x = x0 + 0.72 * (x1 - x0)
        arrow_y = y0 + 0.72 * (y1 - y0)
        if abs(x1 - x0) >= abs(y1 - y0):
            arrow_symbol = "triangle-right" if x1 >= x0 else "triangle-left"
        else:
            arrow_symbol = "triangle-up" if y1 >= y0 else "triangle-down"
        fig.add_trace(
            go.Scatter(
                x=[arrow_x],
                y=[arrow_y],
                mode="markers",
                marker={
                    "symbol": arrow_symbol,
                    "size": 10.5,
                    "color": line_color,
                    "line": {"width": 0},
                },
                opacity=0.95,
                hoverinfo="skip",
                showlegend=False,
            )
        )

    node_x = []
    node_y = []
    node_text = []
    node_custom = []
    node_sizes = []
    node_colors = []
    for node in nodes:
        x, y = positions[node]
        lmp_value = float(lmps.get(node, 0.0))
        demand = float(demand_by_node.get(node, 0.0))
        generation = float((generation_results or {}).get(node, 0.0))
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"N{node}")
        node_custom.append([node, demand, generation, lmp_value])
        node_sizes.append(28)
        node_colors.append(_node_orb_color(lmp_value, min_lmp, max_lmp))

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            marker={
                "size": [42 for _ in node_sizes],
                "color": "#80ffb9",
                "opacity": 0.15,
                "line": {"width": 0},
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="middle center",
            textfont={
                "family": "Inter, Roboto Mono, Arial, sans-serif",
                "size": 12,
                "color": "#f8fafc",
            },
            marker={
                "size": node_sizes,
                "color": node_colors,
                "opacity": 0.92,
                "line": {"color": "#d9fbe8", "width": 1.6},
            },
            customdata=node_custom,
            hovertemplate=(
                "<b>Node %{customdata[0]}</b><br>"
                "Total Demand: %{customdata[1]:.1f} MW<br>"
                "Generation: %{customdata[2]:.1f} MW<br>"
                "LMP: €%{customdata[3]:.2f}/MWh"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    fig.update_layout(
        paper_bgcolor="#051a12",
        plot_bgcolor="#051a12",
        margin={"l": 12, "r": 12, "t": 12, "b": 12},
        height=620,
        xaxis={
            "visible": False,
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "fixedrange": True,
        },
        yaxis={
            "visible": False,
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "scaleanchor": "x",
            "scaleratio": 1,
            "fixedrange": True,
        },
        hovermode="closest",
        hoverlabel={
            "bgcolor": "rgba(2, 12, 8, 0.96)",
            "bordercolor": "#00e676",
            "font": {
                "family": "Inter, Roboto Mono, Arial, sans-serif",
                "size": 12,
                "color": "#f8fafc",
            },
            "align": "left",
        },
        font={"family": "Inter, Roboto Mono, Arial, sans-serif", "color": "#e2e8f0", "size": 11},
        dragmode=False,
    )

    if node_x and node_y:
        pad = 0.9
        fig.update_xaxes(range=[min(node_x) - pad, max(node_x) + pad])
        fig.update_yaxes(range=[min(node_y) - pad, max(node_y) + pad])

    return fig
