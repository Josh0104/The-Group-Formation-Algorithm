from nicegui import ui
from person import AnswerOption, Gender, Person


def change_sort_format(format_setting_container,team_container, team_cards,chart_container ,teams_data, e):
    format_setting_container.clear()
    team_container.clear()
    chart_container.clear()
    team_cards.clear()
    display_teams(e.value, teams_data)


def display_teams(select_sort_format_value, teams_data):
    team_cards = []
    team_stats = {}
    
    for team, members in teams_data:
        stats = compute_stats(members)
        team_stats[team] = stats
    
    team_ui_container = ui.column()
    format_setting_container = ui.column().classes("w-full max-w-4xl mx-auto gap-4 ")
    team_container = ui.column().classes("w-full max-w-4xl mx-auto gap-4 ")
    chart_container = ui.row().classes("w-full justify-center ")

    team_ui_container.clear() 
    
    
    with format_setting_container:
        selectSortFormatOptions = ["Alphabetical", "Age"]
        ui.select(options=selectSortFormatOptions, value=selectSortFormatOptions[0], on_change= lambda e: change_sort_format(format_setting_container,team_container, team_cards,chart_container ,teams_data, e))
        
    with team_ui_container:
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
                        
                        if select_sort_format_value== "Alphabetical":
                            sort_alpha()
                        elif select_sort_format_value== "Age":
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

        # ui.label("In the charts the answers are translated into points as follows: Yes = 3, Maybe = 1, and No = 0.").classes("mt-[3rem] text-sm")
        
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