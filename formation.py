from mip import Model, xsum, BINARY, minimize, GUROBI, OptimizationStatus
import os
import time
import csv
import random

# Global variable to store last model for saving
last_model = None

def form_teams(people, number_of_groups, is_printing_output, args_output_file, args_no_output):
    global last_model

    # Load data
    campers = list(people.values())
    num_teams = number_of_groups

    def yes_no_maybe_score(answer):
        if "yes" in answer.lower(): return 3
        elif "maybe" in answer.lower(): return 2
        else: return 1

    def is_team_leader(answer):
        return 1 if "yes" in answer.lower() else 0

    skill_levels = [yes_no_maybe_score(p.a4) for p in campers]
    is_leader = [is_team_leader(p.a1) for p in campers]
    creativity = [yes_no_maybe_score(p.a2) for p in campers]
    bible_knowledge = [yes_no_maybe_score(p.a3) for p in campers]
    musical_ability = [yes_no_maybe_score(p.a5) for p in campers]
    camp_experience = [yes_no_maybe_score(p.a6) for p in campers]
    performance_experience = [yes_no_maybe_score(p.a7) for p in campers]
    prop_design = [yes_no_maybe_score(p.a8) for p in campers]

    num_campers = len(campers)
    teams = range(num_teams)
    camper_ids = range(num_campers)

    avg_skill = sum(skill_levels) / num_teams
    avg_creativity = sum(creativity) / num_teams
    avg_bible = sum(bible_knowledge) / num_teams
    avg_music = sum(musical_ability) / num_teams
    avg_experience = sum(camp_experience) / num_teams
    avg_performance = sum(performance_experience) / num_teams
    avg_prop_design = sum(prop_design) / num_teams

    m = Model(solver_name=GUROBI)
    m.max_seconds = 120
    x = [[m.add_var(var_type=BINARY) for _ in teams] for _ in camper_ids]

    for c in camper_ids:
        m += xsum(x[c][t] for t in teams) == 1

    imbalance = [m.add_var() for _ in teams]
    creativity_imbalance = [m.add_var() for _ in teams]
    bible_imbalance = [m.add_var() for _ in teams]
    music_imbalance = [m.add_var() for _ in teams]
    experience_imbalance = [m.add_var() for _ in teams]
    performance_imbalance = [m.add_var() for _ in teams]
    prop_imbalance = [m.add_var() for _ in teams]

    for t in teams:
        m += imbalance[t] >= xsum(skill_levels[c] * x[c][t] for c in camper_ids) - avg_skill
        m += imbalance[t] >= avg_skill - xsum(skill_levels[c] * x[c][t] for c in camper_ids)
        m += creativity_imbalance[t] >= xsum(creativity[c] * x[c][t] for c in camper_ids) - avg_creativity
        m += creativity_imbalance[t] >= avg_creativity - xsum(creativity[c] * x[c][t] for c in camper_ids)
        m += bible_imbalance[t] >= xsum(bible_knowledge[c] * x[c][t] for c in camper_ids) - avg_bible
        m += bible_imbalance[t] >= avg_bible - xsum(bible_knowledge[c] * x[c][t] for c in camper_ids)
        m += music_imbalance[t] >= xsum(musical_ability[c] * x[c][t] for c in camper_ids) - avg_music
        m += music_imbalance[t] >= avg_music - xsum(musical_ability[c] * x[c][t] for c in camper_ids)
        m += experience_imbalance[t] >= xsum(camp_experience[c] * x[c][t] for c in camper_ids) - avg_experience
        m += experience_imbalance[t] >= avg_experience - xsum(camp_experience[c] * x[c][t] for c in camper_ids)
        m += performance_imbalance[t] >= xsum(performance_experience[c] * x[c][t] for c in camper_ids) - avg_performance
        m += performance_imbalance[t] >= avg_performance - xsum(performance_experience[c] * x[c][t] for c in camper_ids)
        m += prop_imbalance[t] >= xsum(prop_design[c] * x[c][t] for c in camper_ids) - avg_prop_design
        m += prop_imbalance[t] >= avg_prop_design - xsum(prop_design[c] * x[c][t] for c in camper_ids)
        m += xsum(is_leader[c] * x[c][t] for c in camper_ids) >= 1

    name_to_index = {
        f"{p.first_name.strip().lower()} {p.last_name.strip().lower()}": i
        for i, p in enumerate(campers)
    }

    q9_violations = []
    q10_violations = []

    for i, person in enumerate(campers):
        if str(person.a9).strip():
            target = str(person.a9).strip().lower()
            j = name_to_index.get(target)
            if j is not None and i != j:
                v = m.add_var(var_type=BINARY)
                for t in teams:
                    m += x[i][t] - x[j][t] <= v
                    m += x[j][t] - x[i][t] <= v
                m.objective += 5 * v
                q9_violations.append(v)

        if str(person.a10).strip():
            target = str(person.a10).strip().lower()
            j = name_to_index.get(target)
            if j is not None and i != j:
                v = m.add_var(var_type=BINARY)
                for t in teams:
                    m += x[i][t] + x[j][t] <= 1 + v
                m.objective += 10 * v
                q10_violations.append(v)

    epsilon = 0.01
    random_weights = [random.uniform(1 - epsilon, 1 + epsilon) for _ in teams]
    m.objective += xsum(random_weights[t] * (
        1.0 * imbalance[t] +
        1.0 * creativity_imbalance[t] +
        1.0 * bible_imbalance[t] +
        0.5 * music_imbalance[t] +
        1.0 * experience_imbalance[t] +
        0.75 * performance_imbalance[t] + 
        0.75 * prop_imbalance[t]
    ) for t in teams)

    m.optimize()

    # Save the model so GUI can access it
    last_model = m

    if m.status == OptimizationStatus.OPTIMAL:
        q9_broken = sum(1 for v in q9_violations if v.x >= 0.99)
        q10_broken = sum(1 for v in q10_violations if v.x >= 0.99)

        print(f"Q9 (want-to-be-with) violations: {q9_broken}")
        print(f"Q10 (avoid-this-person) violations: {q10_broken}")

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

        if args_no_output is not True:
            output_dir = args_output_file if args_output_file != None else "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = int(time.time())
            output_path = os.path.join(output_dir, f"{timestamp}.csv")

            with open(output_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "First name", "Last name", "Team"])
                writer.writerows(rows)

            print(f"Output saved to: {output_path}")

        if is_printing_output:
            for row in rows:
                print(row)
            for t in teams:
                print(f"Team {t + 1}: {len([row for row in rows if row[3] == t + 1])}")
    else:
        print("No optimal solution found.")
