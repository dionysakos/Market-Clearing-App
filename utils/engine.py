import pulp as pu
import pandas as pd

def run_market_clearing(nodes_df, lines_df, ptdf_df, solver_path=None):
    """
    We run DC-OPF using PTDFs.
    
    :param nodes_df: DataFrame with columns ['Node', 'Demand', 'Pmax', 'Cost']
    :param lines_df: DataFrame with columns ['Line', 'Thermal_Limit']
    :param ptdf_df: DataFrame with PTDFs (Index=Line, Columns=Nodes)
    :param solver_path: Optional path for the CBC solver (e.g., for Mac)
    :return: status, total_cost, gen_results, flow_results, lmps, congestion_prices
    """
    
    # Solver 
    if solver_path:
        solver = pu.COIN_CMD(path=solver_path, msg=0, mip=False)
    else:
        solver = pu.PULP_CBC_CMD(msg=0, mip=False)

    prob = pu.LpProblem("DCOPF_PTDF_Model", pu.LpMinimize)

    # Variables
    p = {} # Generation
    r = {} # Net Injection
    f = {} # Power Flow

    # Definition of Decision Variables
    for _, row in nodes_df.iterrows():
        node = row['Node']
        # p >= 0, Pmax limit
        p[node] = pu.LpVariable(f"p_{node}", lowBound=0, upBound=row['Pmax'], cat=pu.LpContinuous)
        # r
        r[node] = pu.LpVariable(f"r_{node}", cat=pu.LpContinuous)

    for _, row in lines_df.iterrows():
        line = row['Line']
        # f
        f[line] = pu.LpVariable(f"f_{line}", cat=pu.LpContinuous)

    # Objective Function 
    prob += pu.lpSum([p[row['Node']] * row['Cost'] for _, row in nodes_df.iterrows()]), "Total_Cost"

    # Constraints

    # Nodal Power Balance: p_i - r_i = d_i (Dual Variable: ρ_n -> LMP)
    for _, row in nodes_df.iterrows():
        node = row['Node']
        demand = row['Demand']
        prob += p[node] - r[node] == demand, f"lmp_{node}"

    # Total Injection Balance: sum(r_i) = 0 (Dual Variable: -φ)
    prob += pu.lpSum([r[node] for node in nodes_df['Node']]) == 0, "minus_phi"

    # Flow Calculation & Thermal Limits
    for _, row in lines_df.iterrows():
        line = row['Line']
        limit = row['Thermal_Limit']
        
        # (ψ_k): f_k = sum(PTDF_k,i * r_i)
        ptdf_expr = pu.lpSum([ptdf_df.loc[line, node] * r[node] for node in nodes_df['Node']])
        prob += f[line] == ptdf_expr, f"psi_{line}"

        # Thermal Limits (λ_str and λ_opp)
        prob += f[line] <= limit, f"lambda_{line}_str"
        prob += f[line] >= -limit, f"lambda_{line}_opp"

    # Solution
    status_code = prob.solve(solver)
    status = pu.LpStatus[status_code]

    # If the problem was not solved optimally, return empty results
    if status != "Optimal":
        return status, None, None, None, None, None

    # Retrieval of Results & Shadow Prices (.pi)
    total_cost = pu.value(prob.objective)

    # Primary Variables
    gen_results = {node: p[node].varValue for node in nodes_df['Node']}
    flow_results = {line: f[line].varValue for line in lines_df['Line']}
    injections = {node: r[node].varValue for node in nodes_df['Node']}

    # Dual Variables (LMPs & Congestion Components)
    lmps = {}
    for node in nodes_df['Node']:
        # Retrieval of the ρ_n (Local Marginal Price)
        lmps[node] = prob.constraints[f"lmp_{node}"].pi
        
    # Congestion Data for Analytics (optional but excellent for dashboards)
    system_lambda = prob.constraints["minus_phi"].pi
    congestion_prices = {}
    for line in lines_df['Line']:
        lambda_str = prob.constraints[f"lambda_{line}_str"].pi
        lambda_opp = prob.constraints[f"lambda_{line}_opp"].pi
        congestion_prices[line] = {'lambda_str': lambda_str, 'lambda_opp': lambda_opp}

    return status, total_cost, gen_results, flow_results, lmps, congestion_prices
