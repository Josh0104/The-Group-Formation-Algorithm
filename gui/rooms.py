from nicegui import ui, app
from gui.layout import add_layout

@ui.page('/rooms')
def rooms():
    add_layout()

    with ui.column().classes("items-center w-full"):
        ui.label('🛏️ Room Management').classes('text-3xl font-bold align-center mt-4')
        ui.button("Run Room Formation", on_click=lambda: ui.notify("Room formation process started!")).classes('mt-4')
