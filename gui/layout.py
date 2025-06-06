# gui/layout.py
from nicegui import app, ui

def add_layout():

    dark = ui.dark_mode()
    if app.storage.general.get('dark_mode', False):
        dark.enable()
    else:
        dark.disable()
    
    with ui.header().classes('row items-center accent text-white dark:bg-blue-950'):
        ui.button(icon='r_list', on_click=lambda: left_drawer.toggle()).props('flat color=white')
        ui.label('Group Formation Builder').classes('text-lg')
        ui.space()
        ui.button('Dashboard', on_click=lambda: ui.navigate.to('/')).props('color=dark:blue-900')
        # ui.button('Results', on_click=lambda: ui.navigate.to('/results')).props('color=dark:blue-900')
        ui.button('Settings', on_click=lambda: ui.navigate.to('/settings')).props('color=dark:blue-900')

    with ui.left_drawer(value=False).classes("w-full dark:bg-slate-900 bg-slate-200") as left_drawer:
        ui.label('Side Menu')
        ui.button('Quit', on_click=app.shutdown, color='negative')


    with ui.footer(value=False).classes('dark:bg-slate-900 flex items-center') as footer:
        ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />')
        with ui.link(target='https://github.com/Josh0104/The-Group-Formation-Algorithm',new_tab=True):
            ui.icon('eva-github').classes('text-3xl text-slate-950')
        # ui.link(text='Link to about'target='camp.cbmbc.org/group-formation', new_tab=True).classes('text-slate-950').props('text-sm')
        ui.label('Version 1.0').classes('align-middle')
        
    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        ui.button(on_click=footer.toggle, icon='contact_support', color='primary').props('fab')

