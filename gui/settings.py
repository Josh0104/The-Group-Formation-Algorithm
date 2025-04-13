from nicegui import ui, app
from gui.layout import add_layout

@ui.page('/settings')
def settings():
    add_layout()

    dark = ui.dark_mode()
    is_dark_mode = app.storage.general.get('dark_mode', False)

    with ui.column().classes("items-center w-full"):
        ui.label('⚙️ Settings').classes('text-3xl font-bold align-center mt-4')

        dark = ui.dark_mode()
        
        ui.switch('Dark mode', on_change=lambda e: dark.enable() if e.value else dark.disable()).bind_value(app.storage.general, 'dark_mode')