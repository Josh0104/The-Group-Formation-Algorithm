from datetime import datetime
from nicegui import ui, run, app, events
import csv_reader as cr
import io
import formation as fm
from formation import Person
from person import Gender, AnswerOption
import os
import main as main
from gui.layout import add_layout
import csv

# Global variables
teams_data: list[tuple] = []
team_stats = {}
team_cards = []
loading_overlay = None

# UI elements

@ui.page('/')
def dashboard() -> None:
    global relation_table, loading_overlay
    add_layout()
    global team_container, chart_container, format_setting_container, separator_line, label_info_chart
    loading_overlay = ui.column().classes('fixed inset-0 z-50 hidden items-center justify-center bg-black/80')
    
    with loading_overlay:
        ui.spinner('hourglass',size='4rem', color='blue')
        ui.label('Loading').classes('text-white text-xl mt-4')
    
    from app_config import args  # access shared args
    person_dict = cr.read_csv_pd(args.input)

    # --- Layout --- 
    with ui.column().classes("items-center w-full"):
        
        ui.label("Team Optimizer Dashboard").classes("text-3xl font-bold mt-4")

        with ui.expansion("Relations").classes("w-7xl mt-4 justify-center dark:bg-gray-700 bg-gray-100 "):

            option_select: dict = {}
            for p in person_dict.values():
                full_name = f"{p.first_name} {p.last_name}"
                option_select[p.uuid,full_name, p.id] =  [full_name] # rhs value and lhs label
                
            with ui.column().classes("items-center w-full"):
                with ui.row().classes("mt-6 justify-center gap-10"):
                    with ui.column().classes("items-center"):
                        ui.label("🫂 Must be on the same team").classes("font-semibold")
                        together_a = ui.select(options=option_select, label="Person A", with_input=True, clearable=True).classes('w-40')
                        together_b = ui.select(options=option_select, label="Person B", with_input=True, clearable=True).classes('w-40')

                        ui.button("Add", on_click=lambda: (upload_card.set_visibility(False),relation_card.set_visibility(True), add_constraint(together_a.value, together_b.value, "TOGETHER")))

                    with ui.column().classes("items-center"):
                        ui.label("🚫 Must be on different teams").classes("font-semibold")
                        separate_a = ui.select(options=option_select, label="Person A", with_input=True, clearable=True).classes('w-40')
                        separate_b = ui.select(options=option_select, label="Person B", with_input=True, clearable=True).classes('w-40')
                        
                        ui.button("Add", on_click=lambda: (upload_card.set_visibility(False),relation_card.set_visibility(True),add_constraint(separate_a.value, separate_b.value, "SEPARATE")))
                    
            with ui.column().classes("items-center w-full"):
                
                columns = [
                    {'name': 'name_1', 'label': 'Name 1', 'field': 'name_1', 'sortable': True, 'align': 'left'},
                    {'name': 'name_2', 'label': 'Name 2', 'field': 'name_2', 'sortable': True, 'align': 'left'},
                    {'name': 'relation', 'label': 'Relation', 'field': 'relation', 'sortable': True, 'align': 'left'},
                #   {'name': 'weight', 'label': 'Weight', 'field': 'weight'},
                #   {'name': 'description', 'label': 'Description', 'field': 'description'}
                    ]
            
                def handle_upload(e):
                    content = e.content.read().decode('utf-8')

                    # Auto detect delimiter (tab or comma)
                    delimiter = '\t' if '\t' in content else ','

                    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
                    rows = list(reader)
                    
                    if rows:
                        relation_data.clear()
                        for r in rows:
                            try: 
                                person_1 = person_dict.get(r['uuid_1'])
                                person_2 = person_dict.get(r['uuid_2'])
                                id_1 = person_1.id
                                id_2 = person_2.id

                                relation_data.append({
                                    'id_1': id_1,
                                    'id_2': id_2,
                                    'uuid_1': r['uuid_1'],
                                    'name_1': r['name_1'],
                                    'uuid_2': r['uuid_2'],
                                    'name_2': r['name_2'],
                                    'relation': r['relation'],
                                    'weight': r['weight'],
                                    'description': r['description']
                                })
                                
                            except KeyError as e:
                                ui.notify(f"Invalid file there is an uuid that does not exist in the people table", color='negative')
                                upload_card.reset()
                                return

                        relation_table.update_rows(rows)
                        relation_card.set_visibility(True)                
                        
                    else:
                        ui.notify('Error in reading csv file', color='negative')
                        upload_card.reset()

            
                upload_card = ui.upload(
                    label="Upload relations file",
                    on_upload=lambda e: handle_upload(e),
                    multiple=False,
                    auto_upload=True,
                    max_file_size=1 * 1024 * 1024, # 1 Mb
                    max_files=1,
                    on_rejected=lambda e: ui.notify(f"File rejected: only allow .csv with max size of 1 Mb", color='negative'),
                ).props('accept=.csv,txt') 
                    
                with ui.card().classes('w-full') as relation_card:
                        relation_table = ui.table(columns=columns, rows=[],row_key='name',).classes('h-52 items-center w-full').props('virtual-scroll')
                        ui.input('Search name').bind_value(relation_table, 'filter')
                        
                        relation_table.add_slot('body-cell-relation', '''
                                    <q-td key="relation" :props="props">
                                        <q-badge :color="props.value == 'TOGETHER' ? 'blue' : 'orange'">
                                            {{ props.value }}
                                        </q-badge>
                                    </q-td>
                                ''')
                ui.button("Clear all relations", color="orange",on_click=lambda: (clear_relations(relation_card))).classes("bg-red-600 text-white")
                ui.button("Save relations as file", on_click=lambda: create_relations_file()).classes("item-center")

            relation_card.set_visibility(False)
            

        ui.button(
            "RUN ALGORITHM",
                on_click=lambda: run_optimizer()
                ).classes("bg-primary text-white")        
    
         #These start hidden
        separator_line = ui.separator().classes("hidden")
        format_setting_container = ui.column().classes("w-full max-w-4xl mx-auto gap-4 hidden")
        team_container = ui.column().classes("w-full max-w-4xl mx-auto gap-4 hidden")
        label_info_chart = ui.label("In the charts the answers are translated into points as follows: Yes = 3, Maybe = 1, and No = 0.").classes("mt-[3rem] text-sm hidden")
        chart_container = ui.row().classes("w-full justify-center hidden")


# Toggle visibility function
def show_loading():
    loading_overlay.classes(remove='hidden')

def hide_loading():
    loading_overlay.classes(add='hidden')


# Compute stats
def compute_stats(team_members: list[Person]) -> dict:
    total = len(team_members)
    leadership = sum(p.a1.value for p in team_members)
    creativity_total = sum(p.a2.value for p in team_members)
    bible_knowledge_total = sum(p.a3.value for p in team_members)
    physcially_fit_total = sum(p.a4.value for p in team_members)
    musicians_total = sum(p.a5.value for p in team_members)
    camp_experience_total = sum(p.a6.value for p in team_members)
    acting_total = sum(p.a7.value for p in team_members)
    prop_design_total = sum(p.a8.value for p in team_members)
    
    
    total_male = sum(1 for p in team_members if p.gender == Gender.MALE and p.get_age() > 24)
    total_female = sum(1 for p in team_members if p.gender == Gender.FEMALE and p.get_age() > 24)
    total_youth = sum(1 for p in team_members if 13 <= p.get_age() <= 24)
    total_kids = sum(1 for p in team_members if 5 <= p.get_age() <= 12)
    total_babies = sum(1 for p in team_members if p.get_age() < 5)
    return {'total': total, 
            'leadership': leadership, 
            'creativity': creativity_total,
            'bible_knowledge': bible_knowledge_total,
            'physcially_fit': physcially_fit_total,
            'musicians': musicians_total, 
            'camp_experience': camp_experience_total,
            'acting': acting_total,
            'prop_design': prop_design_total,
            'male': total_male,
            'female': total_female,
            'youth': total_youth,
            'kids': total_kids,
            'babies': total_babies
            }

# Run optimizer
async def run_optimizer():
    global teams_data, team_stats
    show_loading()
    
    try:
        people = await run.io_bound(lambda: main.run_formation(relation_data))
        if people is None:
            print("No solution found")
            ui.notify("No solution found", color="negative")
            return

        raw_teams: dict[int, list[Person]] = {}
        for p in people:
            raw_teams.setdefault(p.team, []).append(p)
        

        teams_data = sorted(raw_teams.items())

        for team, members in teams_data:
            stats = compute_stats(members)
            team_stats[team] = stats

        update_team_ui()
        
            
    except Exception as e:
        ui.notify(f"Error running optimizer: {e}", color="negative")
        print(f"Error: {e}")
    
    finally:
        hide_loading()

# Save current solution
def save_solution():
    try:
        if fm.last_model is not None:
            os.makedirs("solutions", exist_ok=True)
            fm.last_model.write("solutions/last_saved.sol")
            ui.notify("Solution saved as 'last_saved.sol'", color="positive")
        else:
            ui.notify("No model found to save", color="negative")
    except Exception as e:
        ui.notify(f"Error saving solution: {e}", color="negative")

# Update team + chart UI
def update_team_ui():
    global team_container, chart_container, label_info_chart
    separator_line.classes(remove='hidden')
    format_setting_container.classes(remove='hidden')
    team_container.classes(remove='hidden')
    chart_container.classes(remove='hidden')
    label_info_chart.classes(remove='hidden')

    format_setting_container.clear()
    team_container.clear()
    chart_container.clear()
    team_cards.clear()
    
    def change_sort_format(e):
        team_container.clear()
        chart_container.clear()
        team_cards.clear()
        display_teams(e)

    with format_setting_container:
        selectSortFormatOptions = ["Alphabetical", "Age"]
        selectSortFormat = ui.select(options=selectSortFormatOptions, value=selectSortFormatOptions[0], on_change=change_sort_format)
        
    team_container.clear()
    chart_container.clear()

    def display_teams(selectSortFormat):
        for team, members in teams_data:
            with team_container:
                stat = team_stats[team]
                with ui.expansion(f'Team {team}', icon='group',caption=f'Total: {stat["total"]} | Male: {stat["male"]} | Female: {stat["female"]} | Youth: {stat["youth"]} | Kids: {stat["kids"]} | Babies: {stat["babies"]} | Musicians {stat["musicians"]}').classes('w-full') as exp:
                    with ui.column().classes("pl-4"):
                        # Categorize by age + gender
                        def sort_alpha():
                            # Sort members alphabetically
                            sorted_members = sorted(members, key=lambda x: (x.first_name.lower(), x.last_name.lower()))
                            num = 0
                            for person in sorted_members:
                                num += 1
                                ui.markdown(f"{num}. {person.first_name} {person.last_name} {label_roles(person)}").classes("text-sm")
                                team_cards.append(exp)

                        def sort_age():
                            def get_age_category(person: Person) -> str:
                                age = person.get_age()
                                if age > 24:
                                    return "Male" if person.gender == Gender.MALE else "Female"
                                elif 13 <= age <= 24:
                                    return "Youth"
                                elif 5 <= age <= 12:
                                    return "Kids"
                                else:
                                    return "Babies"

                            # Inside your UI rendering:
                            categories = {
                                "Male": [],
                                "Female": [],
                                "Youth": [],
                                "Kids": [],
                                "Babies": [],
                            }

                            # Fill buckets
                            for m in members:
                                cat = get_age_category(m)
                                categories[cat].append(m)

                            # Display in order, sorted alphabetically within each category
                            category_order = ["Male", "Female", "Youth", "Kids", "Babies"]
                            num = 0

                            for cat in category_order:
                                people = sorted(categories[cat], key=lambda x: (x.first_name.lower(), x.last_name.lower()))
                                if people:
                                    ui.label(f"{cat} - {len(people)}").classes("font-semibold mt-2")
                                    for person in people:
                                        num += 1
                                        ui.markdown(f"{num}. {person.first_name} {person.last_name} {label_roles(person)}").classes("text-sm")
                                        
                                        team_cards.append(exp)
                        
                        if selectSortFormat.value == "Alphabetical":
                            sort_alpha()
                        elif selectSortFormat.value == "Age":
                            sort_age()                        

        labels = [f'Team {team}' for team, _ in teams_data]
        leadership_scores = [team_stats[team]['leadership'] for team, _ in teams_data]
        creativity_scores = [team_stats[team]['creativity'] for team, _ in teams_data]
        bible_knowledge_scores = [team_stats[team]['bible_knowledge'] for team, _ in teams_data]
        physical_fit_scores = [team_stats[team]['physcially_fit'] for team, _ in teams_data]
        musicians_scores = [team_stats[team]['musicians'] for team, _ in teams_data]
        camp_experience_scores = [team_stats[team]['camp_experience'] for team, _ in teams_data]
        acting_scores = [team_stats[team]['acting'] for team, _ in teams_data]
        prop_design_scores = [team_stats[team]['prop_design'] for team, _ in teams_data]
        
        

        with chart_container:
            ui.echart(
                {
                'title': {'text': 'Total leadership score score per team'},
                'tooltip': {},
                'xAxis': {'type': 'category', 'data': labels},
                'yAxis': {'type': 'value'},
                'series': [{
                    'type': 'bar',
                    'data': leadership_scores,
                    'itemStyle': {'color': '#4F46E5'}
                }]
            }).classes("w-full max-w-4xl")
            
        with chart_container:
            ui.echart(
                {
                'title': {'text': 'Total creativity score per team'},
                'tooltip': {},
                'xAxis': {'type': 'category', 'data': labels},
                'yAxis': {'type': 'value'},
                'series': [{
                    'type': 'bar',
                    'data': creativity_scores,
                    'itemStyle': {'color': '#57b8ff'}
                }]
            }).classes("w-full max-w-4xl")
        
        with chart_container:
            ui.echart(
                {
                'title': {'text': 'Total Bible knowledge score per team'},
                'tooltip': {},
                'xAxis': {'type': 'category', 'data': labels},
                'yAxis': {'type': 'value'},
                'series': [{
                    'type': 'bar',
                    'data': bible_knowledge_scores,
                    'itemStyle': {'color': '#c83e4d'}
                }]
            }).classes("w-full max-w-4xl")   
        
        with chart_container:
            ui.echart(
                {
                'title': {'text': 'Total physically fit score per team'},
                'tooltip': {},
                'xAxis': {'type': 'category', 'data': labels},
                'yAxis': {'type': 'value'},
                'series': [{
                    'type': 'bar',
                    'data': physical_fit_scores,
                    'itemStyle': {'color': '#fbb13c'}
                }]
            }).classes("w-full max-w-4xl")
            
        with chart_container:
            ui.echart(
                {
                'title': {'text': 'Total musicians score per team'},
                'tooltip': {},
                'xAxis': {'type': 'category', 'data': labels},
                'yAxis': {'type': 'value'},
                'series': [{
                    'type': 'bar',
                    'data': musicians_scores,
                    'itemStyle': {'color': '#fe6847'}
                }]
            }).classes("w-full max-w-4xl")
        
        with chart_container:
            ui.echart(
                {
                'title': {'text': 'Total camp experience score per team'},
                'tooltip': {},
                'xAxis': {'type': 'category', 'data': labels},
                'yAxis': {'type': 'value'},
                'series': [{
                    'type': 'bar',
                    'data': camp_experience_scores,
                    'itemStyle': {'color': '#63C7B2'}
                }]
            }).classes("w-full max-w-4xl")
        
        with chart_container:
            ui.echart(
                {
                'title': {'text': 'Total acting score per team'},
                'tooltip': {},
                'xAxis': {'type': 'category', 'data': labels},
                'yAxis': {'type': 'value'},
                'series': [{
                    'type': 'bar',
                    'data': acting_scores,
                    'itemStyle': {'color': '#d5b942'}
                }]
            }).classes("w-full max-w-4xl")
        
        with chart_container:
            ui.echart(
                {
                'title': {'text': 'Total prop design score per team'},
                'tooltip': {},
                'xAxis': {'type': 'category', 'data': labels},
                'yAxis': {'type': 'value'},
                'series': [{
                    'type': 'bar',
                    'data': prop_design_scores,
                    'itemStyle': {'color': '#7dc95e'}
                }]
            }).classes("w-full max-w-4xl")
            
            
    # Scroll down to the results
    ui.run_javascript('''
    let start = window.scrollY;
    let end = document.body.scrollHeight - 2700; // document.body.scrollHeight;// Adjust this value to the desired scroll position
    let distance = end - start;
    let duration = 1500; // duration in ms
    let startTime = performance.now();

    requestAnimationFrame(function step(currentTime) {
        let elapsed = currentTime - startTime;
        let progress = Math.min(elapsed / duration, 1);
        let ease = progress < 0.5
            ? 2 * progress * progress 
            : -1 + (4 - 2 * progress) * progress;

        window.scrollTo(0, start + distance * ease);

        if (progress < 1) {
            requestAnimationFrame(step);
        }
    });
    ''')
    # Display teams based on selected sort format
    display_teams(selectSortFormat)

def label_roles(person : Person) -> str:
    roles = []
    if person.a1 == AnswerOption.YES:
        roles.append("👑") 
    elif person.a1 == AnswerOption.MAYBE:
        roles.append("(👑)")
        
    if person.a2 == AnswerOption.YES:
        roles.append("💡")
    elif person.a2 == AnswerOption.MAYBE:
        roles.append("(💡)")
        
    if person.a3 == AnswerOption.YES:
        roles.append("📖")
    elif person.a3 == AnswerOption.MAYBE:
        roles.append("(📖)")
        
    if person.a4 == AnswerOption.YES:
        roles.append("🏃")
    elif person.a4 == AnswerOption.MAYBE:
        roles.append("(🏃)")
        
    if person.a5 == AnswerOption.YES:
        roles.append("🎶")
        
    if person.a6 == AnswerOption.NO:
        roles.append("🆕")
        
    if person.a7 == AnswerOption.YES:
        roles.append("🕺")
    elif person.a7 == AnswerOption.MAYBE:
        roles.append("(🕺)")

    if person.a8 == AnswerOption.YES:
        roles.append("🎨")
        
    return ' '.join(roles) if roles else ""
    
relation_data = []

def add_constraint(person_a, person_b, relation_type):
    global relation_data, relation_table

    if not person_a or not person_b or person_a == person_b:
        ui.notify("Invalid selection: cannot add relation on the same person", color="red")
        return

    uuid_1, name_1, id_1 = person_a
    uuid_2, name_2, id_2 = person_b

    # Check for direct duplicate or conflict
    for relation in relation_data:
        u1, u2 = relation['uuid_1'], relation['uuid_2']
        rel_type = relation['relation']

        if (
            (u1 == uuid_1 and u2 == uuid_2) or
            (u1 == uuid_2 and u2 == uuid_1)
        ):
            if rel_type == relation_type:
                ui.notify("Invalid selection: relation already exists", color="red")
            else:
                ui.notify(f"Invalid conflict: {name_1} and {name_2} already have a '{rel_type}' constraint", color="red")
            return

    # Build TOGETHER graph
    from collections import defaultdict, deque
    graph = defaultdict(set)
    for r in relation_data:
        if r['relation'].upper() == 'TOGETHER':
            graph[r['uuid_1']].add(r['uuid_2'])
            graph[r['uuid_2']].add(r['uuid_1'])

    # Transitivity logic
    def is_transitively_connected(start, target):
        visited = set()
        queue = deque([start])
        while queue:
            current = queue.popleft()
            if current == target:
                return True
            for neighbor in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    # Prevent redundant transitive TOGETHER
    if relation_type.upper() == 'TOGETHER':
        if is_transitively_connected(uuid_1, uuid_2):
            ui.notify(f"Invalid transitive relation: {name_1} is already connected to {name_2} via other people", color="red")
            return

    # Prevent SEPARATE between people already transitively together
    if relation_type.upper() == 'SEPARATE':
        if is_transitively_connected(uuid_1, uuid_2):
            ui.notify(f"Invalid logic: cannot separate {name_1} and {name_2} — they are already transitively connected by TOGETHER constraints", color="red")
            return
    
    # Add new valid relation
    relation_data.append({
        'id_1': id_1,
        'id_2': id_2,
        'uuid_1': uuid_1,
        'name_1': name_1,
        'uuid_2': uuid_2,
        'name_2': name_2,
        'relation': relation_type,
        'weight': 1,
        'description': '',
    })

    relation_table.add_row({
        'name_1': name_1,
        'name_2': name_2,
        'relation': relation_type,
    })
    relation_table.run_method('scrollTo', len(relation_table.rows) - 1)

    ui.notify(f"Added constraint: {name_1} - {name_2} ({relation_type})")
    
    # Relation logic:
    # A == B - ❌ Invalid (same person)
    # A ↔ B already exists - ❌ Duplicate or conflict
    # A–B–C exists and A–C added (TOGETHER) - ❌ Redundant via transitivity
    # A->B & B–>C exists and A–C added (SEPARATE) - ❌ Conflict (can’t separate A–C)
    
def create_relations_file():
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    path = os.path.join("data/relations", f"relations_{timestamp}.csv")

    with open(path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['uuid_1', 'name_1', 'uuid_2', 'name_2', 'relation', 'weight', 'description'])
        for row in relation_data:
            writer.writerow([row['uuid_1'], row['name_1'], row['uuid_2'], row['name_2'], row['relation'], row['weight'], row['description']])

    ui.notify("Saved the relation file")
    
def clear_relations(relation_card):
    global relation_data, relation_table
    relation_data.clear()
    relation_table.rows.clear()
    relation_card.set_visibility(False)
    ui.notify("Cleared all relations")
