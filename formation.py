from mip import Model, xsum, BINARY, minimize, GUROBI, OptimizationStatus
from csv_reader import read_csv_pd
import os
import time
import csv
import random

def form_teams():
    # Load data
    people = read_csv_pd("data/users.csv")
    campers = list(people.values())
    num_teams = 5  # Adjust as needed

    # Generic Yes/Maybe/No scoring (for Q2, Q3, Q4,)
    def yes_no_maybe_score(answer):
        if "yes" in answer.lower():
            return 3
        elif "maybe" in answer.lower():
            return 2
        else:
            return 1

    # Team leader → Q1
    def is_team_leader(answer):
        return 1 if "yes" in answer.lower() else 0

    # Extract answers
    skill_levels = [yes_no_maybe_score(person.a4) for person in campers]
    is_leader = [is_team_leader(person.a1) for person in campers]
    creativity = [yes_no_maybe_score(person.a2) for person in campers]
    bible_knowledge = [yes_no_maybe_score(person.a3) for person in campers]

    num_campers = len(campers)
    teams = range(num_teams)
    camper_ids = range(num_campers)

    # Averages
    avg_skill = sum(skill_levels) / num_teams
    avg_creativity = sum(creativity) / num_teams
    avg_bible = sum(bible_knowledge) / num_teams

    # Model
    m = Model(solver_name=GUROBI)
    x = [[m.add_var(var_type=BINARY) for _ in teams] for _ in camper_ids]

    # Each camper in one team
    for c in camper_ids:
        m += xsum(x[c][t] for t in teams) == 1

    # Skill imbalance
    imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_skill = xsum(skill_levels[c] * x[c][t] for c in camper_ids)
        m += imbalance[t] >= team_skill - avg_skill
        m += imbalance[t] >= avg_skill - team_skill

    # Creativity imbalance
    creativity_imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_creativity = xsum(creativity[c] * x[c][t] for c in camper_ids)
        m += creativity_imbalance[t] >= team_creativity - avg_creativity
        m += creativity_imbalance[t] >= avg_creativity - team_creativity

    # Bible knowledge imbalance
    bible_imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_bible = xsum(bible_knowledge[c] * x[c][t] for c in camper_ids)
        m += bible_imbalance[t] >= team_bible - avg_bible
        m += bible_imbalance[t] >= avg_bible - team_bible

    # Leader requirement
    for t in teams:
        m += xsum(is_leader[c] * x[c][t] for c in camper_ids) >= 1

    # Randomized weights for soft variation
    epsilon = 0.01
    random_weights = [random.uniform(1 - epsilon, 1 + epsilon) for _ in teams]
    m.objective = minimize(
        xsum(random_weights[t] * (
            imbalance[t] +
            creativity_imbalance[t] +
            bible_imbalance[t]
        ) for t in teams)
    )

    # Solve
    m.optimize()

    # Output results
    if m.status == OptimizationStatus.OPTIMAL:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        output_path = os.path.join(output_dir, f"{timestamp}.csv")

        rows = []
        for t in teams:
            for c in camper_ids:
                if x[c][t].x >= 0.99:
                    camper = campers[c]
                    rows.append([camper.uuid, camper.first_name, camper.last_name, t + 1])

        with open(output_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "First name", "Last name", "Team"])
            writer.writerows(rows)

        print(f"Output saved to: {output_path}")
    else:
        print("No optimal solution found.")
