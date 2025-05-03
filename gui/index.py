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

# Constants
DATA_PATH = 'data/users.csv'

# Global variables
teams_data: list[tuple] = []
team_stats = {}

# Constraint tracking
same_team_constraints = []
diff_team_constraints = []

same_a = None
diff_a = None  
same_b = None
diff_b = None
team_cards = []
loading_container = None
loading = None

# UI elements
loading_container = ui.column().classes("fixed inset-0 z-50 hidden items-center justify-center bg-white/60")

relation_data = []
relation_table = None

@ui.page('/')
def dashboard() -> None:
    global relation_table
    add_layout()
    global team_container, chart_container, format_setting_container
    
    from app_config import args  # access shared args
    person_dict = cr.read_csv_pd(args.input)
    

    # --- Layout --- 
    with ui.column().classes("items-center w-full"):
        
        ui.label("Team Optimizer Dashboard").classes("text-3xl font-bold mt-4")

        # option_select = [f'{p.first_name} {p.last_name}' for p in person_dict.values()]
        option_select: dict = {}
        for p in person_dict.values():
            full_name = f"{p.first_name} {p.last_name}"
            option_select[p.uuid,full_name, p.id] =  [full_name] # rhs value and lhs label
                      
        with ui.row().classes("mt-6 justify-center gap-10"):
            with ui.column().classes("items-center"):
                ui.label("🫂 Must be on the same team").classes("font-semibold")
                together_a = ui.select(options=option_select, label="Person A", with_input=True, clearable=True).classes('w-40')
                together_b = ui.select(options=option_select, label="Person B", with_input=True, clearable=True).classes('w-40')

                ui.button("Add", on_click=lambda: (upload_card.set_visibility(False),relation_expansion.set_visibility(True), add_constraint(together_a.value, together_b.value, "TOGETHER")))

            with ui.column().classes("items-center"):
                ui.label("🚫 Must be on different teams").classes("font-semibold")
                separate_a = ui.select(options=option_select, label="Person A", with_input=True, clearable=True).classes('w-40')
                separate_b = ui.select(options=option_select, label="Person B", with_input=True, clearable=True).classes('w-40')
                
                ui.button("Add", on_click=lambda: (upload_card.set_visibility(False),relation_expansion.set_visibility(True),add_constraint(separate_a.value, separate_b.value, "SEPARATE")))
                
        ui.button("Save and use relations", on_click=lambda: create_relations_file())
        
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
            print(rows)

            if rows:
                # relation_table_dialog.rows = rows
                # relation_table_dialog.update()
                dialog.open()
                relation_card.move(uploaded_card)
                
            else:
                ui.notify('No data found in CSV', color='negative')
        
        upload_card = ui.upload(
            label="Upload relations file",
            on_upload=lambda e: handle_upload(e),
        )

        # Create empty dialog and table first
        dialog = ui.dialog()
        with dialog:
            with ui.card() as uploaded_card:
                ui.label('Uploaded Relations File').classes('text-xl mb-2')
                # relation_table_dialog = ui.table(columns=columns, rows=[], row_key='name',).classes('h-52 items-center w-full').props('virtual-scroll')
            
        with ui.expansion(f'Relation table').classes('w-1/2 justify-center') as relation_expansion:
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

        relation_expansion.set_visibility(False)


        # Upload button
        # ui.label("Or choose a file").classes("text-sm text-yellow-200 mt-2")
        # ui.upload(on_upload=handle_upload).props('accept=".csv"')

        ui.row().classes("mt-4 gap-4")
        ui.button(
            "RUN OPTIMIZER WITH CONSTRAINTS",
                on_click=lambda: run_optimizer()
                ).classes("bg-primary text-white")        
        ui.button("SAVE CURRENT SOLUTION", on_click=save_solution).classes("bg-green-600 text-white")
    
         #These start hidden
        format_setting_container = ui.column().classes("w-full max-w-4xl mx-auto gap-4 hidden")
        team_container = ui.column().classes("w-full max-w-4xl mx-auto gap-4 hidden")
        chart_container = ui.row().classes("w-full justify-center hidden")
        # with loading_container:
        #     ui.spinner(size='lg', color='primary').props('thickness=6')
        #     ui.label("Optimizing teams... Please wait").classes("text-md")
        

# Compute stats
def compute_stats(team_members: list[Person]) -> dict:
    total = len(team_members)
    leaders = sum(1 for p in team_members if "yes" in p.a1)
    skill_total = sum(p.a4.value for p in team_members if p.a4 is not None)
    total_musicians = sum(1 for p in team_members if p.a5 == AnswerOption.YES)
    return {'total': total, 'leaders': leaders, 'skill': skill_total, 'musicians': total_musicians}

# Run optimizer
async def run_optimizer():
    global teams_data, team_stats
    loading_container.classes(remove='hidden')
    
    try:
        people = await run.io_bound(lambda: main.run_formation(relation_data))
        if people is None:
            ui.notify("No solution found", color="negative")
            return
        
        people_dicts = [p.to_dict() for p in people]
        app.storage.user['latest_solution'] = people_dicts # Store the latest solution in app storage user


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
        loading_container.classes(add='hidden')

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
    global team_container, chart_container
    format_setting_container.classes(remove='hidden')
    team_container.classes(remove='hidden')
    chart_container.classes(remove='hidden')

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
        
    team_container = ui.column().classes("w-full max-w-4xl mx-auto gap-4")
    chart_container = ui.row().classes("w-full justify-center mt-8")

    def display_teams(selectSortFormat):
        for team, members in teams_data:
            with team_container:
                stat = team_stats[team]
                with ui.expansion(f'Team {team}', icon='group',caption=f'Total: {stat["total"]} | Musicians {stat["musicians"]}').classes('w-full') as exp:
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
        skills = [team_stats[team]['skill'] for team, _ in teams_data]

        with chart_container:
            ui.echart(
                {
                'title': {'text': 'Total Skill Score per Team'},
                'tooltip': {},
                'xAxis': {'type': 'category', 'data': labels},
                'yAxis': {'type': 'value'},
                'series': [{
                    'type': 'bar',
                    'data': skills,
                    'itemStyle': {'color': '#4F46E5'}
                }]
            }).classes("w-full max-w-4xl")
            
    # Scroll down to the results
    ui.run_javascript('''
    let start = window.scrollY;
    let end = 450; // document.body.scrollHeight;// Adjust this value to the desired scroll position
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
    if "yes" in person.a1:
        roles.append("👑") 
    elif person.a1 == AnswerOption.MAYBE:
        roles.append("(👑)")
        
    if person.a2 == AnswerOption.YES:
        roles.append("💡")
    elif person.a2 == AnswerOption.MAYBE:
        roles.append("(💡)")
        
    if person.a5 == AnswerOption.YES:
        roles.append("🎶")
        
    if person.a3 == AnswerOption.YES:
        roles.append("📖")
        
    if person.a8 == AnswerOption.YES:
        roles.append("🎨")
        
    if person.a7 == AnswerOption.YES:
        roles.append("🕺")
    elif person.a7 == AnswerOption.MAYBE:
        roles.append("(🕺)")
        
    if person.a4 == AnswerOption.YES:
        pass
    if person.a4 == AnswerOption.YES:
        roles.append("🏃")
    if person.a6 == AnswerOption.NO:
        roles.append("🆕")
    return ' '.join(roles) if roles else ""
    
relation_data = []

def add_constraint(person_a, person_b, relation_type):
    global relation_data

    if not person_a or not person_b or person_a == person_b:
        ui.notify("Invalid selection: cannot add relation on the same person", color="red")
        return

    uuid_1, name_1, id_1 = person_a
    uuid_2, name_2, id_2 = person_b

    # STEP 1: Check for direct duplicate or conflict
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

    # STEP 2: Build TOGETHER graph
    from collections import defaultdict, deque
    graph = defaultdict(set)
    for r in relation_data:
        if r['relation'].upper() == 'TOGETHER':
            graph[r['uuid_1']].add(r['uuid_2'])
            graph[r['uuid_2']].add(r['uuid_1'])

    # STEP 3: Transitivity logic
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

    # 3a: Prevent redundant transitive TOGETHER
    if relation_type.upper() == 'TOGETHER':
        if is_transitively_connected(uuid_1, uuid_2):
            ui.notify(f"Invalid transitive relation: {name_1} is already connected to {name_2} via other people", color="red")
            return

    # 3b: Prevent SEPARATE between people already transitively together
    if relation_type.upper() == 'SEPARATE':
        if is_transitively_connected(uuid_1, uuid_2):
            ui.notify(f"Invalid logic: cannot separate {name_1} and {name_2} — they are already transitively connected by TOGETHER constraints", color="red")
            return
    
    # STEP 4: Add new valid relation
    relation_data.append({
        'id_1': id_1,
        'id_2': id_2,
        'uuid_1': uuid_1,
        'name_1': name_1,
        'uuid_2': uuid_2,
        'name_2': name_2,
        'relation': relation_type,
        'weight': 5,
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
    path = os.path.join("data", f"relations_{timestamp}.csv")

    with open(path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['uuid_1', 'name_1', 'uuid_2', 'name_2', 'relation', 'weight', 'description'])
        for row in relation_data:
            writer.writerow([row['uuid_1'], row['name_1'], row['uuid_2'], row['name_2'], row['relation'], row['weight'], row['description']])

    ui.notify("Saved the relation file")
