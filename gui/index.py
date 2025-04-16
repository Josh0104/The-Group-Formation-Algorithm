from nicegui import ui, run, app
import csv_reader as cr
import formation as fm
from formation import Person
from person import Gender
import os
import main as main
from gui.layout import add_layout

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

@ui.page('/')
def dashboard() -> None:
    add_layout()
                
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
                ui.button("Add", on_click=lambda: add_constraint(together=True))

            with ui.column().classes("items-center"):
                ui.label("🚫 Must be on different teams").classes("font-semibold")
                separate_a = ui.select(options=option_select, label="Person A", with_input=True,
        on_change=lambda e: ui.notify(e.value)).classes('w-40')
                separate_b = ui.select(options=option_select, label="Person B", with_input=True,
        on_change=lambda e: ui.notify(e.value)).classes('w-40')
                ui.button("Add", on_click=lambda: add_constraint(together=False))

        ui.row().classes("mt-4 gap-4")
        ui.button(
            "RUN OPTIMIZER WITH CONSTRAINTS",
                on_click=lambda: run_optimizer()
                ).classes("bg-primary text-white")        
        ui.button("SAVE CURRENT SOLUTION", on_click=save_solution).classes("bg-green-600 text-white")
    
    
        with loading_container:
            ui.spinner(size='lg', color='primary').props('thickness=6')
            ui.label("Optimizing teams... Please wait").classes("text-md")
        

# Compute stats
def compute_stats(team_members: list[Person]) -> dict:
    total = len(team_members)
    leaders = sum(1 for p in team_members if "yes" in p.a1)
    skill_total = sum(p.a4.value for p in team_members if p.a4 is not None)
    return {'total': total, 'leaders': leaders, 'skill': skill_total}

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
    
    team_container = ui.column().classes("w-full max-w-4xl mx-auto mt-8 gap-4")
    chart_container = ui.row().classes("w-full justify-center mt-8")
    team_container.clear()
    team_cards.clear()
    chart_container.clear()

    for team, members in teams_data:
        with team_container:
            with ui.expansion(f'Team {team}', icon='group').classes('w-full') as exp:
                with ui.column().classes("pl-4"):
                    stat = team_stats[team]
                    ui.label(f"👥 Total Members: {stat['total']} | ⭐ Leaders: {stat['leaders']}")
                    with ui.column().classes('gap-0'):
                        num = 0
                        members = sorted(members, key=lambda x: (x.first_name, x.last_name))
                        for member in members:
                            num += 1
                            ui.markdown(f"{num}. {member.first_name} {member.last_name}")
                        
                team_cards.append(exp)

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
        let end = document.body.scrollHeight;// 450; // Adjust this value to the desired scroll position
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
        

# Constraints
def add_constraint(together=True):
    person_a = same_a.value if together else diff_a.value
    person_b = same_b.value if together else diff_b.value
    if not person_a or not person_b or person_a == person_b:
        return
    constraint = (person_a, person_b)
    if together:
        if constraint not in same_team_constraints:
            same_team_constraints.append(constraint)
            ui.notify(f'Added same-team constraint: {person_a} + {person_b}')
    else:
        if constraint not in diff_team_constraints:
            diff_team_constraints.append(constraint)
            ui.notify(f'Added different-team constraint: {person_a} x {person_b}')


    

