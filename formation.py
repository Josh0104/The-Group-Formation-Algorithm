from mip import Model, xsum, BINARY, minimize, GUROBI, OptimizationStatus

def form_teams() -> None:
    # Create Model with Gurobi as the solver
    m = Model(solver_name=GUROBI)

    # Example Data
    campers = range(10)  # 10 campers
    teams = range(2)     # 2 teams
    skill_levels = [3, 2, 4, 5, 1, 3, 2, 4, 5, 1]  # Example skill levels for campers
    max_skill_level = sum(skill_levels) / len(teams)  # Convert to float for safety

    # Decision Variables: x[c][t] is 1 if camper c is assigned to team t, else 0
    x = [[m.add_var(var_type=BINARY) for t in teams] for c in campers]

    # Constraint: Each camper is assigned to exactly one team
    for c in campers:
        m += xsum(x[c][t] for t in teams) == 1

    # Skill balance constraint using auxiliary variables
    imbalance = [m.add_var() for t in teams]  # New variables for imbalance

    for t in teams:
        team_skill = xsum(skill_levels[c] * x[c][t] for c in campers)  # No float conversion
        m += imbalance[t] >= team_skill - max_skill_level  # Corrected constraint
        m += imbalance[t] >= max_skill_level - team_skill  # Corrected constraint

    # Objective Function: Minimize skill imbalance across teams
    m.objective = minimize(xsum(imbalance))

    # Solve the optimization problem
    m.optimize()

    # Print Results (only if an optimal solution is found)
    if m.status == OptimizationStatus.OPTIMAL:  # if optimal solution found
        for t in teams:
            print(f"Team {t+1}: ", [c for c in campers if x[c][t].x is not None and x[c][t].x >= 0.99])
    else:
        print("No optimal solution found!")
