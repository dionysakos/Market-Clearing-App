import streamlit as st
import pandas as pd
from utils.network_tools import calculate_ptdf
from utils.engine import run_market_clearing  
from utils.visualization import draw_network_graph

st.markdown(
    """
    <style>
        .kpi-card {
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 8px;
            padding: 0.85rem 0.9rem;
            background: rgba(255, 255, 255, 0.03);
            min-height: 112px;
        }
        .kpi-label {
            font-size: 0.82rem;
            color: #cbd5e1;
            margin-bottom: 0.28rem;
        }
        .kpi-value {
            font-size: 1.24rem;
            font-weight: 700;
            line-height: 1.3;
        }
        .kpi-delta {
            font-size: 0.8rem;
            margin-top: 0.3rem;
        }
        .kpi-positive {
            color: #22c55e;
        }
        .kpi-negative {
            color: #ef4444;
        }
        .kpi-neutral {
            color: #e2e8f0;
        }
        .kpi-warning {
            color: #f59e0b;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def _kpi_card(label, value, tone="neutral", delta_text=None, delta_html=None):
    tone_class = {
        "positive": "kpi-positive",
        "negative": "kpi-negative",
        "neutral": "kpi-neutral",
        "warning": "kpi-warning",
    }.get(tone, "kpi-neutral")
    if delta_html is not None:
        delta_block = f"<div class='kpi-delta'>{delta_html}</div>"
    elif delta_text:
        delta_block = f"<div class='kpi-delta {tone_class}'>{delta_text}</div>"
    else:
        delta_block = ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value {tone_class}">{value}</div>
            {delta_block}
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title("Market Analytics")
st.caption("Solve the market clearing problem and inspect system-wide and nodal pricing outputs.")

if 'nodes_df' not in st.session_state or 'lines_df' not in st.session_state:

    st.warning("No data found. Please navigate to the Network Configuration page to define your network.")
    st.stop() 

nodes_df = st.session_state['nodes_df']
lines_df = st.session_state['lines_df']
if nodes_df.empty or lines_df.empty:
    st.warning("No configured network found. Please define nodes and transmission lines in Network Configuration.")
    st.stop()
hub_node = st.session_state.get("hub_node", nodes_df["Node"].iloc[-1])

# Dynamically calculate PTDF based on the user's grid topology
try:
    ptdf_df = calculate_ptdf(nodes_df, lines_df, ref_node=hub_node)
except Exception as e:
    st.error(f"Error calculating PTDF matrix. Please check your network topology and Reactances. Details: {e}")
    st.stop()

def _stable_value(value):
    return None if pd.isna(value) else float(value) if isinstance(value, (int, float)) else value


network_signature = (
    tuple(tuple(_stable_value(v) for v in row) for row in nodes_df[["Node", "Demand", "Pmin", "Pmax", "Cost"]].itertuples(index=False, name=None)),
    tuple(tuple(_stable_value(v) for v in row) for row in lines_df[["Line", "From", "To", "Thermal_Limit", "Reactance"]].itertuples(index=False, name=None)),
    int(hub_node),
)
if st.session_state.get("market_signature") != network_signature:
    st.session_state.pop("market_result", None)
    st.session_state["market_signature"] = network_signature

if st.button("Execute Market Clearing", type="primary"):
    with st.spinner("Running market clearing optimization..."):
        result = run_market_clearing(
            nodes_df, lines_df, ptdf_df
        )
    st.session_state["market_result"] = result

if "market_result" in st.session_state:
    status, cost, gen, flows, lmps, congestion, system_lambda = st.session_state["market_result"]
    if status == "Optimal" and all(value is not None for value in [cost, gen, flows, lmps, congestion, system_lambda]):
        st.success("The problem was solved optimally!")

        congested_lines = sum(
            (
                not pd.isna(row["Thermal_Limit"])
                and abs(float(flows.get(int(row["Line"]), 0.0))) >= 0.999 * float(row["Thermal_Limit"])
            )
            for _, row in lines_df.iterrows()
        )
        st.subheader("Executive Metrics")
        summary_columns = st.columns(4)
        with summary_columns[0]:
            _kpi_card("Optimization Status", status, tone="positive", delta_text="Solver reached optimum")
        with summary_columns[1]:
            _kpi_card("System λ (SMP)", f"€ {system_lambda:,.2f}/MWh", tone="neutral")
        with summary_columns[2]:
            _kpi_card("Total Generation Cost", f"€ {cost:,.2f}", tone="positive")
        with summary_columns[3]:
            _kpi_card(
                "Congested Lines",
                f"{congested_lines}",
                tone="warning" if congested_lines > 0 else "positive",
                delta_text="At thermal limit",
            )
        
        st.divider()
        
        st.subheader("Nodal Pricing")
        st.caption("Each node card shows the locational marginal price and its dispatch/demand snapshot.")
        for start in range(0, len(nodes_df), 4):
            node_columns = st.columns(min(4, len(nodes_df) - start))
            for column, (_, row) in zip(node_columns, nodes_df.iloc[start:start + 4].iterrows()):
                node_id = int(row["Node"])
                node_lmp = float(lmps.get(node_id, 0.0))
                pmin_display = "-∞" if pd.isna(row["Pmin"]) else f"{float(row['Pmin']):.1f}"
                with column:
                    _kpi_card(
                        f"Node {node_id}",
                        f"€ {node_lmp:,.2f}/MWh",
                        tone="neutral",
                        delta_html=(
                            f"<span class='kpi-positive'>Generation {gen.get(node_id, 0):,.1f} MW (Pmin {pmin_display})</span> | "
                            f"<span class='kpi-negative'>Demand {row['Demand']:.1f} MW</span>"
                        ),
                    )
        
        st.divider()
        
        st.subheader("Transmission Line Flows")
        st.caption("Static flow labels keep the inspection view stable and readable.")

        for start in range(0, len(lines_df), 4):
            line_columns = st.columns(min(4, len(lines_df) - start))
            for column, (_, row) in zip(line_columns, lines_df.iloc[start:start + 4].iterrows()):
                line_id = int(row["Line"])
                flow_value = float(flows.get(line_id, 0))
                line_limit = row["Thermal_Limit"]
                has_limit = not pd.isna(line_limit)
                line_limit_value = float(line_limit) if has_limit else None
                loading_pct = (abs(flow_value) / line_limit_value * 100) if has_limit and line_limit_value > 0 else 0.0
                is_congested = abs(flow_value) >= 0.999 * line_limit_value if has_limit and line_limit_value > 0 else False
                limit_label = f"{line_limit_value:.1f} MW" if has_limit else "∞"
                with column:
                    _kpi_card(
                        f"Line {line_id}",
                        f"{flow_value:.1f} MW",
                        tone="warning" if is_congested else "positive",
                        delta_text=f"From {int(row['From'])} to {int(row['To'])} | Loading {loading_pct:.1f}% of {limit_label}",
                    )

        st.divider()
        st.pyplot(
            draw_network_graph(nodes_df, lines_df, flows, lmps, congestion, hub_node=hub_node),
            use_container_width=True,
        )

        st.divider()

        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.write("Node Summary")
            res_nodes = []
            for n in nodes_df['Node']:
                pmin_val = nodes_df.loc[nodes_df['Node'] == n, 'Pmin'].iloc[0]
                pmax_val = nodes_df.loc[nodes_df['Node'] == n, 'Pmax'].iloc[0]
                res_nodes.append({
                    "Node": int(n),
                    "LMP (EUR/MWh)": lmps.get(n, 0),
                    "Generation (MW)": gen.get(n, 0),
                    "Pmin (MW)": "-∞" if pd.isna(pmin_val) else float(pmin_val),
                    "Pmax (MW)": "∞" if pd.isna(pmax_val) else float(pmax_val),
                    "Demand (MW)": float(nodes_df.loc[nodes_df['Node'] == n, 'Demand'].iloc[0]),
                })
            st.dataframe(pd.DataFrame(res_nodes), use_container_width=True)
            
        with col_res2:
            st.write("Line Summary")
            res_lines = []
            for l in lines_df['Line']:
                res_lines.append({
                    "Line": int(l),
                    "Flow (MW)": flows.get(l, 0),
                    "Congestion Cost (+)": congestion.get(l, {}).get('lambda_str', 0),
                    "Congestion Cost (-)": congestion.get(l, {}).get('lambda_opp', 0),
                })
            st.dataframe(pd.DataFrame(res_lines), use_container_width=True)

    else:
        st.error(f"The optimization failed. Solver Status: {status}")
else:
    st.info("Execute market clearing to generate KPIs and line flow metrics.")
