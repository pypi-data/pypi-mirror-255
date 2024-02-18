
import tkinter as tk

# try:
#     from shared_contents import SharedVariables
#     from base_frame import BasePage
# except ModuleNotFoundError:
#     from vision_oslo_extension.shared_contents import SharedVariables
#     from vision_oslo_extension.base_frame import BasePage


# from shared_contents import SharedVariables
# from base_frame import BasePage
# import oslo_extraction


from vision_oslo_extension.shared_contents import SharedVariables
from vision_oslo_extension.base_frame import BasePage

from vision_oslo_extension import oslo_extraction

class PageOne(BasePage):

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 2")
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()


class PageTwo(BasePage):

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.headframe = self.create_frame(fill=tk.BOTH)
        # self.timeframe = self.create_frame(fill=tk.BOTH, column_weights=(2, 1, 2, 1))
        self.dirframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1))
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), column_weights=(4, 1))
        self.infoframe = self.create_frame(fill=tk.BOTH)

        label = tk.Label(master=self.headframe, text = 'OSLO Model Check / Verification',font = controller.sub_title_font)
        label.pack(side="top", fill="x", pady=2)

        note = tk.Label(master=self.headframe, text = 'Instruction: User expected solve all VISION Model and can click Run to OSLO diagnose page to proceed.',font = controller.text_font)
        note.pack(side="left", fill="x", pady=5)

        explain1 = tk.Label(master=self.optionframe, text = '1. OSLO Information Listing', font = controller.text_font)
        explain1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=2)

        button1 = tk.Button(master=self.optionframe, text = 'Excute 1', command=lambda: self.set_main_option("1","C01"))
        button1.grid(row = 0, column = 1, sticky = "w", padx=5, pady=2)

        explain2 = tk.Label(master=self.optionframe, text = '2: Connection Report / Map', font = controller.text_font)
        explain2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=2)

        button2 = tk.Button(master=self.optionframe, text = 'Excute 2', command=lambda: self.set_main_option("2","C02"))
        button2.grid(row = 1, column = 1, sticky = "w", padx=5, pady=2)

        explain3 = tk.Label(master=self.optionframe, text = '3: Development in process', font = controller.text_font)
        explain3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=2)

        button3 = tk.Button(master=self.optionframe, text = 'Excute 3', command=lambda: self.set_main_option("3","C03"))
        button3.grid(row = 2, column = 1, sticky = "w", padx=5, pady=2)

        # explain4 = tk.Label(master=self.optionframe, text = '4: AC: Meanuseful Processing (BSEN 50388:2022 Annex B)', font = controller.text_font)
        # explain4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=2)

        # button4 = tk.Button(master=self.optionframe, text = 'Excute 4', command=lambda: self.set_main_option("4","P04"))
        # button4.grid(row = 3, column = 1, sticky = "w", padx=5, pady=2)

        # explain5 = tk.Label(master=self.optionframe, text = '5: AC: Provision for development 1', font = controller.text_font)
        # explain5.grid(row = 4, column = 0, sticky = "w", padx=5, pady=2)

        # button5 = tk.Button(master=self.optionframe, text = 'Excute 5', command=lambda: self.set_main_option("5","P05"))
        # button5.grid(row = 4, column = 1, sticky = "w", padx=5, pady=2)

        # explain6 = tk.Label(master=self.optionframe, text = '6: AC: Provision for development 2', font = controller.text_font)
        # explain6.grid(row = 5, column = 0, sticky = "w", padx=5, pady=2)

        # button6 = tk.Button(master=self.optionframe, text = 'Excute 6', command=lambda: self.set_main_option("6","P06"))
        # button6.grid(row = 5, column = 1, sticky = "w", padx=5, pady=2)

        # explain7 = tk.Label(master=self.optionframe, text = '7: DC: Substation Power & RTU Asessment Data Preparation', font = controller.text_font)
        # explain7.grid(row = 6, column = 0, sticky = "w", padx=5, pady=2)

        # button7 = tk.Button(master=self.optionframe, text = 'Excute 7', command=lambda: self.set_main_option("7","P07"))
        # button7.grid(row = 6, column = 1, sticky = "w", padx=5, pady=2)

        # explain8 = tk.Label(master=self.optionframe, text = '8: DC: Substation Protection/ Track CB / ETE Assessment Data Preparation', font = controller.text_font)
        # explain8.grid(row = 7, column = 0, sticky = "w", padx=5, pady=2)

        # button8 = tk.Button(master=self.optionframe, text = 'Excute 8', command=lambda: self.set_main_option("8","P08"))
        # button8.grid(row = 7, column = 1, sticky = "w", padx=5, pady=2)

        # explain9 = tk.Label(master=self.optionframe, text = '9: DC: Provision for Development 1', font = controller.text_font)
        # explain9.grid(row = 8, column = 0, sticky = "w", padx=5, pady=2)

        # button9 = tk.Button(master=self.optionframe, text = 'Excute 9', command=lambda: self.set_main_option("9","P09"))
        # button9.grid(row = 8, column = 1, sticky = "w", padx=5, pady=2)

        # explain10 = tk.Label(master=self.optionframe, text = '10: DC: Provision for Development 2', font = controller.text_font)
        # explain10.grid(row = 9, column = 0, sticky = "w", padx=5, pady=2)

        # button10 = tk.Button(master=self.optionframe, text = 'Excute 10', command=lambda: self.set_main_option("10","P10"))
        # button10.grid(row = 9, column = 1, sticky = "w", padx=5, pady=2)

        # explain11 = tk.Label(master=self.optionframe, text = '11: Smoothed feeder currents', font = controller.text_font)
        # explain11.grid(row = 10, column = 0, sticky = "w", padx=5, pady=2)

        # button11 = tk.Button(master=self.optionframe, text = 'Excute 11', command=lambda: self.set_main_option("11","F11"))
        # button11.grid(row = 10, column = 1, sticky = "w", padx=5, pady=2)

        # explain12 = tk.Label(master=self.optionframe, text = '12: Smoothed branch currents', font = controller.text_font)
        # explain12.grid(row = 11, column = 0, sticky = "w", padx=5, pady=2)

        # button12 = tk.Button(master=self.optionframe, text = 'Excute 12', command=lambda: self.set_main_option("12","F12"))
        # button12.grid(row = 11, column = 1, sticky = "w", padx=5, pady=2)

        # explain13 = tk.Label(master=self.optionframe, text = '13: Supply point persistent currents (development in progress)', font = controller.text_font)
        # explain13.grid(row = 12, column = 0, sticky = "w", padx=5, pady=2)

        # button13 = tk.Button(master=self.optionframe, text = 'Excute 13', command=lambda: self.set_main_option("13","F13"))
        # button13.grid(row = 12, column = 1, sticky = "w", padx=5, pady=2)

        # explain14 = tk.Label(master=self.optionframe, text = '14: Output to data files', font = controller.text_font)
        # explain14.grid(row = 13, column = 0, sticky = "w", padx=5, pady=2)

        # button14 = tk.Button(master=self.optionframe, text = 'Excute 14', command=lambda: self.set_main_option("14","F14"))
        # button14.grid(row = 13, column = 1, sticky = "w", padx=5, pady=2)


        button = tk.Button(self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button.pack(pady = 5)


    def set_main_option(self,value,target_page):
        SharedVariables.main_option = value
        self.controller.show_frame(target_page)
        # test = SharedVariables.main_option
        # print(test)

# OSLO Extraction Page
class PageThree(BasePage):

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.headframe = self.create_frame(fill=tk.BOTH)
        # self.timeframe = self.create_frame(fill=tk.BOTH, column_weights=(2, 1, 2, 1))
        self.dirframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1))
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), column_weights=(4, 1))
        self.infoframe = self.create_frame(fill=tk.BOTH)

        label = tk.Label(master=self.headframe, text = 'OSLO Extraction Option Selection',font = controller.sub_title_font)
        label.pack(side="top", fill="x", pady=2)

        # section1 = tk.Label(master=self.headframe, text = 'Info Enter',font = controller.text_font)
        # section1.pack(side="top", fill="x", pady=2)

        # note = tk.Message(
        #     master=self.headframe, 
        #     text = 'Instruction: User can go to info page entering extraction requirements using excute buttons below',
        #     aspect = 1200, 
        #     font = controller.text_font
        # )
        note = tk.Label(master=self.headframe, text = 'Instruction: User can go to info page entering extraction requirements using excute buttons below',font = controller.text_font)
        note.pack(side="left", fill="x", pady=5)

        # label = tk.Label(master=self.headframe, text = 'This is page one',font = controller.text_font)
        # label.pack(side="top", fill="x", pady=10)
        
        # section1 = tk.Label(master=self.dirframe, text = 'Old Extraction Approach. Entering Information as instructed',font = controller.big_text_font)
        # section1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=2)

        # explain00 = tk.Label(master=self.dirframe, text = 'GO TO CONVENTIONAL WAY', font = controller.text_font)
        # explain00.grid(row = 1, column = 0, sticky = "e", padx=5, pady=2)

        # button00 = tk.Button(master=self.dirframe, text = 'GO TO SCREEN', command=self.run_oslo_extraction)
        # button00.grid(row = 1, column = 1, sticky = "w", padx=5, pady=2)

        # section2 = tk.Label(master=self.dirframe, text = 'New Extraction Approach. Entering Information in the Info Page',font = controller.big_text_font)
        # section2.grid(row = 2, column = 0, sticky = "w", padx=5, pady=2)

        # label1 = tk.Label(master=self.timeframe, text = 'Extraction From (XXXXXXX)',font = controller.text_font)
        # label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        # SharedVariables.time_start = tk.StringVar()
        # entry1 = tk.Entry(master=self.timeframe,width = 10,textvariable = SharedVariables.time_start)
        # entry1.grid(row = 0,column = 1)

        # label2 = tk.Label(master=self.timeframe, text = 'Extraction To (XXXXXXX)',font = controller.text_font)
        # label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        # SharedVariables.time_end = tk.StringVar()
        # entry2 = tk.Entry(master=self.timeframe,width = 10,textvariable = SharedVariables.time_end)
        # entry2.grid(row = 0,column = 3)

        # explain0 = tk.Label(master=self.dirframe, text = 'GO TO EXTRACTION INFO PAGE', font = controller.text_font)
        # explain0.grid(row = 3, column = 0, sticky = "e", padx=5, pady=2)

        # button0 = tk.Button(master=self.dirframe, text = 'INFO PAGE', command=self.run_oslo_extraction)
        # button0.grid(row = 3, column = 1, sticky = "w", padx=5, pady=2)


        # SharedVariables.main_option = tk.StringVar()
        # extraction user interface
        explain1 = tk.Label(master=self.optionframe, text = '1. List of electrical files', font = controller.text_font)
        explain1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=2)

        button1 = tk.Button(master=self.optionframe, text = 'Excute 1', command=lambda: self.set_main_option("1","F01"))
        button1.grid(row = 0, column = 1, sticky = "w", padx=5, pady=2)

        explain2 = tk.Label(master=self.optionframe, text = '2: Snapshot', font = controller.text_font)
        explain2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=2)

        button2 = tk.Button(master=self.optionframe, text = 'Excute 2', command=lambda: self.set_main_option("2","F02"))
        button2.grid(row = 1, column = 1, sticky = "w", padx=5, pady=2)

        explain3 = tk.Label(master=self.optionframe, text = '3: Individual train step output', font = controller.text_font)
        explain3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=2)

        button3 = tk.Button(master=self.optionframe, text = 'Excute 3', command=lambda: self.set_main_option("3","F03"))
        button3.grid(row = 2, column = 1, sticky = "w", padx=5, pady=2)

        explain4 = tk.Label(master=self.optionframe, text = '4: Maximum currents and minimum and maximum voltages', font = controller.text_font)
        explain4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=2)

        button4 = tk.Button(master=self.optionframe, text = 'Excute 4', command=lambda: self.set_main_option("4","F04"))
        button4.grid(row = 3, column = 1, sticky = "w", padx=5, pady=2)

        explain5 = tk.Label(master=self.optionframe, text = '5: Train high voltage summary', font = controller.text_font)
        explain5.grid(row = 4, column = 0, sticky = "w", padx=5, pady=2)

        button5 = tk.Button(master=self.optionframe, text = 'Excute 5', command=lambda: self.set_main_option("5","F05"))
        button5.grid(row = 4, column = 1, sticky = "w", padx=5, pady=2)

        explain6 = tk.Label(master=self.optionframe, text = '6: Train low voltage summary', font = controller.text_font)
        explain6.grid(row = 5, column = 0, sticky = "w", padx=5, pady=2)

        button6 = tk.Button(master=self.optionframe, text = 'Excute 6', command=lambda: self.set_main_option("6","F06"))
        button6.grid(row = 5, column = 1, sticky = "w", padx=5, pady=2)

        explain7 = tk.Label(master=self.optionframe, text = '7: Average MW and MVAr demands in supply points, metering points, static VAr, etc', font = controller.text_font)
        explain7.grid(row = 6, column = 0, sticky = "w", padx=5, pady=2)

        button7 = tk.Button(master=self.optionframe, text = 'Excute 7', command=lambda: self.set_main_option("7","F07"))
        button7.grid(row = 6, column = 1, sticky = "w", padx=5, pady=2)

        explain8 = tk.Label(master=self.optionframe, text = '8: Feeder step output', font = controller.text_font)
        explain8.grid(row = 7, column = 0, sticky = "w", padx=5, pady=2)

        button8 = tk.Button(master=self.optionframe, text = 'Excute 8', command=lambda: self.set_main_option("8","F08"))
        button8.grid(row = 7, column = 1, sticky = "w", padx=5, pady=2)

        explain9 = tk.Label(master=self.optionframe, text = '9: Branch step output', font = controller.text_font)
        explain9.grid(row = 8, column = 0, sticky = "w", padx=5, pady=2)

        button9 = tk.Button(master=self.optionframe, text = 'Excute 9', command=lambda: self.set_main_option("9","F09"))
        button9.grid(row = 8, column = 1, sticky = "w", padx=5, pady=2)

        explain10 = tk.Label(master=self.optionframe, text = '10: Transformer step output', font = controller.text_font)
        explain10.grid(row = 9, column = 0, sticky = "w", padx=5, pady=2)

        button10 = tk.Button(master=self.optionframe, text = 'Excute 10', command=lambda: self.set_main_option("10","F10"))
        button10.grid(row = 9, column = 1, sticky = "w", padx=5, pady=2)

        explain11 = tk.Label(master=self.optionframe, text = '11: Smoothed feeder currents', font = controller.text_font)
        explain11.grid(row = 10, column = 0, sticky = "w", padx=5, pady=2)

        button11 = tk.Button(master=self.optionframe, text = 'Excute 11', command=lambda: self.set_main_option("11","F11"))
        button11.grid(row = 10, column = 1, sticky = "w", padx=5, pady=2)

        explain12 = tk.Label(master=self.optionframe, text = '12: Smoothed branch currents', font = controller.text_font)
        explain12.grid(row = 11, column = 0, sticky = "w", padx=5, pady=2)

        button12 = tk.Button(master=self.optionframe, text = 'Excute 12', command=lambda: self.set_main_option("12","F12"))
        button12.grid(row = 11, column = 1, sticky = "w", padx=5, pady=2)

        explain13 = tk.Label(master=self.optionframe, text = '13: Supply point persistent currents (development in progress)', font = controller.text_font)
        explain13.grid(row = 12, column = 0, sticky = "w", padx=5, pady=2)

        button13 = tk.Button(master=self.optionframe, text = 'Excute 13', command=lambda: self.set_main_option("13","F13"))
        button13.grid(row = 12, column = 1, sticky = "w", padx=5, pady=2)

        explain14 = tk.Label(master=self.optionframe, text = '14: Output to data files', font = controller.text_font)
        explain14.grid(row = 13, column = 0, sticky = "w", padx=5, pady=2)

        button14 = tk.Button(master=self.optionframe, text = 'Excute 14', command=lambda: self.set_main_option("14","F14"))
        button14.grid(row = 13, column = 1, sticky = "w", padx=5, pady=2)


        button = tk.Button(self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button.pack(pady = 5)

        # self.user_input_label = tk.Label(self, text="")
        # self.user_input_label.pack(side="top", fill="x", pady=10)

        # button1 = tk.Button(self, text="Oslo Extraction",
        #                    command=self.run_oslo_extraction)
        # button1.pack()
    
    # def update_user_input(self, user_input):
    #     self.user_input_label.config(text=f"User Input: {user_input}")
    #     self.user_input = user_input
    
    # def create_frame(self, fill=None, row_weights=None, column_weights=None):
    #     frame = tk.Frame(self)
    #     if fill:
    #         frame.pack(fill=fill)
    #     if row_weights:
    #         for i, weight in enumerate(row_weights):
    #             frame.rowconfigure(i, weight=weight)
    #     if column_weights:
    #         for i, weight in enumerate(column_weights):
    #             frame.columnconfigure(i, weight=weight)
    #     return frame
    
    # def get_entry_value(self):
    #     user_input = SharedVariables.sim_variable.get()
    #     print("User Input: ", user_input )
    #     #return user_input

    # def button_callback(self,target_page):
    #     self.get_entry_value()
    #     self.controller.show_frame(target_page)

    def set_main_option(self,value,target_page):
        SharedVariables.main_option = value
        self.controller.show_frame(target_page)
        # test = SharedVariables.main_option
        # print(test)


    def run_oslo_extraction(self):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            # self.update_user_input(sim_name)
            # Assuming oslo_extraction.main takes a parameter
            continue_process = oslo_extraction.main(sim_name)

            if not continue_process:
                # Do something if the process should not continue
                print("OSLO Extraction Terminated.")
            else:
                # Do something if the process should continue
                print("Continuing the process.")
        
        except Exception as e:
            print("Error in oslo_extraction.main:", e)

# OSLO Post Processing page
class PageFour(BasePage):

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        
        self.headframe = self.create_frame(fill=tk.BOTH)
        # self.timeframe = self.create_frame(fill=tk.BOTH, column_weights=(2, 1, 2, 1))
        self.dirframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1))
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), column_weights=(4, 1))
        self.infoframe = self.create_frame(fill=tk.BOTH)

        label = tk.Label(master=self.headframe, text = 'OSLO Post-Processing Option Selection',font = controller.sub_title_font)
        label.pack(side="top", fill="x", pady=2)

        note = tk.Label(master=self.headframe, text = 'Instruction: User can go to info page entering processing requirements using excute buttons below',font = controller.text_font)
        note.pack(side="left", fill="x", pady=5)

        explain1 = tk.Label(master=self.optionframe, text = '1. AC & DC: List OSLO Train Data', font = controller.text_font)
        explain1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=2)

        button1 = tk.Button(master=self.optionframe, text = 'Excute 1', command=lambda: self.set_main_option("1","P01"))
        button1.grid(row = 0, column = 1, sticky = "w", padx=5, pady=2)

        explain2 = tk.Label(master=self.optionframe, text = '2: AC & DC: Low Voltage Analysis Report', font = controller.text_font)
        explain2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=2)

        button2 = tk.Button(master=self.optionframe, text = 'Excute 2', command=lambda: self.set_main_option("2","P02"))
        button2.grid(row = 1, column = 1, sticky = "w", padx=5, pady=2)

        explain3 = tk.Label(master=self.optionframe, text = '3: AC: Average Power & Voltage Assessment (Minimum Requirement)', font = controller.text_font)
        explain3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=2)

        button3 = tk.Button(master=self.optionframe, text = 'Excute 3', command=lambda: self.set_main_option("3","P03"))
        button3.grid(row = 2, column = 1, sticky = "w", padx=5, pady=2)

        explain4 = tk.Label(master=self.optionframe, text = '4: AC: Meanuseful Processing (BSEN 50388:2022 Annex B)', font = controller.text_font)
        explain4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=2)

        button4 = tk.Button(master=self.optionframe, text = 'Excute 4', command=lambda: self.set_main_option("4","P04"))
        button4.grid(row = 3, column = 1, sticky = "w", padx=5, pady=2)

        explain5 = tk.Label(master=self.optionframe, text = '5: AC: Incoming Feeder Protection (Suggest use for IDMT Protection)', font = controller.text_font)
        explain5.grid(row = 4, column = 0, sticky = "w", padx=5, pady=2)

        button5 = tk.Button(master=self.optionframe, text = 'Excute 5', command=lambda: self.set_main_option("5","P05"))
        button5.grid(row = 4, column = 1, sticky = "w", padx=5, pady=2)

        explain6 = tk.Label(master=self.optionframe, text = '6: AC: New Supply Point Connection Assessment (Grid Code Compliance)', font = controller.text_font)
        explain6.grid(row = 5, column = 0, sticky = "w", padx=5, pady=2)

        button6 = tk.Button(master=self.optionframe, text = 'Excute 6', command=lambda: self.set_main_option("6","P06"))
        button6.grid(row = 5, column = 1, sticky = "w", padx=5, pady=2)

        explain7 = tk.Label(master=self.optionframe, text = '7: AC: OLE Current Rating Assessment', font = controller.text_font)
        explain7.grid(row = 6, column = 0, sticky = "w", padx=5, pady=2)

        button7 = tk.Button(master=self.optionframe, text = 'Excute 7', command=lambda: self.set_main_option("7","P07"))
        button7.grid(row = 6, column = 1, sticky = "w", padx=5, pady=2)

        explain8 = tk.Label(master=self.optionframe, text = '8: AC: Provision for Development', font = controller.text_font)
        explain8.grid(row = 7, column = 0, sticky = "w", padx=5, pady=2)

        button8 = tk.Button(master=self.optionframe, text = 'Excute 8', command=lambda: self.set_main_option("8","P08"))
        button8.grid(row = 7, column = 1, sticky = "w", padx=5, pady=2)

        explain9 = tk.Label(master=self.optionframe, text = '9: DC: (DATA PREP.) For Grid, TRU, Main CB, DC Busbar, Neg ETE, Bonding Assessment', font = controller.text_font)
        explain9.grid(row = 8, column = 0, sticky = "w", padx=5, pady=2)

        button9 = tk.Button(master=self.optionframe, text = 'Excute 9', command=lambda: self.set_main_option("9","P09"))
        button9.grid(row = 8, column = 1, sticky = "w", padx=5, pady=2)

        explain10 = tk.Label(master=self.optionframe, text = '10: DC (DATA PREP.): For Track CB, Pos ETE Assessment', font = controller.text_font)
        explain10.grid(row = 9, column = 0, sticky = "w", padx=5, pady=2)

        button10 = tk.Button(master=self.optionframe, text = 'Excute 10', command=lambda: self.set_main_option("10","P10"))
        button10.grid(row = 9, column = 1, sticky = "w", padx=5, pady=2)

        explain11 = tk.Label(master=self.optionframe, text = '11: DC (Assessment): Generate All Assessment Summary Reports', font = controller.text_font)
        explain11.grid(row = 10, column = 0, sticky = "w", padx=5, pady=2)

        button11 = tk.Button(master=self.optionframe, text = 'Excute 11', command=lambda: self.set_main_option("11","P11"))
        button11.grid(row = 10, column = 1, sticky = "w", padx=5, pady=2)

        explain12 = tk.Label(master=self.optionframe, text = '12: DC: Provision for Development 2', font = controller.text_font)
        explain12.grid(row = 11, column = 0, sticky = "w", padx=5, pady=2)

        button12 = tk.Button(master=self.optionframe, text = 'Excute 12', command=lambda: self.set_main_option("12","P12"))
        button12.grid(row = 11, column = 1, sticky = "w", padx=5, pady=2)

        # explain13 = tk.Label(master=self.optionframe, text = '13: Supply point persistent currents (development in progress)', font = controller.text_font)
        # explain13.grid(row = 12, column = 0, sticky = "w", padx=5, pady=2)

        # button13 = tk.Button(master=self.optionframe, text = 'Excute 13', command=lambda: self.set_main_option("13","F13"))
        # button13.grid(row = 12, column = 1, sticky = "w", padx=5, pady=2)

        # explain14 = tk.Label(master=self.optionframe, text = '14: Output to data files', font = controller.text_font)
        # explain14.grid(row = 13, column = 0, sticky = "w", padx=5, pady=2)

        # button14 = tk.Button(master=self.optionframe, text = 'Excute 14', command=lambda: self.set_main_option("14","F14"))
        # button14.grid(row = 13, column = 1, sticky = "w", padx=5, pady=2)


        button = tk.Button(self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button.pack(pady = 5)


    def set_main_option(self,value,target_page):
        SharedVariables.main_option = value
        self.controller.show_frame(target_page)
        # test = SharedVariables.main_option
        # print(test)