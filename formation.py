from mip import Model, xsum, BINARY, OptimizationStatus
import os
import time
import csv
import random
import relations as Relations
from datetime import datetime
from person import Person, AgeGroup

def form_teams(people: dict[str, Person], number_of_groups, is_printing_output, args_output_file, args_no_output, args_verbose, relations_data, args_solver, args_timeout): 

    # Load data
    campers = list(people.values())
    num_teams = number_of_groups
    

    # Extract attributes from campers
    leadership = [p.a1.value for p in campers]
    creativity = [p.a2.value for p in campers]
    bible_knowledge = [p.a3.value for p in campers]
    physcial_fit = [p.a4.value for p in campers]
    musical_ability = [p.a5.value for p in campers]
    camp_experience = [p.a6.value for p in campers]
    performance_experience = [p.a7.value for p in campers]
    prop_design = [p.a8.value for p in campers]
    # Age groups
    men = [1 if p.age_group == AgeGroup.MEN else 0 for p in campers]    
    women = [1 if p.age_group == AgeGroup.WOMEN else 0 for p in campers]
    youth = [1 if p.age_group == AgeGroup.YOUTH else 0 for p in campers]
    kids = [1 if p.age_group == AgeGroup.KIDS else 0 for p in campers]
    babies = [1 if p.age_group == AgeGroup.BABIES else 0 for p in campers]

    num_campers = len(campers)
    teams = range(num_teams)
    camper_ids = range(num_campers)

    avg_leadership = sum(leadership) / num_teams
    avg_creativity = sum(creativity) / num_teams
    avg_bible = sum(bible_knowledge) / num_teams
    avg_physcial_fit = sum(physcial_fit) / num_teams
    avg_music = sum(musical_ability) / num_teams
    avg_experience = sum(camp_experience) / num_teams
    avg_performance = sum(performance_experience) / num_teams
    avg_prop_design = sum(prop_design) / num_teams
    # Calculate average for each age group
    avg_men = sum(men) / num_teams
    avg_women = sum(women) / num_teams
    avg_youth = sum(youth) / num_teams
    avg_kids = sum(kids) / num_teams
    avg_babies = sum(babies) / num_teams
    
    if args_solver is not None:
        m = Model(solver_name=args_solver)
    else:
        m = Model('GRB')
    print(f"Using solver: {m.solver_name}")
        
    m.verbose = 0 if args_verbose is False else 1 # Print solver output
    m.max_seconds = args_timeout
    x = [[m.add_var(var_type=BINARY) for _ in teams] for _ in camper_ids]

    # Every camper is assigned to one and only one team.
    for c in camper_ids:
        m += xsum(x[c][t] for t in teams) == 1

    # Define Team Imbalance Variables
    leadership_imbalance = [m.add_var() for _ in teams]
    creativity_imbalance = [m.add_var() for _ in teams]
    bible_imbalance = [m.add_var() for _ in teams]
    physcial_fit_imbalance = [m.add_var() for _ in teams]
    music_imbalance = [m.add_var() for _ in teams]
    experience_imbalance = [m.add_var() for _ in teams]
    performance_imbalance = [m.add_var() for _ in teams]
    prop_imbalance = [m.add_var() for _ in teams]
    
    # Define Age Imbalance Variables
    men_imbalance = [m.add_var() for _ in teams]
    women_imbalance = [m.add_var() for _ in teams]
    youth_imbalance = [m.add_var() for _ in teams]
    kids_imbalance = [m.add_var() for _ in teams]
    babies_imbalance = [m.add_var() for _ in teams]
    avg_team_size = num_campers / num_teams # Average team size
    plus_minus = 2 # Allowable deviation from average team size
    min_team_size = int(avg_team_size - plus_minus) # Minimum team size (±)
    max_team_size = int(avg_team_size + plus_minus) # Maximum team size (±)

    # Balance constraints per skill
    # imbalance ≥ absolute difference between actual skill in team and average skill.
    for t in teams:
        m += leadership_imbalance[t] >= xsum(leadership[c] * x[c][t] for c in camper_ids) - avg_leadership
        m += leadership_imbalance[t] >= avg_leadership - xsum(leadership[c] * x[c][t] for c in camper_ids)
        m += creativity_imbalance[t] >= xsum(creativity[c] * x[c][t] for c in camper_ids) - avg_creativity
        m += creativity_imbalance[t] >= avg_creativity - xsum(creativity[c] * x[c][t] for c in camper_ids)
        m += bible_imbalance[t] >= xsum(bible_knowledge[c] * x[c][t] for c in camper_ids) - avg_bible
        m += bible_imbalance[t] >= avg_bible - xsum(bible_knowledge[c] * x[c][t] for c in camper_ids)
        m += physcial_fit_imbalance[t] >= xsum(physcial_fit[c] * x[c][t] for c in camper_ids) - avg_physcial_fit
        m += physcial_fit_imbalance[t] >= avg_physcial_fit - xsum(physcial_fit[c] * x[c][t] for c in camper_ids)
        m += music_imbalance[t] >= xsum(musical_ability[c] * x[c][t] for c in camper_ids) - avg_music
        m += music_imbalance[t] >= avg_music - xsum(musical_ability[c] * x[c][t] for c in camper_ids)
        m += experience_imbalance[t] >= xsum(camp_experience[c] * x[c][t] for c in camper_ids) - avg_experience
        m += experience_imbalance[t] >= avg_experience - xsum(camp_experience[c] * x[c][t] for c in camper_ids)
        m += performance_imbalance[t] >= xsum(performance_experience[c] * x[c][t] for c in camper_ids) - avg_performance
        m += performance_imbalance[t] >= avg_performance - xsum(performance_experience[c] * x[c][t] for c in camper_ids)
        m += prop_imbalance[t] >= xsum(prop_design[c] * x[c][t] for c in camper_ids) - avg_prop_design
        m += prop_imbalance[t] >= avg_prop_design - xsum(prop_design[c] * x[c][t] for c in camper_ids)
        # Balance constraints per age group
        m += men_imbalance[t] >= xsum(men[c] * x[c][t] for c in camper_ids) - avg_men
        m += men_imbalance[t] >= avg_men - xsum(men[c] * x[c][t] for c in camper_ids)
        m += women_imbalance[t] >= xsum(women[c] * x[c][t] for c in camper_ids) - avg_women
        m += women_imbalance[t] >= avg_women - xsum(women[c] * x[c][t] for c in camper_ids)
        m += youth_imbalance[t] >= xsum(youth[c] * x[c][t] for c in camper_ids) - avg_youth
        m += youth_imbalance[t] >= avg_youth - xsum(youth[c] * x[c][t] for c in camper_ids)
        m += kids_imbalance[t] >= xsum(kids[c] * x[c][t] for c in camper_ids) - avg_kids
        m += kids_imbalance[t] >= avg_kids - xsum(kids[c] * x[c][t] for c in camper_ids)
        m += babies_imbalance[t] >= xsum(babies[c] * x[c][t] for c in camper_ids) - avg_babies
        m += babies_imbalance[t] >= avg_babies - xsum(babies[c] * x[c][t] for c in camper_ids)

        m += xsum(x[c][t] for c in camper_ids) >= min_team_size # Team size constraint (±)
        m += xsum(x[c][t] for c in camper_ids) <= max_team_size # Team size constraint (±)

    epsilon = 0.01
    random_weights = [random.uniform(1 - epsilon, 1 + epsilon) for _ in teams]
    m.objective += xsum(random_weights[t] * (
        1.0 * leadership_imbalance[t] +
        1.0 * creativity_imbalance[t] +
        1.0 * bible_imbalance[t] +
        1.0 * physcial_fit_imbalance[t] +
        1.0 * music_imbalance[t] +
        0.5 * experience_imbalance[t] +
        1.0 * performance_imbalance[t] + 
        1.0 * prop_imbalance[t] + 
        1.0 * men_imbalance[t] +
        1.0 * women_imbalance[t] +
        1.0 * youth_imbalance[t] +
        1.0 * kids_imbalance[t] +
        1.0 * babies_imbalance[t]
    ) for t in teams)
    
    # Add relations constraints
    # if relations_data is None:
        # print("No relations data provided.")
        # relations_data = Relations.get_relations(people,None)

    relations_together: list[tuple] = []
    relations_separate: list[tuple] = []
    
    
    for r in relations_data:
        id_1 = r['id_1']
        id_2 = r['id_2']
        relation_type = r['relation']
        
        if relation_type == 'TOGETHER':
            relations_together.append((id_1, id_2))
        elif relation_type == 'SEPARATE':
            relations_separate.append((id_1, id_2))
            
    for (p, q) in relations_together:
        for t in teams:
                m += x[p][t] - x[q][t] == 0
                    
    for (p, q) in relations_separate:
        for t in teams:
            m += x[p][t] + x[q][t] <= 1

    m.optimize()
    
    print(f'Total dataset size: {len(camper_ids)}')

    if m.status == OptimizationStatus.OPTIMAL:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        output_path = os.path.join(output_dir, f"{timestamp}.csv")

        for t in teams:
            for c in camper_ids:
                if x[c][t].x >= 0.99:
                    camper = campers[c]
                    camper.set_team(t + 1)

        if args_no_output is not True:
            output_dir = args_output_file if args_output_file != None else "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            output_path = os.path.join(output_dir, f"teams_{timestamp}.csv")
            
            with open(output_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "First name", "Last name", "Team"])
                writer.writerows([c.uuid, c.first_name, c.last_name, c.team] for c in campers)

            print(f"Output saved to: {output_path}")

        if is_printing_output:
            for t in teams:
                team_members = [c for c in campers if c.team == t + 1]
                print(f"\nTeam {t + 1} - Total: {len(team_members)}")
                for member in team_members:
                    print(f"  {member.first_name} {member.last_name}")
        
        return campers
            
    else:
        print("No optimal solution found.")
    
    return None
