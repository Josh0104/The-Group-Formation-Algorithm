from nicegui import ui, run
import csv_reader as cr
import formation as fm
import os

# Constants
DATA_PATH = 'data/users.csv'

# Global variables
person_dict = cr.read_csv_pd(DATA_PATH)
teams_data = []  # List of tuples: (team_number, [Person, ...])
team_stats = {}  # Dict[int, dict] of team number to stats

# Constraint tracking
same_team_constraints = []
diff_team_constraints = []

# UI elements
team_cards = []
team_container = ui.column().classes("w-full max-w-4xl mx-auto mt-8 gap-4")  # holds teams output

# Fullscreen loading overlay
loading_overlay = ui.row().classes("fixed inset-0 bg-white bg-opacity-70 z-50 items-center justify-center hidden")
with loading_overlay:
    with ui.column().classes("items-center"):
        loading_spinner = ui.spinner(size='lg', color='primary').props('thickness=6')
        ui.label("Optimizing teams... Please wait").classes("text-md mt-2")

# Helper to recompute team stats
def compute_stats(team_members):
    total = len(team_members)
    leaders = sum(1 for p in team_members if "yes" in p.a1.lower())
    return {'total': total, 'leaders': leaders}

# Run optimizer and update UI
async def run_optimizer():
    global teams_data, team_stats
    loading_overlay.classes(remove='hidden')

    try:
        await run.io_bound(lambda: fm.form_teams(
            people=person_dict,
            number_of_groups=5,
            is_printing_output=False,
            args_output_file=None,
            args_no_output=False
        ))

        output_files = [f for f in os.listdir("output") if f.endswith(".csv")]
        if not output_files:
            ui.notify("No output file found", color="negative")
            return

        latest_file = sorted(output_files, key=lambda f: os.path.getmtime(f"output/{f}"))[-1]
        with open(f"output/{latest_file}", "r") as f:
            lines = f.readlines()[1:]  # skip header
            raw_teams = {}
            for line in lines:
                uuid, first, last, team = line.strip().split(",")
                team = int(team)
                person = person_dict.get(uuid)
                if person:
                    raw_teams.setdefault(team, []).append(person)

        teams_data = sorted(raw_teams.items())
        team_stats = {team: compute_stats(members) for team, members in teams_data}
        update_team_ui()

    finally:
        loading_overlay.classes(add='hidden')

# Update the output UI
def update_team_ui():
    team_container.clear()
    team_cards.clear()

    for team, members in teams_data:
        with team_container:
            with ui.expansion(f'Team {team}', icon='group').classes('w-full') as exp:
                with ui.column().classes("pl-4"):
                    stat = team_stats[team]
                    ui.label(f"👥 Total Members: {stat['total']} | ⭐ Leaders: {stat['leaders']}")
                    for member in members:
                        ui.label(f"• {member.first_name} {member.last_name}")
                team_cards.append(exp)

# Constraint adding (UI only for now)
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

# --- GUI layout ---
with ui.column().classes("items-center w-full"):
    ui.label("Team Optimizer Dashboard").classes("text-3xl font-bold mt-4")
    ui.separator()

    with ui.row().classes("mt-6 justify-center gap-10"):
        with ui.column().classes("items-center"):
            ui.label("Force people on same team").classes("font-semibold")
            same_a = ui.select([f'{p.first_name} {p.last_name}' for p in person_dict.values()], label="Person A")
            same_b = ui.select([f'{p.first_name} {p.last_name}' for p in person_dict.values()], label="Person B")
            ui.button("Add", on_click=lambda: add_constraint(together=True))

        with ui.column().classes("items-center"):
            ui.label("Force people on different teams").classes("font-semibold")
            diff_a = ui.select([f'{p.first_name} {p.last_name}' for p in person_dict.values()], label="Person A")
            diff_b = ui.select([f'{p.first_name} {p.last_name}' for p in person_dict.values()], label="Person B")
            ui.button("Add", on_click=lambda: add_constraint(together=False))

    ui.button("RE-RUN OPTIMIZER WITH CONSTRAINTS", on_click=run_optimizer).classes("mt-6 bg-primary text-white")

# --- App start ---
ui.run()
