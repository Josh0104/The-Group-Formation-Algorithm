from nicegui import ui, app
from gui.layout import add_layout
import gui.settings 
import gui.index
import gui.result

def run_gui():
    
    add_layout()
    
    # Run the GUI
    app.native.window_args['text_select'] = True #select the text with native window - https://www.reddit.com/r/nicegui/comments/1gtmvuh/comment/lxq1u1q/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button 
    ui.run(title='Group Formation Builder', native=True, window_size=(1200,800))