from mip import Model, xsum, BINARY, minimize, GUROBI, OptimizationStatus
import gurobipy as gp
import os
import time
import csv
import random
import relations as Relations
from person import Person

# Global variable to store last model for saving
last_model = None

def form_teams(people: dict[str, Person], number_of_groups, is_printing_output, args_output_file, args_no_output, args_verbose): 
    global last_model

    # Load data
    campers = list(people.values())
    num_teams = number_of_groups

    def is_team_leader(answer):
        return 1 if "yes" in answer.lower() else 0

    skill_levels = [p.a4.value for p in campers]
    is_leader = [is_team_leader(p.a1) for p in campers]
    creativity = [p.a2.value for p in campers]
    bible_knowledge = [p.a3.value for p in campers]
    musical_ability = [p.a5.value for p in campers]
    camp_experience = [p.a6.value for p in campers]
    performance_experience = [p.a7.value for p in campers]
    prop_design = [p.a8.value for p in campers]

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
    m.verbose = 0 if args_verbose is False else 1 # Print solver output
    m.max_seconds = 120 # Set a time limit of 120 seconds
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
    avg_team_size = num_campers / num_teams # Average team size
    plus_minus = 2 # Allowable deviation from average team size
    min_team_size = int(avg_team_size - plus_minus) # Minimum team size (±)
    max_team_size = int(avg_team_size + plus_minus) # Maximum team size (±)

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
        m += xsum(x[c][t] for c in camper_ids) >= min_team_size # Team size constraint (±)
        m += xsum(x[c][t] for c in camper_ids) <= max_team_size # Team size constraint (±)


    epsilon = 0.01
    random_weights = [random.uniform(1 - epsilon, 1 + epsilon) for _ in teams]
    m.objective += xsum(random_weights[t] * (
        1.0 * imbalance[t] +
        1.0 * creativity_imbalance[t] +
        1.0 * bible_imbalance[t] +
        0.75 * music_imbalance[t] +
        0.5 * experience_imbalance[t] +
        1.0 * performance_imbalance[t] + 
        1.0 * prop_imbalance[t]
    ) for t in teams)
    
    relations = Relations.get_relations(people)
    
    relations_together: list[tuple] = []
    relations_separate: list[tuple] = []
    for r in relations.values():
        id_1 = r['id_1']
        id_2 = r['id_2']
        relation = r['relation']
        print(f"Relation: {r['relation']}, {id_1}, {id_2} {r['name_1']}, {r['name_2']}, {r['relation']}")
        
        if relation == 'TOGETHER':
            relations_together.append((id_1, id_2))
        elif relation == 'SEPARATE':
            relations_separate.append((id_1, id_2))
            
        for (p, q) in relations_separate:
            for t in teams:
                m += x[p][t] + x[q][t] <= 1

        for (p, q) in relations_together:
            for t in teams:
                m += x[p][t] - x[q][t] == 0
                
        # uuid_1 = r['uuid_1']
        # uuid_2 = r['uuid_2']
        # relation = r['relation']
        # weight = r['weight']
        # description = r['description']

        # if relation == "TOGETHER":
        #     v = m.add_var(var_type=BINARY)
        #     for t in teams:
        #         m += x[name_to_index[uuid_1]][t] - x[name_to_index[uuid_2]][t] <= v
        #         m += x[name_to_index[uuid_2]][t] - x[name_to_index[uuid_1]][t] <= v
        #     m.objective += 5 * v
        #     q9_violations.append(v)

        # elif relation == "SEPARATE":
        #     v = m.add_var(var_type=BINARY)
        #     for t in teams:
        #         m += x[name_to_index[uuid_1]][t] + x[name_to_index[uuid_2]][t] <= 1 + v
        #     m.objective += 10 * v
        #     q10_violations.append(v)

    # Static data
    # Constraint: prevent certain campers from being in the same team
    
    # not_together = [(7,8), (7,2)]
    

    m.optimize()

    # Save the model so GUI can access it
    last_model = m

    if m.status == OptimizationStatus.OPTIMAL:

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        output_path = os.path.join(output_dir, f"{timestamp}.csv")

        for t in teams:
            for c in camper_ids:
                if x[c][t].x >= 0.99:
                    camper = campers[c]
                    # rows.append([camper.uuid, camper.first_name, camper.last_name, t + 1])
                    camper.set_team(t + 1)

        if args_no_output is not True:
            output_dir = args_output_file if args_output_file != None else "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = int(time.time())
            output_path = os.path.join(output_dir, f"{timestamp}.csv")

            with open(output_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "First name", "Last name", "Team"])
                writer.writerows([c.uuid, c.first_name, c.last_name, c.team] for c in campers)

            print(f"Output saved to: {output_path}")

        if is_printing_output:
            for c in campers:
                print(c)
            for t in teams:
                print(f"Team {t + 1}: {len([c for c in campers if c[3] == t + 1])}")
        
        return campers
            
    else:
        print("No optimal solution found.")
    
    return None
