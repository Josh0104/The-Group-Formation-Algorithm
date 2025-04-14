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
        ui.button('Dashboard', on_click=lambda: ui.navigate.to('/')).props('color=dark:blue-800')
        ui.button('Results', on_click=lambda: ui.navigate.to('/results')).props('color=dark:blue-800')
        ui.button('Settings', on_click=lambda: ui.navigate.to('/settings')).props('color=dark:blue-800')

    with ui.left_drawer(value=False).classes("w-full") as left_drawer:
        ui.label('Side Menu')

    with ui.footer(value=False) as footer:
        ui.label('Version 0.0')
        
    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        ui.button(on_click=footer.toggle, icon='contact_support').props('fab')
