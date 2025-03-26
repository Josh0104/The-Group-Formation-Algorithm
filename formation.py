from mip import Model, xsum, BINARY, minimize, GUROBI, OptimizationStatus
import os
import time
import csv
import random

def form_teams(people):
    # Load data
    campers = list(people.values())
    num_teams = 5  # Adjust as needed

    # Generic Yes/Maybe/No scoring (for Q2–Q6)
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
    skill_levels = [yes_no_maybe_score(person.a4) for person in campers]        # Q4
    is_leader = [is_team_leader(person.a1) for person in campers]               # Q1
    creativity = [yes_no_maybe_score(person.a2) for person in campers]          # Q2
    bible_knowledge = [yes_no_maybe_score(person.a3) for person in campers]     # Q3
    musical_ability = [yes_no_maybe_score(person.a5) for person in campers]     # Q5
    camp_experience = [yes_no_maybe_score(person.a6) for person in campers]     # Q6
    performance_experience = [yes_no_maybe_score(person.a7) for person in campers]  # Q7
    prop_design = [yes_no_maybe_score(person.a8) for person in campers]             # Q8

    num_campers = len(campers)
    teams = range(num_teams)
    camper_ids = range(num_campers)

    # Averages
    avg_skill = sum(skill_levels) / num_teams
    avg_creativity = sum(creativity) / num_teams
    avg_bible = sum(bible_knowledge) / num_teams
    avg_music = sum(musical_ability) / num_teams
    avg_experience = sum(camp_experience) / num_teams
    avg_performance = sum(performance_experience) / num_teams
    avg_prop_design = sum(prop_design) / num_teams

    # Model
    m = Model(solver_name=GUROBI)
    m.max_seconds = 120
    x = [[m.add_var(var_type=BINARY) for _ in teams] for _ in camper_ids]

    # Each camper in one team
    for c in camper_ids:
        m += xsum(x[c][t] for t in teams) == 1

    # Skill imbalance (Q4)
    imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_skill = xsum(skill_levels[c] * x[c][t] for c in camper_ids)
        m += imbalance[t] >= team_skill - avg_skill
        m += imbalance[t] >= avg_skill - team_skill

    # Creativity imbalance (Q2)
    creativity_imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_creativity = xsum(creativity[c] * x[c][t] for c in camper_ids)
        m += creativity_imbalance[t] >= team_creativity - avg_creativity
        m += creativity_imbalance[t] >= avg_creativity - team_creativity

    # Bible knowledge imbalance (Q3)
    bible_imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_bible = xsum(bible_knowledge[c] * x[c][t] for c in camper_ids)
        m += bible_imbalance[t] >= team_bible - avg_bible
        m += bible_imbalance[t] >= avg_bible - team_bible

    # Musical ability imbalance (Q5)
    music_imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_music = xsum(musical_ability[c] * x[c][t] for c in camper_ids)
        m += music_imbalance[t] >= team_music - avg_music
        m += music_imbalance[t] >= avg_music - team_music

    # Camp experience imbalance (Q6)
    experience_imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_experience = xsum(camp_experience[c] * x[c][t] for c in camper_ids)
        m += experience_imbalance[t] >= team_experience - avg_experience
        m += experience_imbalance[t] >= avg_experience - team_experience

    # Leader requirement (Q1)
    for t in teams:
        m += xsum(is_leader[c] * x[c][t] for c in camper_ids) >= 1

    # Performance experience imbalance (Q7)
    performance_imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_perf = xsum(performance_experience[c] * x[c][t] for c in camper_ids)
        m += performance_imbalance[t] >= team_perf - avg_performance
        m += performance_imbalance[t] >= avg_performance - team_perf

    # Prop/costume design imbalance (Q8)
    prop_imbalance = [m.add_var() for _ in teams]
    for t in teams:
        team_prop = xsum(prop_design[c] * x[c][t] for c in camper_ids)
        m += prop_imbalance[t] >= team_prop - avg_prop_design
        m += prop_imbalance[t] >= avg_prop_design - team_prop

    # Randomized weights for soft variation
    epsilon = 0.01
    random_weights = [random.uniform(1 - epsilon, 1 + epsilon) for _ in teams]
    m.objective = minimize(
        xsum(random_weights[t] * (
            1.0 * imbalance[t] +
            1.0 * creativity_imbalance[t] +
            1.0 * bible_imbalance[t] +
            0.5 * music_imbalance[t] +
            1.0 * experience_imbalance[t] +
            0.75 * performance_imbalance[t] + 
            0.75 * prop_imbalance[t]
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
