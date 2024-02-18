#

import tkinter as tk
import threading
# try:
#     from shared_contents import SharedVariables, Local_Shared
#     from base_frame import BasePage
#     import model_check
# except ModuleNotFoundError:
#     from vision_oslo_extension.shared_contents import SharedVariables, Local_Shared
#     from vision_oslo_extension.base_frame import BasePage
#     from vision_oslo_extension import model_check


# from shared_contents import SharedVariables, Local_Shared
# from base_frame import BasePage
# import model_check

from vision_oslo_extension.shared_contents import SharedVariables, Local_Shared
from vision_oslo_extension.base_frame import BasePage
from vision_oslo_extension import model_check

# Basic Information Summary
class C01(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "1"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 1: Basic Information Summary',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce various summary reports inlcuding branch list, supply point list, transformer list and errors or warnings summary. This process should be fairly quick.',aspect = 1200, font = controller.text_font)
        explain.pack()

        # option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        # choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: List all trains step output from the simulation', value="1", variable=option1)
        # choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        # choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: List all trains step output From Start to End (Time information below required)',value="2", variable=option1)
        # choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: List all trains step output of selected branches for the whole simulation window', value="3", variable=option1)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: List all trains step output of selected branches From Start to End (Time information below required)', value="4", variable=option1)
        # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        # label0 = tk.Label(master=self.inputframe, text = 'Option 2 and Option 3 requires Info Below',font = controller.text_font)
        # label0.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)
        
        # label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        # label1.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        # input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        # entry1.grid(row = 1,column = 1)

        # label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        # label2.grid(row = 1, column = 2, sticky = "w", padx=2, pady=2)

        # input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        # entry2.grid(row = 1,column = 3)

        # label3 = tk.Label(master=self.inputframe, text = 'Option 3 and Option 4 requires Info Below',font = controller.text_font)
        # label3.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        # label4 = tk.Label(master=self.inputframe, text = 'Customised Branch File Name',font = controller.text_font)
        # label4.grid(row = 3, column = 0, sticky = "w", padx=2, pady=2)

        # input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        # entry3.grid(row = 3,column = 1)

        # label5 = tk.Label(master=self.inputframe, text = '(Note: DO NOT include file suffix i.e. .txt)',font = controller.text_font)
        # label5.grid(row = 3, column = 2, sticky = "w", padx=2, pady=2)

        

        # text1 = tk.Label(master=self.nameframe, text = 'Simulation Name',font = controller.text_font)
        # text1.grid(row = 0, column = 0) # sticky n alight to top center part

        # label = tk.Label(self, text="This is Page One", font=controller.title_font)
        # label.pack(pady=10, padx=10)
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_model_check(),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageTwo"))
        button2.grid(row = 0, column = 1)


    def run_model_check(self):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming post_processing.main takes a parameter

            time_start = Local_Shared.time_start
            time_end = Local_Shared.time_end
            option_select = Local_Shared.option_select
            text_input = Local_Shared.text_input
            low_v = Local_Shared.low_threshold
            high_v = Local_Shared.high_threshold
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = model_check.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
            if not continue_process:
                # Do something if the process should not continue
                print('\033[1;31m') # color control warning message red
                print("ERROR: Process terminated unexpectly. Please Check Error History Above or Contact Support. You can continue use other options...")
                print('\033[1;0m') # color control warning message reset
            else:
                # Do something if the process should continue
                print('\033[1;32m') # color control warning message red
                print("Action Succesfully Completed. Check monitor history above and result files in your folder.")
                print('\033[1;0m') # color control warning message reset
        
        except Exception as e:
            print("Error in model_check.py:", e)

# Low Voltage Analysis Report
class C02(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "2"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 2: Connection Report',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce two tables. One showing the connection of all nodes. One showing all connected nodes from the supply points.',aspect = 1200, font = controller.text_font)
        explain.pack()

        # explain1 = tk.Label(master=self.headframe, text = 'NOTE: OPTION 2 and OPTION 3 IS UNDER DEVELOPMENT',font = controller.text_font)
        # explain1.pack()

        # option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        # choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Processing whole simulation', value="1", variable=option1)
        # choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        # choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Processing customised time window (Time information below required)',value="2", variable=option1)
        # choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Processing customised branches (Branch info below required)', value="3", variable=option1)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: List all trains step output of selected branches From Start to End (Time information below required)', value="4", variable=option1)
        # # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        # label3 = tk.Label(master=self.optionframe, text = 'VOLTAGE THRESHOLD IS REQUIRED FOR ALL OPTIONS',font = controller.text_font)
        # label3.grid(row = 3, column = 0, sticky = "w", padx=2, pady=2)
        
        # label6 = tk.Label(master=self.inputframe, text = 'Low Voltage Threshold (max 5 digit):',font = controller.text_font)
        # label6.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        # input4 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry4 = tk.Entry(master=self.inputframe,width = 10,textvariable = input4)
        # entry4.grid(row = 1,column = 1)

        # label7 = tk.Label(master=self.inputframe, text = 'Range [0 - 30000], Unit (V)',font = controller.text_font)
        # label7.grid(row = 1, column = 2, sticky = "w", padx=2, pady=2)

        # # label8 = tk.Label(master=self.inputframe, text = 'Unit (V)',font = controller.text_font)
        # # label8.grid(row = 1, column = 3, sticky = "w", padx=2, pady=2)

        # label1 = tk.Label(master=self.inputframe, text = 'Output From (Format: DHHMMSS)',font = controller.text_font)
        # label1.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        # input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        # entry1.grid(row = 2,column = 1)

        # label2 = tk.Label(master=self.inputframe, text = 'Output To (Format: DHHMMSS)',font = controller.text_font)
        # label2.grid(row = 2, column = 2, sticky = "w", padx=2, pady=2)

        # input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        # entry2.grid(row = 2,column = 3)

        # label4 = tk.Label(master=self.inputframe, text = 'Customised Branch File Name',font = controller.text_font)
        # label4.grid(row = 3, column = 0, sticky = "w", padx=2, pady=2)

        # input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        # entry3.grid(row = 3,column = 1)

        # label5 = tk.Label(master=self.inputframe, text = '(Note: DO NOT include file suffix i.e. .txt)',font = controller.text_font)
        # label5.grid(row = 3, column = 2, sticky = "w", padx=2, pady=2)

        

        # text1 = tk.Label(master=self.nameframe, text = 'Simulation Name',font = controller.text_font)
        # text1.grid(row = 0, column = 0) # sticky n alight to top center part

        # label = tk.Label(self, text="This is Page One", font=controller.title_font)
        # label.pack(pady=10, padx=10)
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_model_check(),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageTwo"))
        button2.grid(row = 0, column = 1)


    def run_model_check(self):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming post_processing.main takes a parameter
            time_start = Local_Shared.time_start
            #time_start = Local_Shared.time_start.get()
            time_end = Local_Shared.time_end
            option_select = Local_Shared.option_select
            text_input = Local_Shared.text_input
            low_v = Local_Shared.low_threshold
            high_v = Local_Shared.high_threshold
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = model_check.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
            if not continue_process:
                # Do something if the process should not continue
                print('\033[1;31m') # color control warning message red
                print("ERROR: Process terminated unexpectly. Please Check Error History Above or Contact Support. You can continue use other options...")
                print('\033[1;0m') # color control warning message reset
            else:
                # Do something if the process should continue
                print('\033[1;32m') # color control warning message red
                print("Action Succesfully Completed. Check monitor history above and result files in your folder.")
                print('\033[1;0m') # color control warning message reset
        
        except Exception as e:
            print("Error in model_check.py:", e)

# One stop AC power prepare
class C03(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "3"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 3: Prepare Data for OSLO Average Processor',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce various .d4 file and .mxn file as required for Average Power Assessment Spreadsheet. A text file "FeederList.txt" is required.',aspect = 1200, font = controller.text_font)
        explain.pack()

        # explain1 = tk.Label(master=self.headframe, text = 'NOTE: FeederList.txt is required before click RUN',font = controller.text_font)
        # explain1.pack()

        # # option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        # # choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: List all trains step output from the simulation', value="1", variable=option1)
        # # choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        # # choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: List all trains step output From Start to End (Time information below required)',value="2", variable=option1)
        # # choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        # # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: List all trains step output of selected branches for the whole simulation window', value="3", variable=option1)
        # # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: List all trains step output of selected branches From Start to End (Time information below required)', value="4", variable=option1)
        # # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        # # label0 = tk.Label(master=self.inputframe, text = 'Option 2 and Option 3 requires Info Below',font = controller.text_font)
        # # label0.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)
        
        # label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        # label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        # input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        # entry1.grid(row = 0,column = 1)

        # label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        # label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        # input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        # entry2.grid(row = 0,column = 3)

        # label3 = tk.Label(master=self.inputframe, text = 'Option 3 and Option 4 requires Info Below',font = controller.text_font)
        # label3.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        # label4 = tk.Label(master=self.inputframe, text = 'Customised Branch File Name',font = controller.text_font)
        # label4.grid(row = 3, column = 0, sticky = "w", padx=2, pady=2)

        # input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        # entry3.grid(row = 3,column = 1)

        # label5 = tk.Label(master=self.inputframe, text = '(Note: DO NOT include file suffix i.e. .txt)',font = controller.text_font)
        # label5.grid(row = 3, column = 2, sticky = "w", padx=2, pady=2)

        

        # text1 = tk.Label(master=self.nameframe, text = 'Simulation Name',font = controller.text_font)
        # text1.grid(row = 0, column = 0) # sticky n alight to top center part

        # label = tk.Label(self, text="This is Page One", font=controller.title_font)
        # label.pack(pady=10, padx=10)
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_model_check(),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageTwo"))
        button2.grid(row = 0, column = 1)


    def run_model_check(self):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming post_processing.main takes a parameter
            time_start = Local_Shared.time_start
            #time_start = Local_Shared.time_start.get()
            time_end = Local_Shared.time_end
            option_select = Local_Shared.option_select
            text_input = Local_Shared.text_input
            low_v = Local_Shared.low_threshold
            high_v = Local_Shared.high_threshold
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = model_check.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
            if not continue_process:
                # Do something if the process should not continue
                print('\033[1;31m') # color control warning message red
                print("ERROR: Process terminated unexpectly. Please Check Error History Above or Contact Support. You can continue use other options...")
                print('\033[1;0m') # color control warning message reset
            else:
                # Do something if the process should continue
                print('\033[1;32m') # color control warning message red
                print("Action Succesfully Completed. Check monitor history above and result files in your folder.")
                print('\033[1;0m') # color control warning message reset
        
        except Exception as e:
            print("Error in model_check.py:", e)

