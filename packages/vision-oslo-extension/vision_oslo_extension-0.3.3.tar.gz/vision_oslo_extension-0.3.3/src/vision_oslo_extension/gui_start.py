
# Third Party

import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog
#from tkinter import messagebox
#from PIL import Image
#import numpy as np 
#from subprocess import check_output 
# import pandas as pd
import subprocess
import os

# Loading subfunctions
# try:
#     from main_page_frame import PageOne, PageTwo, PageThree, PageFour
#     from extraction_frame import F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14
#     from processing_frame import P01, P02, P03, P04, P05, P06, P07, P08
#     from check_frame import C01, C02, C03
#     from shared_contents import SharedVariables
# except ModuleNotFoundError:
#     from vision_oslo_extension.main_page_frame import PageOne, PageTwo, PageThree, PageFour
#     from vision_oslo_extension.extraction_frame import F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14
#     from vision_oslo_extension.processing_frame import P01, P02, P03, P04, P05, P06, P07, P08
#     from vision_oslo_extension.check_frame import C01, C02, C03
#     from vision_oslo_extension.shared_contents import SharedVariables


# from main_page_frame import PageOne, PageTwo, PageThree, PageFour
# from extraction_frame import F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14
# from processing_frame import P01, P02, P03, P04, P05, P06, P07, P08
# from check_frame import C01, C02, C03
# from shared_contents import SharedVariables

from vision_oslo_extension.main_page_frame import PageOne, PageTwo, PageThree, PageFour
from vision_oslo_extension.extraction_frame import F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14
from vision_oslo_extension.processing_frame import P01, P02, P03, P04, P05, P06, P07, P08, P08, P09, P10, P11, P12
from vision_oslo_extension.check_frame import C01, C02, C03
from vision_oslo_extension.shared_contents import SharedVariables,SharedMethods

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold")
        self.sub_title_font = tkfont.Font(family='Helvetica', size=12, weight="bold")
        self.big_text_font = tkfont.Font(family='Helvetica', size=10, weight="bold")
        self.text_font = tkfont.Font(family='Helvetica', size=10)
        # root.geometry('300x200')
        self.title('Vision-Oslo Extension')

        # define the top bar menu  'variible called menu
        menu = tk.Menu(self)
        self.config(menu = menu)
        # sub-menu 1 = filemenu
        filemenu = tk.Menu(menu)
        menu.add_cascade(label='File', menu = filemenu)
        filemenu.add_command(label= 'Select Simulation', command = lambda: SampleApp.open_simulation(self))
        filemenu.add_command(label= 'Open Configuration File', command = lambda: SampleApp.open_file_dialog(self))
        filemenu.add_separator()
        filemenu.add_command(label= 'Exit', command = self.quit)

        # sub-menu 2 import template
        getmenu = tk.Menu(menu)
        menu.add_cascade(label='Import', menu = getmenu)
        getmenu.add_command(label= 'Text - FeederList.txt',command = lambda: SharedMethods.copy_example_files('FeederList.txt'))
        getmenu.add_command(label= 'Text - BranchList.txt',command = lambda: SharedMethods.copy_example_files('BranchList.txt'))
        getmenu.add_command(label= 'Text - BranchListNode.txt',command = lambda: SharedMethods.copy_example_files('BranchListNode.txt'))
        getmenu.add_command(label= 'Text - TransformerList.txt',command = lambda: SharedMethods.copy_example_files('TransformerList.txt'))
        getmenu.add_command(label= 'Text - TrainList.txt',command = lambda: SharedMethods.copy_example_files('TrainList.txt'))
        getmenu.add_command(label= 'Excel - (AC) For Average Power',command = lambda: SharedMethods.copy_example_files('power_template.xlsx'))
        getmenu.add_command(label= 'Excel - (AC) For IF Protection',command = lambda: SharedMethods.copy_example_files('protection_template.xlsx'))
        getmenu.add_command(label= 'Excel - (AC) For New SP Connect',command = lambda: SharedMethods.copy_example_files('new_connection_template.xlsx'))
        getmenu.add_command(label= 'Excel - (AC) For OLE Rating',command = lambda: SharedMethods.copy_example_files('ole_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For TRU Summary',command = lambda: SharedMethods.copy_example_files('TRU_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For Main DCCB Summary',command = lambda: SharedMethods.copy_example_files('mainCB_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For DCBB Summary',command = lambda: SharedMethods.copy_example_files('DCBB_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For Neg ETE Summary',command = lambda: SharedMethods.copy_example_files('NegETE_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For Imp Bond Summary',command = lambda: SharedMethods.copy_example_files('ImpBond_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - For Data Input')


        # sub-menu 2 = helpmenu
        helpmenu = tk.Menu(menu)
        menu.add_cascade(label='Help', menu = helpmenu)
        helpmenu.add_command(label='About',command = self.show_about_popup)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree, PageFour, \
                  F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14, \
                    P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, P11, P12, \
                        C01, C02, C03):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def show_about_popup(self):
        about_popup = tk.Toplevel(self)
        about_popup.title("About-Copyright")

        about_text = "VISION-OSLO extension, version 1.0 (UNDER TEST)"
        about_font = tkfont.Font(family='Helvetica', size=11, weight="bold")
        about_label = tk.Label(about_popup, text=about_text, font = about_font, padx=10, pady=10)
        about_label.pack()

        info_text = "This is developed by Jieming Ye. \
            Copyright to Network Rail, Route Services, Engineering Services. Publish Date: Jan/2024. \
                For support please consult Jieming.Ye@networkrail.co.uk"
        info_label = tk.Message(about_popup, text=info_text, aspect = 800, padx=10, pady=10)
        info_label.pack()

        # Center the popup window on the screen
        about_popup.geometry("+%d+%d" % (self.winfo_rootx() + self.winfo_width() // 2 - about_popup.winfo_reqwidth() // 2,
                                         self.winfo_rooty() + self.winfo_height() // 2 - about_popup.winfo_reqheight() // 2))
    
    
    def open_simulation(self):
        initial_dir = os.getcwd()
        file_path = filedialog.askopenfilename(title="Select Simulation",initialdir=initial_dir)
        if file_path:
            print(f"Selected file: {file_path}")
            file_name = os.path.basename(file_path)
            file_name_parts = file_name.split('.')
        
            # Only the first part of the file name (before the dot)
            simname = file_name_parts[0] if file_name_parts else file_name

            print(simname)

            SharedVariables.sim_variable.set(simname)

            # # Call the method in StartPage to update the Entry widget
            # if 'StartPage' in self.frames:
            #     start_page = self.frames['StartPage']
            #     start_page.update_simulation_entry(simname)

    
    # Create a function to be called when the "Open" menu option is clicked
    def open_file_dialog(self):
        initial_dir = os.getcwd()  # Get the current working directory
        file_path = filedialog.askopenfilename(title="Select a file",initialdir=initial_dir)
        if file_path:
            print(f"Selected file: {file_path}")
            
            print('\033[1;33m') # color control warning message yellow
            print("WARNING: DO NOT EXIT THE PROGRAME BEFORE SAVING THE OPENED FILE.")
            print('\033[1;0m') # color control warning message reset

            self.open_file(file_path)


    def open_file(self, file_path):
        try:
            subprocess.Popen(['start', '', file_path], shell=True,close_fds=True)
            #subprocess.Popen(['start', '/B','', file_path], shell=True,close_fds=True)
            # command = 'start '+file_path
            # print(command)
            # os.system(command)

            # On macOS, you can use 'open' instead of 'start'
            # subprocess.run(['open', file_path], check=True)

        except Exception as e:
            print(f"Error opening file with default app: {e}")


class StartPage(tk.Frame): # define another object of first page

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.headframe = self.create_frame(fill=tk.BOTH)
        self.nameframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 6))
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(4, 1))
        self.infoframe = self.create_frame(fill=tk.BOTH)

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Welcome to VISION-OSLO Add-In',font = controller.title_font)
        head.pack()
        
        text1 = tk.Label(master=self.nameframe, text = 'Simulation Name',font = controller.text_font)
        text1.grid(row = 0, column = 0) # sticky n alight to top center part

        SharedVariables.sim_variable = tk.StringVar()
        entry1 = tk.Entry(master=self.nameframe,width = 40,textvariable = SharedVariables.sim_variable)
        entry1.grid(row = 0,column = 1)

        # explain1 = tk.Message(master=self.optionframe, text = 'Pre-Model Information Prepare: create VISION-OSLO ready information',aspect = 600, font = controller.text_font)
        # explain1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)
        explain1 = tk.Label(master=self.optionframe, text = 'Pre-Model Information Prepare: create VISION-OSLO ready information', font = controller.text_font)
        explain1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        button1 = tk.Button(master=self.optionframe, text = 'Model Prepare', command=lambda: self.button_callback("PageOne"))
        button1.grid(row = 0, column = 1, sticky = "w", padx=5, pady=5)

        explain2 = tk.Label(master=self.optionframe, text = 'Model Check Report: check model report. A working VISION-OSLO model is required', font=controller.text_font)
        explain2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        #button2 = tk.Button(master=optionframe, text = 'Model Check', command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(master=self.optionframe, text = 'Model Check', command=lambda: self.button_callback("PageTwo"))
        button2.grid(row = 1, column = 1, sticky = "w", padx=5, pady=5)

        explain3 = tk.Label(master=self.optionframe, text = 'Default OSLO Extraction: A VISION-OSLO simulation result (oof) file is required.',font = controller.text_font)
        explain3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)  

        button3 = tk.Button(master=self.optionframe, text = 'Result Extraction', command=lambda: self.button_callback("PageThree"))
        button3.grid(row = 2, column = 1, sticky = "w", padx=5, pady=5)

        explain4 = tk.Label(master=self.optionframe, text = 'Custmised Post-Processing: A VISION-OSLO simulation result (oof) file is required.',font = controller.text_font)
        explain4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)  

        button4 = tk.Button(master=self.optionframe, text = 'Result Process', command=lambda: self.button_callback("PageFour"))
        button4.grid(row = 3, column = 1, sticky = "w", padx=5, pady=5)

        diclaimer = tk.Label(master=self.infoframe, text = 'Version 1.0  CopyRight @ 2023')
        diclaimer.pack()
      
        # label = tk.Label(self, text="This is the start page")
        # label.pack(side="top", fill="x", pady=10)

        # button1 = tk.Button(self, text="Go to Page One",
        #                     command=lambda: controller.show_frame("PageOne"))
        # button2 = tk.Button(self, text="Go to Page Two",
        #                     command=lambda: controller.show_frame("PageTwo"))
        # button1.pack()
        # button2.pack()
    
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

    # def update_simulation_entry(self, simname):
    #     # Update the Entry widget with the selected simulation name
    #     SharedVariables.sim_variable.set(simname)



# programme running
if __name__ == '__main__':
    app = SampleApp()
    app.mainloop() 