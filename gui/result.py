from nicegui import ui
from gui.layout import add_layout

@ui.page('/results')
def results():
    add_layout()
    ui.label('Results Page').classes('text-2xl mt-4')
    ui.label('Here you can view the results of the group formation process.').classes('mt-2')