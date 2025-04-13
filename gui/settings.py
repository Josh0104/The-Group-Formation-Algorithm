from nicegui import ui
from gui.layout import add_layout

@ui.page('/settings')
def settings():
    add_layout()  # This is required
    ui.label('Settings Page').classes('text-2xl mt-4')