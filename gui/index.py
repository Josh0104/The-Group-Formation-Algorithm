from datetime import datetime
from nicegui import ui, run, app, events
import csv_reader as cr
import formation as fm
from formation import Person
from person import Gender, AnswerOption
import os
import main as main
from gui.layout import add_layout
import csv, io

# Constants
DATA_PATH = 'data/users.csv'

# Global variables
person_dict = cr.read_csv_pd(DATA_PATH)
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

@ui.page('/')
def dashboard() -> None:
    add_layout()
    global team_container, chart_container, format_setting_container

    # --- Layout --- 
    with ui.column().classes("items-center w-full"):
        
        ui.label("Team Optimizer Dashboard").classes("text-3xl font-bold mt-4")

        with ui.row().classes("mt-6 justify-center gap-10"):
            with ui.column().classes("items-center"):
                ui.label("🫂 Must be on the same team").classes("font-semibold")
                option_select = [f'{p.first_name} {p.last_name}' for p in person_dict.values()]
                option_select = sorted(option_select)
                together_a = ui.select(options=option_select, label="Person A", with_input=True,
        on_change=lambda e: ui.notify(e.value)).classes('w-40')
                together_b = ui.select(options=option_select, label="Person B", with_input=True,
        on_change=lambda e: ui.notify(e.value)).classes('w-40')
                ui.button("Add", on_click=lambda: 
                    add_constraint(together_a, together_b, "together"))

            with ui.column().classes("items-center"):
                ui.label("🚫 Must be on different teams").classes("font-semibold")
                separate_a = ui.select(options=option_select, label="Person A", with_input=True,
        on_change=lambda e: ui.notify(e.value)).classes('w-40')
                separate_b = ui.select(options=option_select, label="Person B", with_input=True,
        on_change=lambda e: ui.notify(e.value)).classes('w-40')
                ui.button("Add", on_click=lambda: add_constraint({separate_a.value, separate_b.value, "separate" }))
        ui.button("Save relations", on_click=lambda: create_relations_file)
                
        # Create empty dialog and table first
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label('Uploaded Relations File').classes('text-xl mb-2')
                table = ui.table(
                    columns=[
                        {'name': k, 'label': k.replace('_', ' ').title(), 'field': k}
                        for k in ['uuid_1', 'name_1', 'uuid_2', 'name_2', 'relation', 'weight', 'description']
                    ],
                    rows=[],
                    row_key='uuid_1',
                ).classes('w-full')

        # Handle file upload
        def handle_upload(e: events.UploadEventArguments):
            content = e.content.read().decode('utf-8')

            # Auto detect delimiter (tab or comma)
            delimiter = '\t' if '\t' in content else ','

            reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
            rows = list(reader)

            if rows:
                table.rows = rows
                table.update()
                dialog.open()
            else:
                ui.notify('No data found in CSV', color='negative')

        # Upload button
        ui.label("Or choose a file").classes("text-sm text-yellow-200 mt-2")
        ui.upload(on_upload=handle_upload).props('accept=".csv"')

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
        people = await run.io_bound(lambda: main.run_formation())
        people_dicts = [p.to_dict() for p in people]
        app.storage.user['latest_solution'] = people_dicts # Store the latest solution in app storage user

        if people is None:
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
    
        

# Constraints
def add_constraint(select_a, select_b, relation, ):
    global relation_data
    
    relation_data.append({select_a.value, select_b.value, relation})
    
    select_a.value
    print(relation_data)
    
    # person_a = same_a.value if together else diff_a.value
    # person_b = same_b.value if together else diff_b.value
    # if not person_a or not person_b or person_a == person_b:
    #     return
    # constraint = (person_a, person_b)
    # if together:
    #     if constraint not in same_team_constraints:
    #         same_team_constraints.append(constraint)
    #         ui.notify(f'Added same-team constraint: {person_a} + {person_b}')
    # else:
    #     if constraint not in diff_team_constraints:
    #         diff_team_constraints.append(constraint)
    #         ui.notify(f'Added different-team constraint: {person_a} x {person_b}')

def create_relations_file():
    global relation_data
    
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    path = os.path.join("data", f"relations_{timestamp}.csv")
    
    
    with open(path,"w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow("uuid_1, name_1, uuid_2, name_2, relation", "weigh", "description")
        writer.writerows([r.uuid_1, r.name_1, r.uuid_2, r.name_2, r.relation, r.weight, r.description] for r in relation_data)

    

