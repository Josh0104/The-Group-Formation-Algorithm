from nicegui import ui

def header():
    # with ui.header().classes('items-center justify-between text-white p-4'):
    #     ui.label('Camp Team Builder').classes('text-xl font-bold')
    #     with ui.row().classes('gap-4'):
    #         ui.button('Home', on_click=lambda: ui.open('/'))
    #         ui.button('Settings', on_click=lambda: ui.open('/settings'))
    # with ui.tabs() as tabs:
    #     one = ui.tab('Home')
    #     two = ui.tab('Settings')
    # with ui.tab_panels(tabs, value=two).classes('w-full'):
    #     with ui.tab_panel(one):
    #         ui.label('First tab')
    #     with ui.tab_panel(two):
    #         ui.label('Second tab')

    with ui.header().classes(replace='row items-center') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        with ui.tabs() as tabs:
            ui.tab('A')
            ui.tab('B')
            ui.tab('C')

    with ui.footer(value=False) as footer:
        ui.label('Footer')

    with ui.left_drawer() as left_drawer:
        ui.label('Side menu')

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

    with ui.tab_panels(tabs, value='A').classes('w-full'):
        with ui.tab_panel('A'):
            ui.label('Content of A')
        with ui.tab_panel('B'):
            ui.label('Content of B')
        with ui.tab_panel('C'):
            ui.label('Content of C')
