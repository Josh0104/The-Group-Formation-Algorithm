from mip import Model, xsum, BINARY, minimize, GUROBI, OptimizationStatus
from csv_reader import read_csv_pd

def form_teams():
    # Load data
    people = read_csv_pd("data/users.csv")
    campers = list(people.values())
    num_teams = 5  # Adjust as needed

    # Extract skill level from Q4 (fitness)
    def interpret_fitness(answer):
        if "yes" in answer.lower():
            return 3
        elif "maybe" in answer.lower():
            return 2
        else:
            return 1

    # Leader from Q1 (willing to be a team leader)
    def is_team_leader(answer):
        return 1 if "yes" in answer.lower() else 0

    skill_levels = [interpret_fitness(person.a4) for person in campers]
    is_leader = [is_team_leader(person.a1) for person in campers]

    num_campers = len(campers)
    teams = range(num_teams)
    camper_ids = range(num_campers)
    avg_skill = sum(skill_levels) / num_teams

    # Model
    m = Model(solver_name=GUROBI)
    x = [[m.add_var(var_type=BINARY) for _ in teams] for _ in camper_ids]

    # Each camper is in one team
    for c in camper_ids:
        m += xsum(x[c][t] for t in teams) == 1

    # Balance skill
    imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_skill = xsum(skill_levels[c] * x[c][t] for c in camper_ids)
        m += imbalance[t] >= team_skill - avg_skill
        m += imbalance[t] >= avg_skill - team_skill

    # ✅ Ensure at least one leader per team
    for t in teams:
        m += xsum(is_leader[c] * x[c][t] for c in camper_ids) >= 1

    # Minimize imbalance
    m.objective = minimize(xsum(imbalance))
    m.optimize()

    # Output results
    if m.status == OptimizationStatus.OPTIMAL:
        for t in teams:
            group = [campers[c].first_name + " " + campers[c].last_name
                     for c in camper_ids if x[c][t].x >= 0.99]
            print(f"Team {t+1} ({len(group)} members): {group}")
    else:
        print("No optimal solution found.")
