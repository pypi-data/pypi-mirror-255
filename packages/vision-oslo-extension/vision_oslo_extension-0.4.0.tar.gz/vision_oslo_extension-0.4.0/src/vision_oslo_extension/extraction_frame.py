#


import tkinter as tk
import threading

# try:
#     from shared_contents import SharedVariables, Local_Shared
#     from base_frame import BasePage
#     import oslo_extraction
# except ModuleNotFoundError:
#     from vision_oslo_extension.shared_contents import SharedVariables, Local_Shared
#     from vision_oslo_extension.base_frame import BasePage
#     from vision_oslo_extension import oslo_extraction


# from shared_contents import SharedVariables, Local_Shared
# from base_frame import BasePage
# import oslo_extraction

from vision_oslo_extension.shared_contents import SharedVariables, Local_Shared
from vision_oslo_extension.base_frame import BasePage
from vision_oslo_extension import oslo_extraction

# class F00(BasePage):
#     def __init__(self, parent, controller):
#         super().__init__(parent, controller)
#         SharedVariables.main_option = "0"
#         Local_Shared.time_start = tk.StringVar(value = "0")
#         Local_Shared.time_end = tk.StringVar(value = "0")
#         Local_Shared.text_input = tk.StringVar(value = "0")
#         Local_Shared.low_threshold = tk.StringVar(value = "0")
#         Local_Shared.high_threshold = tk.StringVar(value = "0")
#         Local_Shared.time_step = tk.StringVar(value = "0")

# List of Input Files
class F01(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "1"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 1: Listing of Electrical File',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'The contents of the electrical output file will be produced, starting with the network data used by the simulation programme, and followed by the data written at each time step during the requested period.',aspect = 1200, font = controller.text_font)
        explain.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: List Input File (all time window)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: List Input File From Start to End (Time information below required)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: List Input File Headers Only', value="3", variable=option1)
        choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 0,column = 3)

        

        # text1 = tk.Label(master=self.nameframe, text = 'Simulation Name',font = controller.text_font)
        # text1.grid(row = 0, column = 0) # sticky n alight to top center part

        # label = tk.Label(self, text="This is Page One", font=controller.title_font)
        # label.pack(pady=10, padx=10)
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(option1,input1,input2),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,option1,input1,input2):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming oslo_extraction.main takes a parameter
            
            # if Local_Shared.time_start is not None: time_start = Local_Shared.time_start.get()
            # if Local_Shared.time_end is not None: time_end = Local_Shared.time_end.get()
            # if Local_Shared.option_select is not None: option_select = Local_Shared.option_select.get()
            # if Local_Shared.text_input is not None: text_input = Local_Shared.text_input.get()
            # if Local_Shared.low_threshold is not None: low_v = Local_Shared.low_threshold.get()
            # if Local_Shared.high_threshold is not None: high_v = Local_Shared.high_threshold.get()
            # if Local_Shared.time_step is not None: time_step = Local_Shared.time_step.get()

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
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# Snapshot
class F02(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "2"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 2: Snapshot',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'This will produce two tables of train and electrical overhead quantities related to the time requested.', font = controller.text_font)
        explain.pack()

        label1 = tk.Label(master=self.inputframe, text = 'Extraction at (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry1.grid(row = 0,column = 1)

        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(input2),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,input_temp):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming oslo_extraction.main takes a parameter
            time_start = input_temp.get()
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
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# Individual train step output
class F03(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "3"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights = (1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 3: Individual Train Step Output',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'This will produce train number specified at each clock increment within the time band requested.', font = controller.text_font)
        explain.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Single Train Step Output (Enter training number below)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Multiple Train Step Output (A text file named as ""TrainList.txt"" is required"',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)
        # Option 3 to be considered if needed in the future
        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Extract the List in the Train List ', value="3", variable=Local_Shared.option_select)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 0,column = 3)

        label3 = tk.Label(master=self.inputframe, text = 'VISION Train Number (Maximum 5 digit)',font = controller.text_font)
        label3.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 1,column = 1)

        
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(option1,input1,input2,input3),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,option1,input1,input2,input3):
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
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# min max values
class F04(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "4"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 4: Maximum Currents and Minimum and Maximum Voltages',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'This will produce the tables of min/max values for each node, supply points, branch and transformers.', font = controller.text_font)
        explain.pack()

        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming oslo_extraction.main takes a parameter

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
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# train high voltage summary
class F05(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "5"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 5: Train High Voltage Summary',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'This will aggregate the length of time for which train s votlage is above the requested threshold.', font = controller.text_font)
        explain.pack()

        label1 = tk.Label(master=self.inputframe, text = 'High Voltage Threshold (Format: XX.X)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Unit (kV)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(input2),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,input_temp):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming oslo_extraction.main takes a parameter

            time_start = Local_Shared.time_start
            time_end = Local_Shared.time_end
            option_select = Local_Shared.option_select
            text_input = Local_Shared.text_input
            low_v = Local_Shared.low_threshold
            high_v = input_temp.get()
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# train low votlage summary
class F06(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "6"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 6: Train Low Voltage Summary',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'This will aggregate the length of time for which train s votlage is below the requested threshold.', font = controller.text_font)
        explain.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Summary only (lst file output with additional info)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Detailed Info (including snapshot of all low voltage time steps)',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        label1 = tk.Label(master=self.inputframe, text = 'Low Voltage Threshold (Format: XX.X)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Unit (kV)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(option1, input2),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,option_temp,input_temp):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming oslo_extraction.main takes a parameter

            time_start = Local_Shared.time_start
            time_end = Local_Shared.time_end
            option_select = option_temp.get()
            text_input = Local_Shared.text_input
            low_v = input_temp.get()
            high_v = Local_Shared.high_threshold
            time_step = Local_Shared.time_step

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# average power
class F07(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "7"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights = (1, 1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 7: Average MW and MVAr Demands',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'Averages of MW and MVAr demand are calculated over succesive intervals of time for the requested supply points, metering points, static VAR compensators and motor alternators requested. Averages are NOT rolling average.', aspect = 1200, font = controller.text_font)
        explain.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Single Demands Output (Enter required info below)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Multiple Demands Output (A text file named as ""FeederList.txt"" is required"',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)
        # Option 3 to be considered if needed in the future
        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Extract the List in the Train List ', value="3", variable=Local_Shared.option_select)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 0,column = 3)

        label3 = tk.Label(master=self.inputframe, text = 'Averaged Time Windows (Formax: XX)',font = controller.text_font)
        label3.grid(row = 2, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 2,column = 1)

        label4 = tk.Label(master=self.inputframe, text = 'Unit (minute)   (2 digits ONLY)',font = controller.text_font)
        label4.grid(row = 2, column = 2, sticky = "w", padx=2, pady=2)

        label5 = tk.Label(master=self.inputframe, text = 'MOVING AVERAGE!',font = controller.text_font)
        label5.grid(row = 2, column = 3, sticky = "w", padx=2, pady=2)

        label6 = tk.Label(master=self.inputframe, text = 'Demand ID (Maximum 4 digit):',font = controller.text_font)
        label6.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input4 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry4 = tk.Entry(master=self.inputframe,width = 10,textvariable = input4)
        entry4.grid(row = 1,column = 1)

        
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(option1,input1,input2,input3,input4),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,option1,input1,input2,input3,input4):
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
            time_step = input4.get()

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# Feeder step output
class F08(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "8"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights = (1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 8: Individual Feeder Step Output',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce a table of votlages and currents (magnitude and phase) together with real and reactive power for the supply points, metering points, static VAR compensators and motor alternators requested for the specified time period', aspect = 1200, font = controller.text_font)
        explain.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Single Feeder Step Output (Enter Feeder ID below)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Multiple Feeder Step Output (A text file named as ""FeederList.txt"" is required"',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)
        # Option 3 to be considered if needed in the future
        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Extract the List in the Train List ', value="3", variable=Local_Shared.option_select)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 0,column = 3)

        label3 = tk.Label(master=self.inputframe, text = 'OSLO Feeder Name (Maximum 4 digit):',font = controller.text_font)
        label3.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 1,column = 1)

        
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(option1,input1,input2,input3),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,option1,input1,input2,input3):
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
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# branch step output
class F09(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "9"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights = (1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 9: Individual Branch Step Output',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce tables of voltage, current, real power, reactive power and displacement factor at the start or the end of the branch(es) requested for the specified time period ', aspect = 1200, font = controller.text_font)
        explain.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Single Branch Step Output (Enter Branch ID + Terminal below)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Multiple Branch Step Output (A text file named as ""BranchNodeList.txt"" is required"',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)
        # Option 3 to be considered if needed in the future
        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Extract the List in the Train List ', value="3", variable=Local_Shared.option_select)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        explain1 = tk.Message(master=self.optionframe, text = 'Input format below should be "Branch ID/S or E". Note that S or E must be capital letters. S means branch start and E means branch end. Empty output or Errors are usually due to the wrong naming format', aspect = 1200, font = controller.text_font)
        explain1.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 0,column = 3)

        label3 = tk.Label(master=self.inputframe, text = 'OSLO Branch Name (Data Format: XXXX/X):',font = controller.text_font)
        label3.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 1,column = 1)

        
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(option1,input1,input2,input3),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,option1,input1,input2,input3):
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
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# trans step output
class F10(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "10"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights = (1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 10: Individual Transformer Step Output',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce tables showing step-by-step values of real power, reactive power, votlage and current will be produced for the specified time period. This will show all windings depending on the transformer type.', aspect = 1200, font = controller.text_font)
        explain.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Single Transformer Step Output (Enter Transformer ID below)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Multiple Transformer Step Output (A text file named as ""TransformerList.txt"" is required"',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)
        # Option 3 to be considered if needed in the future
        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Extract the List in the Train List ', value="3", variable=Local_Shared.option_select)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        label1 = tk.Label(master=self.inputframe, text = 'Extraction From (Format: DHHMMSS)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = 'Extraction To (Format: DHHMMSS)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        entry2.grid(row = 0,column = 3)

        label3 = tk.Label(master=self.inputframe, text = 'OSLO Transformer Name (Maximum 4 digit):',font = controller.text_font)
        label3.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 1,column = 1)

        
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(option1,input1,input2,input3),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,option1,input1,input2,input3):
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
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# smoothed feeder current
class F11(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "11"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights = (1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 11: Smoothed Feeder Currents',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'At every time step, rolling average currents are calculated over specified time step for the specified supply points, metering point, static VAR compentsator and motor alternators. Only current in the "normal" direction of power flow are taken into account. A seperate file is created for the reverse direction of power flow.', aspect = 1200, font = controller.text_font)
        explain.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Single Feeder Currents Output (Enter Feeder ID below)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Multiple Feeder Currents Output (A text file named as ""FeederList.txt"" is required"',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)
        # Option 3 to be considered if needed in the future
        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Extract the List in the Train List ', value="3", variable=Local_Shared.option_select)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        label1 = tk.Label(master=self.inputframe, text = 'Time Steps (Maixmum 3 digits)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = '(Note this is time STEP based on simulation setting)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        # input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        # entry2.grid(row = 0,column = 3)

        label3 = tk.Label(master=self.inputframe, text = 'OSLO Feeder Name (Maximum 4 digit):',font = controller.text_font)
        label3.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 1,column = 1)

        
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(option1,input1,input3),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,option1,input1,input3):
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
            time_step = input1.get()

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# smoothed branch current
class F12(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "12"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, row_weights = (1, 1), column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 12: Smoothed Branch Currents',font = controller.sub_title_font)
        head.pack()

        explain = tk.Message(master=self.headframe, text = 'This will produce a table of maximum rolling branch currents (average and RMS) for the specified branch(es), together with the time-period over which the maximum occurred.', aspect = 1200, font = controller.text_font)
        explain.pack()

        option1 = tk.StringVar(value = "0") # Initialize with a value not used by the radio buttons
        choice1 = tk.Radiobutton(master=self.optionframe, text = 'Option 1: Single Branch Currents Output (Enter Branch ID + Terminal below)', value="1", variable=option1)
        choice1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        choice2 = tk.Radiobutton(master=self.optionframe, text = 'Option 2: Multiple Branch Currents Output (A text file named as ""BranchNodeList.txt"" is required"',value="2", variable=option1)
        choice2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)
        # Option 3 to be considered if needed in the future
        # choice3 = tk.Radiobutton(master=self.optionframe, text = 'Option 3: Extract the List in the Train List ', value="3", variable=Local_Shared.option_select)
        # choice3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        explain1 = tk.Message(master=self.optionframe, text = 'Input format below should be "Branch ID/S or E". Note that S or E must be capital letters. S means branch start and E means branch end. Empty output or Errors are usually due to the wrong naming format', aspect = 1200, font = controller.text_font)
        explain1.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)

        label1 = tk.Label(master=self.inputframe, text = 'Time Steps (Maixmum 3 digits)',font = controller.text_font)
        label1.grid(row = 0, column = 0, sticky = "w", padx=2, pady=2)

        input1 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry1 = tk.Entry(master=self.inputframe,width = 10,textvariable = input1)
        entry1.grid(row = 0,column = 1)

        label2 = tk.Label(master=self.inputframe, text = '(Note this is time STEP based on simulation setting)',font = controller.text_font)
        label2.grid(row = 0, column = 2, sticky = "w", padx=2, pady=2)

        # input2 = tk.StringVar() # Initialize with a value not used by the radio buttons
        # entry2 = tk.Entry(master=self.inputframe,width = 10,textvariable = input2)
        # entry2.grid(row = 0,column = 3)

        label3 = tk.Label(master=self.inputframe, text = 'OSLO Branch Name (Format: XXXX/X):',font = controller.text_font)
        label3.grid(row = 1, column = 0, sticky = "w", padx=2, pady=2)

        input3 = tk.StringVar() # Initialize with a value not used by the radio buttons
        entry3 = tk.Entry(master=self.inputframe,width = 10,textvariable = input3)
        entry3.grid(row = 1,column = 1)

        
        button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(option1,input1,input3),width = 20, height =2)
        button.pack()

        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self,option1,input1,input3):
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
            time_step = input1.get()

            # Run the batch processing function in a separate thread
            thread = threading.Thread(target=self.run_excution_in_thread, args=(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step))
            thread.start()
        
        except Exception as e:
            print("Error in threading...Contact Support / Do not carry out multiple tasking at the same time. ", e)
    
    def run_excution_in_thread(self, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        try:    
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

# supply point persistent current
class F13(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        SharedVariables.main_option = "13"

        self.headframe = self.create_frame(fill=tk.BOTH)
        
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1))
        self.inputframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1, 1, 1))

        self.excuteframe = self.create_frame(fill=tk.BOTH)

        self.infoframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 1))

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Page 13: Supply Point Persistent Currents (Under Development)',font = controller.sub_title_font)
        head.pack()

        explain = tk.Label(master=self.headframe, text = 'DEVELOPMENT IN PROCESS. (NOT SURE IF USEFUL OR NOT)', font = controller.text_font)
        explain.pack()

        #button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(),width = 20, height =2)
        button = tk.Button(master=self.excuteframe, text="RUN!", command=lambda: controller.show_frame("PageThree"),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming oslo_extraction.main takes a parameter

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
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)

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

        #button = tk.Button(master=self.excuteframe, text="RUN!", command = lambda: self.run_oslo_extraction(),width = 20, height =2)
        button = tk.Button(master=self.excuteframe, text="RUN!", command=lambda: controller.show_frame("PageThree"),width = 20, height =2)
        button.pack()


        button1 = tk.Button(master=self.infoframe, text="Back to Home", command=lambda: controller.show_frame("StartPage"))
        button1.grid(row = 0, column = 0)
        button2 = tk.Button(master=self.infoframe, text="Back to Extraction", command=lambda: controller.show_frame("PageThree"))
        button2.grid(row = 0, column = 1)


    def run_oslo_extraction(self):
        try:
            # so that sim_name is updated when clicked
            sim_name = SharedVariables.sim_variable.get() # call variables saved in a shared places.
            #main_option = SharedVariables.main_option.get()
            main_option = SharedVariables.main_option
            # self.update_user_input(sim_name)
            # Assuming oslo_extraction.main takes a parameter

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
            continue_process = oslo_extraction.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
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
            print("Error in oslo_extraction.py:", e)


