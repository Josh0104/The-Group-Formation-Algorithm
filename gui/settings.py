from nicegui import ui
from header import header

@ui.page('/settings')
def settings():
    header()
    ui.label('Settings Page').classes('text-2xl mt-4')