#

import tkinter as tk
import threading
import os
# try:
#     from shared_contents import SharedVariables, Local_Shared
#     from base_frame import BasePage
#     import post_processing
#     import batch_processing
# except ModuleNotFoundError:
#     from vision_oslo_extension.shared_contents import SharedVariables, Local_Shared
#     from vision_oslo_extension.base_frame import BasePage
#     from vision_oslo_extension import post_processing
#     from vision_oslo_extension import batch_processing


# from shared_contents import SharedVariables, Local_Shared
# from base_frame import BasePage
# import post_processing
# import batch_processing

from vision_oslo_extension.shared_contents import SharedVariables, Local_Shared
from vision_oslo_extension.base_frame import BasePage
from vision_oslo_extension import post_processing, batch_processing,average_load,protection_if,grid_connection,ole_processing,dc_summary

# List OSLO Train Data
class P01(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "1"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 1: List OSLO Train Data',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce a step output of all OSLO trains within the simulation. User could copy and paste the information to a Excel --> data convert to table using space as seperator --> analysis and plot as required.',aspect = 1200, font = controller.text_font)
        explain.pack()

        explain0 = tk.Label(master=self.headframe, text = 'NOTE: OPTION 3 and 4 require a Branch List text file (User Defined Name Allowed)',font = controller.text_font)
        explain0.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: List all trains step output from the simulation', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: List all trains step output From Start to End (Time information below required)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: List all trains step output of selected branches for the whole simulation window', value="3", variable=option1)
        choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: List all trains step output of selected branches From Start to End (Time information below required)', value="4", variable=option1)
        choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        label0 = tk.Label(master=self.inputframe, text = 'Option 2 and Option 3 requires Info Below',font = controller.text_font)
        label0.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)
        
        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 1,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 1, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 1,column = 3)

        label3 = tk.Label(master=self.inputframe, text = 'Option 3 and Option 4 requires Info Below',font = controller.text_font)
        label3.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        label4 = tk.Label(master=self.inputframe, text = 'Customised Branch File Name',font = controller.text_font)
        label4.grid(row = 3, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 3,column = 1)

        label5 = tk.Label(master=self.inputframe, text = '(Note: DO NOT include file suffix i.e. .txt)',font = controller.text_font)
        label5.grid(row = 3, column = 2, sticky = "w", padx=2, pady=2)

        

        # text1 = tk.Label(master=self.nameframe, text = 'Simulation Name',font = controller.text_font)
        # text1.grid(row = 0, column = 0) # sticky n alight to top center part

        # label = tk.Label(self, text="This is Page One", font=controller.title_font)
        # label.pack(pady=10, padx=10)
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_post_processing(option1,input1,input2, input3),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_post_processing(self,option1,input1,input2,input3):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming post_processing.main takes a parameter

            time_start = input1.get()
            time_end = input2.get()
            option_select = option1.get()
            text_input = input3.get()
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
            continue_process = post_processing.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in post_processing.py:", e)

# Low Voltage Analysis Report
class P02(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "2"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 2: Low Voltage Analysis',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce three tables (csv files). Table list will cover all trains step output where the voltage is below the threshold. Summary table 1 will provide summary report group by trains. Summary table 2 will provide summary report group by branches.',aspect = 1200, font = controller.text_font)
        explain.pack()

        explain1 = tk.Label(master=self.headframe, text = 'NOTE: OPTION 2 and OPTION 3 IS UNDER DEVELOPMENT',font = controller.text_font)
        explain1.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Processing whole simulation', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Processing customised time window (Time information below required)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Processing customised branches (Branch info below required)', value="3", variable=option1)
        choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: List all trains step output of selected branches From Start to End (Time information below required)', value="4", variable=option1)
        # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        label3 = tk.Label(master=self.optionframe, text = 'VOLTAGE THRESHOLD IS REQUIRED FOR ALL OPTIONS',font = controller.text_font)
        label3.grid(row = 3, column = 0, sticky = "w", padx=2, pady=2)
        
        label6 = tk.Label(master=self.inputframe, text = 'Low Voltage Threshold (max 5 digit):',font = controller.text_font)
        label6.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input4 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry4 = tk.Entry(master=self.inputframe,width = 10,textvariable = input4)
        entry4.grid(row = 1,column = 1)

        label7 = tk.Label(master=self.inputframe, text = 'Range [0 - 30000], Unit (V)',font = controller.text_font)
        label7.grid(row = 1, column = 2, sticky = "w", padx=2, pady=2)

        # label8 = tk.Label(master=self.inputframe, text = 'Unit (V)',font = controller.text_font)
        # label8.grid(row = 1, column = 3, sticky = "w", padx=2, pady=2)

        label1 = tk.Label(master=self.inputframe, text = 'Output From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 2,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Output To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 2, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 2,column = 3)

        label4 = tk.Label(master=self.inputframe, text = 'Customised Branch File Name',font = controller.text_font)
        label4.grid(row = 3, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 3,column = 1)

        label5 = tk.Label(master=self.inputframe, text = '(Note: DO NOT include file suffix i.e. .txt)',font = controller.text_font)
        label5.grid(row = 3, column = 2, sticky = "w", padx=2, pady=2)

        

        # text1 = tk.Label(master=self.nameframe, text = 'Simulation Name',font = controller.text_font)
        # text1.grid(row = 0, column = 0) # sticky n alight to top center part

        # label = tk.Label(self, text="This is Page One", font=controller.title_font)
        # label.pack(pady=10, padx=10)
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_post_processing(option1,input1,input2,input3,input4),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_post_processing(self,option1,input1,input2,input3,input4):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming post_processing.main takes a parameter
            time_start = input1.get()
            #time_start = Local_Shared.time_start.get()
            time_end = input2.get()
            option_select = option1.get()
            text_input = input3.get()
            low_v = input4.get()
            high_v = Local_Shared.high_threshold
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = post_processing.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in post_processing.py:", e)

# One stop AC power prepare
class P03(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "3"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 3: AC - Supply Points Load Analysis - Average Power',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This function requires the excel spreadsheet with proper pre-defined information. See manual for detailed requirements',aspect = 1200, font = controller.text_font)
        explain.pack()

        explain1 = tk.Label(master=self.headframe, text = 'NOTE: Excel spreadsheet in .xlsx format is required before click RUN',font = controller.text_font)
        explain1.pack()
        explain2 = tk.Label(master=self.headframe, text = 'NOTE: Import "Excel - For Average Power" if needed ',font = controller.text_font)
        explain2.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Full Auto Process. (Require .oof + .lst.txt files.)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Auto process with user defined node configuration. (Only require .oof file)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Update spreadsheet only. (Require all .d4 files and .mxn files)', value="3", variable=option1)
        choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: Extract d4 files and mxn file only. (Only require .oof file)', value="4", variable=option1)
        choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        label01 = tk.Label(master=self.inputframe, text = 'Excel Name:',font = controller.text_font)
        label01.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry01 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry01.grid(row = 0,column = 1)

        label02 = tk.Label(master=self.inputframe, text = '(No suffix)',font = controller.text_font)
        label02.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        label02 = tk.Label(master=self.inputframe, text = 'Below required for Option 1,2,4',font = controller.text_font)
        label02.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)
        
        
        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 2,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 2, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 2,column = 3)

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
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_batch_processing(option1,input1,input2,input3),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_batch_processing(self,option1,input1,input2,input3):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)

            time_start = input1.get()
            time_end = input2.get()
            option_select = option1.get()
            text_input = input3.get()
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
            continue_process = average_load.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in average_load.py:", e)

# Umean useful Analysis
class P04(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "4"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 2: Umeanuseful',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce a text file stating the Umean useful (ZONE) for the selected geographical section and list of Umeanuseful (TRAIN) in ascending order. User needs to make sensible choice of Trains for the assessment.',aspect = 1200, font = controller.text_font)
        explain.pack()

        # explain1 = tk.Label(master=self.headframe, text = 'NOTE: OPTION 2 and OPTION 3 IS UNDER DEVELOPMENT',font = controller.text_font)
        # explain1.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Processing whole time window (Suggest for Umean (TRAIN))', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Processing customised time window (Suggest for Umean (Zone))',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Processing customised branches (Branch info below required)', value="3", variable=option1)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: List all trains step output of selected branches From Start to End (Time information below required)', value="4", variable=option1)
        # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        explain1 = tk.Label(master=self.optionframe, text = 'NOTE: Branch List File should define the assessed geographic range.',font = controller.text_font)
        explain1.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)
        

        label4 = tk.Label(master=self.inputframe, text = 'Branch File Name (Required):',font = controller.text_font)
        label4.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 0,column = 1)

        label5 = tk.Label(master=self.inputframe, text = '(Note: DO NOT include file suffix i.e. .txt)',font = controller.text_font)
        label5.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        label1 = tk.Label(master=self.inputframe, text = 'Peak time From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 1,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Peak time To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 1, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 1,column = 3)

        # text1 = tk.Label(master=self.nameframe, text = 'Simulation Name',font = controller.text_font)
        # text1.grid(row = 0, column = 0) # sticky n alight to top center part

        # label = tk.Label(self, text="This is Page One", font=controller.title_font)
        # label.pack(pady=10, padx=10)
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_post_processing(option1,input1,input2,input3),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_post_processing(self,option1,input1,input2,input3):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming post_processing.main takes a parameter
            time_start = input1.get()
            #time_start = Local_Shared.time_start.get()
            time_end = input2.get()
            option_select = option1.get()
            text_input = input3.get()
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
            continue_process = post_processing.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in post_processing.py:", e)

# Incoming Feeder Protection
class P05(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "5"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 5: AC - Incoming Feeder Protection',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This function is used to carry out prelimiary assessment on incoming feeder protection based on relay type (DT or IDMT). This function requires the excel spreadsheet with proper pre-defined information. See manual for detailed requirements',aspect = 1200, font = controller.text_font)
        explain.pack()

        explain1 = tk.Label(master=self.headframe, text = 'NOTE: Excel spreadsheet in .xlsx format is required before click RUN',font = controller.text_font)
        explain1.pack()
        
        explain2 = tk.Label(master=self.headframe, text = 'NOTE: Import "Excel - For IF Protection" if needed ',font = controller.text_font)
        explain2.pack()


        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Full Auto Process. (Require .oof files)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Update Spreadsheet only. (Require all .d4 files)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Update spreadsheet only. (Require all .d4 files and .mxn files)', value="3", variable=option1)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: Extract d4 files and mxn file only. (Only require .oof file)', value="4", variable=option1)
        # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        label01 = tk.Label(master=self.inputframe, text = 'Excel Name:',font = controller.text_font)
        label01.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry01 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry01.grid(row = 0,column = 1)

        label02 = tk.Label(master=self.inputframe, text = '(No suffix)',font = controller.text_font)
        label02.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        label02 = tk.Label(master=self.inputframe, text = 'Below required for Option 1',font = controller.text_font)
        label02.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)
        
        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 2,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 2, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 2,column = 3)

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
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_batch_processing(option1,input1,input2,input3),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_batch_processing(self,option1,input1,input2,input3):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)

            time_start = input1.get()
            time_end = input2.get()
            option_select = option1.get()
            text_input = input3.get()
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
            continue_process = protection_if.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in protection_if.py:", e)

# New Grid Connection Assessment
class P06(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "6"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 6: AC - New Supply Point Connection Assessment',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This function is used to carry out new supply point assessment as required by Grid Code. This function requires the excel spreadsheet with proper pre-defined information. See manual for detailed requirements',aspect = 1200, font = controller.text_font)
        explain.pack()

        explain1 = tk.Label(master=self.headframe, text = 'NOTE: Excel spreadsheet in .xlsx format is required before click RUN',font = controller.text_font)
        explain1.pack()
        
        explain2 = tk.Label(master=self.headframe, text = 'NOTE: Import "Excel - For New SP Connect" if needed ',font = controller.text_font)
        explain2.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Full Auto Process. (Require .oof files)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Update Spreadsheet only. (Require extracted .d4 files)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Update spreadsheet only. (Require all .d4 files and .mxn files)', value="3", variable=option1)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: Extract d4 files and mxn file only. (Only require .oof file)', value="4", variable=option1)
        # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        label01 = tk.Label(master=self.inputframe, text = 'Excel Name:',font = controller.text_font)
        label01.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry01 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry01.grid(row = 0,column = 1)

        label02 = tk.Label(master=self.inputframe, text = '(No suffix)',font = controller.text_font)
        label02.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        label02 = tk.Label(master=self.inputframe, text = 'Below required for Option 1',font = controller.text_font)
        label02.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)
        
        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 2,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 2, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 2,column = 3)

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
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_batch_processing(option1,input1,input2,input3),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_batch_processing(self,option1,input1,input2,input3):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            time_start = input1.get()
            time_end = input2.get()
            option_select = option1.get()
            text_input = input3.get()
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
            continue_process = grid_connection.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in grid_connection.py:", e)

# OLE Rating Assessment
class P07(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "7"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 6: AC - OLE Current Rating Assessment',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This function is used to carry out OLE current rating assessment. This function requires the excel spreadsheet with proper pre-defined information. See manual for detailed requirements',aspect = 1200, font = controller.text_font)
        explain.pack()

        explain1 = tk.Label(master=self.headframe, text = 'NOTE: Excel spreadsheet in .xlsx format is required before click RUN',font = controller.text_font)
        explain1.pack()
        
        explain2 = tk.Label(master=self.headframe, text = 'NOTE: Import "Excel - For OLE Rating" if needed ',font = controller.text_font)
        explain2.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Full Auto Process. (Require .oof files)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Update Spreadsheet only. (Require extracted .d4 files)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Update spreadsheet only. (Require all .d4 files and .mxn files)', value="3", variable=option1)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: Extract d4 files and mxn file only. (Only require .oof file)', value="4", variable=option1)
        # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        label01 = tk.Label(master=self.inputframe, text = 'Excel Name:',font = controller.text_font)
        label01.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry01 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry01.grid(row = 0,column = 1)

        label02 = tk.Label(master=self.inputframe, text = '(No suffix)',font = controller.text_font)
        label02.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        label02 = tk.Label(master=self.inputframe, text = 'Below required for Option 1',font = controller.text_font)
        label02.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)
        
        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 2,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 2, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 2,column = 3)

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
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_batch_processing(option1,input1,input2,input3),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_batch_processing(self,option1,input1,input2,input3):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            time_start = input1.get()
            time_end = input2.get()
            option_select = option1.get()
            text_input = input3.get()
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
            continue_process = ole_processing.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in ole_processing.py:", e)

# To be Developed
class P08(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "8"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 8: TO BE DEVELOPED',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'TO BE DEVELOPED', font = controller.text_font)
        explain.pack()

        #button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_post_processing(),width = 20, height =2)
        button = tk.Button(master=self.excuteframe, text="RUN!", command=lambda: controller.show_frame("PageFour"),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)

# Substation TRU assessment
class P09(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "9"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 9: Substation TRU Assessment Data Prepare',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce multiple .d4 files from extraction and .csv files for each substation. A substation list named as "FeederList.txt" is required.',aspect = 1200, font = controller.text_font)
        explain.pack()

        explain1 = tk.Label(master=self.headframe, text = 'NOTE: "FeederList.txt" is required before click RUN',font = controller.text_font)
        explain1.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Substation RMS current (1,4,5,30,60,120,180 min) and average power (30 min)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Grid Calculation (require "GridAllocation.csv" file)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: List all trains step output of selected branches for the whole simulation window', value="3", variable=option1)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        # choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: List all trains step output of selected branches From Start to End (Time information below required)', value="4", variable=option1)
        # choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        label0 = tk.Label(master=self.inputframe, text = 'Enter Assessment Time Window',font = controller.text_font)
        label0.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)
        
        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 1,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 1, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 1,column = 3)

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
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_batch_processing(option1,input1,input2),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_batch_processing(self,option1,input1,input2):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)

            time_start = input1.get()
            time_end = input2.get()
            option_select = option1.get()
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
            continue_process = batch_processing.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in batch_processing.py:", e)

# Substation Branch Process
class P10(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "10"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 10: Substation Protection/Track CB & ETE Assessment Data Prepare',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce multiple .csv files depending on the option selection. This is used to assess XXXXXXXXXXXXX',aspect = 1200, font = controller.text_font)
        explain.pack()

        explain1 = tk.Label(master=self.headframe, text = 'NOTE: Time Window is COMPULSORY. Option 4-6 is UNDER DEVELOPMENT.',font = controller.text_font)
        explain1.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: All branches (Auto) step output summary', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: All branches (Auto) rolling RMS current calculation',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: All branches (Auto) maximum rolling RMS current summary', value="3", variable=option1)
        choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: Customised branches step output summary ("BranchNodeList.txt"is required)', value="4", variable=option1)
        choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        choice5 = tk.Radiobutton(master=self.optionframe, text = 'Option 5: Customised branches rolling RMS current calculation ("BranchNodeList.txt"is required)', value="5", variable=option1)
        choice5.grid(row = 4, column = 0, sticky = "w", padx=5, pady=5)

        choice6 = tk.Radiobutton(master=self.optionframe, text = 'Option 6: Customised branches maximum rolling RMS current summary ("BranchNodeList.txt"is required)', value="6", variable=option1)
        choice6.grid(row = 5, column = 0, sticky = "w", padx=5, pady=5)



        label0 = tk.Label(master=self.inputframe, text = 'Enter Assessment Time Window',font = controller.text_font)
        label0.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)
        
        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 1,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 1, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 1,column = 3)

        label3 = tk.Label(master=self.inputframe, text = 'Time Seconds (0 - 86400):',font = controller.text_font)
        label3.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 2,column = 1)

        label4 = tk.Label(master=self.inputframe, text = '(Note this is time in seconds)',font = controller.text_font)
        label4.grid(row = 2, column = 2, sticky = "w", padx=2, pady=2)

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
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_batch_processing(option1,input1,input2,input3),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_batch_processing(self,option1,input1,input2,input3):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)

            time_start = input1.get()
            time_end = input2.get()
            option_select = option1.get()
            text_input = Local_Shared.text_input
            low_v = Local_Shared.low_threshold
            high_v = Local_Shared.high_threshold
            time_step = input3.get()

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = batch_processing.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in batch_processing.py:", e)

# Substation DC Summary
class P11(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "11"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 11: DC Substation Assessment Summary',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce assessment summary against ratings for all scenarios. User is expected to set some presettings in a spreadsheet. A setting excel required.',aspect = 1200, font = controller.text_font)
        explain.pack()

        explain1 = tk.Label(master=self.headframe, text = 'NOTE: Excel spreadsheet in .xlsx format is required before click RUN.',font = controller.text_font)
        explain1.pack()

        explain2 = tk.Label(master=self.headframe, text = 'NOTE: Import proper excel as required Below if needed.',font = controller.text_font)
        explain2.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: TRU Summary - [Import: Excel - For TRU Summary if needed]', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Main DC Circuit Breaker Summary - [Import: Excel - For Main DCCB Summary if needed]',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: DC Busbar Summary - [Import: Excel - For DCBB Summary if needed]',value="3", variable=option1)
        choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        choice4 = tk.Radiobutton(master=self.optionframe, text = 'Option 4: Negative ETE Summary - [Import: Excel - For Neg ETE Summary if needed]',value="4", variable=option1)
        choice4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)

        choice5 = tk.Radiobutton(master=self.optionframe, text = 'Option 5: Impedance Bond Summary - [Import: Excel - For Imp Bond Summary if needed]',value="5", variable=option1)
        choice5.grid(row = 4, column = 0, sticky = "w", padx=5, pady=5)


        label01 = tk.Label(master=self.inputframe, text = 'Excel Name:',font = controller.text_font)
        label01.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry01 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry01.grid(row = 0,column = 1)

        label02 = tk.Label(master=self.inputframe, text = '(No suffix)',font = controller.text_font)
        label02.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        # label02 = tk.Label(master=self.inputframe, text = 'Below required for Option 1',font = controller.text_font)
        # label02.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)
        
        # label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        # label1.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        # input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        # entry1.grid(row = 2,column = 1)

        # label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        # label2.grid(row = 2, column = 2, sticky = "w", padx=2, pady=2)

        # input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        # entry2.grid(row = 2,column = 3)

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
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_batch_processing(option1,input3),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_batch_processing(self,option1,input3):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)

            time_start = Local_Shared.time_start
            time_end = Local_Shared.time_end
            option_select = option1.get()
            text_input = input3.get()
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
            continue_process = dc_summary.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in batch_processing.py:", e)

# To be Developed
class P12(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "12"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 1: TO BE DEVELOPED',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'TO BE DEVELOPED', font = controller.text_font)
        explain.pack()

        #button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_post_processing(),width = 20, height =2)
        button = tk.Button(master=self.excuteframe, text="RUN!", command=lambda: controller.show_frame("PageFour"),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)

# output to data files
class F14(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "14"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 14: Output to Data Files',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'Directs seveval outputs plus train summary output', font = controller.text_font)
        explain.pack()

        #button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_post_processing(),width = 20, height =2)
        button = tk.Button(master=self.excuteframe, text="RUN!", command=lambda: controller.show_frame("PageFour"),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Processing", command=lambda: controller.show_frame("PageFour"))
        button2.grid(row = 0, column = 1)


    def run_post_processing(self):
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

            continue_process = post_processing.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)

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
            print("Error in post_processing.main:", e)


