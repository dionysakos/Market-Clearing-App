import pandas as pd
import pulp as pu

def run_market_clearing(nodes_df, lines_df, ptdf_df, solver_path=None):
    """
    We run DC-OPF using PTDFs.
    Τhe model of DC-OPF is formulated as descirbed in Anthony Papavasiliou's Book as follows:
    
    :param nodes_df: ['Node', 'Demand', 'Pmin', 'Pmax', 'Cost']
    :param lines_df: ['Line', 'Thermal_Limit']
    :param ptdf_df:  PTDFs (Index=Line, Columns=Nodes)
    :param solver_path: Optional path for the CBC solver
    :return: status, total_cost, gen_results, flow_results, lmps, congestion_prices, system_lambda
    """
    
    # Solver 
    if solver_path:
        solver = pu.COIN_CMD(path=solver_path, msg=0, mip=False)
    else:
        solver = pu.PULP_CBC_CMD(msg=0, mip=False)

    prob = pu.LpProblem("Economic_Dispatch_with_Constraints", pu.LpMinimize)

    p = {} # Generation per generator row
    r = {} # Net Injection per node
    f = {} # Power Flow per line

    generator_specs = []
    for gen_idx, row in nodes_df.iterrows():
        node = int(row['Node'])
        pmin = None if pd.isna(row['Pmin']) else float(row['Pmin'])
        pmax = None if pd.isna(row['Pmax']) else float(row['Pmax'])
        cost = float(row['Cost'])
        demand = float(row['Demand'])
        generator_specs.append(
            {
                "gen_id": gen_idx + 1,
                "node": node,
                "pmin": pmin,
                "pmax": pmax,
                "cost": cost,
                "demand": demand,
            }
        )

    unique_nodes = list(dict.fromkeys(spec["node"] for spec in generator_specs))
    demand_by_node = (
        nodes_df.groupby("Node", sort=False)["Demand"].sum().astype(float).to_dict()
    )

    # Decision Variables
    for spec in generator_specs:
        gen_id = spec["gen_id"]
        p[gen_id] = pu.LpVariable(
            f"p_gen_{gen_id}_n_{spec['node']}",
            lowBound=spec["pmin"],
            upBound=spec["pmax"],
            cat=pu.LpContinuous,
        )

    for node in unique_nodes:
        r[node] = pu.LpVariable(f"r_{node}", cat=pu.LpContinuous)

    for _, row in lines_df.iterrows():
        line = row['Line']
        f[line] = pu.LpVariable(f"f_{line}", cat=pu.LpContinuous)

    # Objective Function 
    prob += pu.lpSum([p[spec["gen_id"]] * spec["cost"] for spec in generator_specs]), "Total_Cost"

    # Constraints

    # Nodal Power Balance: Σ generation at node - r_i = demand_i
    for node in unique_nodes:
        node_generation = pu.lpSum(
            [p[spec["gen_id"]] for spec in generator_specs if spec["node"] == node]
        )
        prob += node_generation - r[node] == demand_by_node.get(node, 0.0), f"lmp_{node}"

    # Total Injection Balance: sum(r_i) = 0 (Dual Variable: -φ)
    prob += pu.lpSum([r[node] for node in unique_nodes]) == 0, "minus_phi"

    # Flow from PTDFs & Thermal Limits
    for _, row in lines_df.iterrows():
        line = row['Line']
        limit = row['Thermal_Limit']
        
        # (ψ_k): f_k = sum(PTDF_k,i * r_i)
        f_line = pu.lpSum([ptdf_df.loc[line, node] * r[node] for node in unique_nodes])
        prob += f[line] == f_line, f"psi_{line}"

        # Thermal Limits (λ_str and λ_opp); skip if unconstrained
        if not pd.isna(limit):
            prob += f[line] <= limit, f"lambda_{line}_str"
            prob += f[line] >= -limit, f"lambda_{line}_opp"

    # Solution
    status_code = prob.solve(solver)
    status = pu.LpStatus[status_code]

    # If the problem was not solved optimally, return empty results
    if status != "Optimal":
        return status, None, None, None, None, None, None

    # Retrieval of Results & Shadow Prices (.pi)
    total_cost = pu.value(prob.objective)

    # Primary Variables
    gen_res = {}
    for spec in generator_specs:
        node = spec["node"]
        gen_res[node] = gen_res.get(node, 0.0) + p[spec["gen_id"]].varValue
    flow_res = {line: f[line].varValue for line in lines_df['Line']}
    injections = {node: r[node].varValue for node in unique_nodes}

    # Dual Variables (LMPs & Congestion Components)
    lmps = {}
    for node in unique_nodes:
        lmps[node] = prob.constraints[f"lmp_{node}"].pi
        
    # Congestion Data 
    system_lambda = prob.constraints["minus_phi"].pi
    congestion_prices = {}
    for line in lines_df['Line']:
        str_name = f"lambda_{line}_str"
        opp_name = f"lambda_{line}_opp"
        lambda_str = prob.constraints[str_name].pi if str_name in prob.constraints else 0.0
        lambda_opp = prob.constraints[opp_name].pi if opp_name in prob.constraints else 0.0
        congestion_prices[line] = {'lambda_str': lambda_str, 'lambda_opp': lambda_opp}

    return status, total_cost, gen_res, flow_res, lmps, congestion_prices, system_lambda
