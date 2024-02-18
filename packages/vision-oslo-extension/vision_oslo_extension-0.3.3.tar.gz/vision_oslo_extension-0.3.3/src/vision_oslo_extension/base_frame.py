

import tkinter as tk
# try:
#     from shared_contents import SharedVariables # for development
# except ModuleNotFoundError:
#     from vision_oslo_extension.shared_contents import SharedVariables # relative import

# from shared_contents import SharedVariables # for development
from vision_oslo_extension.shared_contents import SharedVariables # relative import

class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def create_frame(self, fill=None, row_weights=None, column_weights=None):
        frame = tk.Frame(self)
        if fill:
            frame.pack(fill=fill)
        if row_weights:
            for i, weight in enumerate(row_weights):
                frame.rowconfigure(i, weight=weight)
        if column_weights:
            for i, weight in enumerate(column_weights):
                frame.columnconfigure(i, weight=weight)
        return frame
    
    def get_entry_value(self):
        user_input = SharedVariables.sim_variable.get()
        print("User Input: ", user_input )
        #return user_input

    def button_callback(self,target_page):
        self.get_entry_value()
        self.controller.show_frame(target_page)
