#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: October 2022
# Modified on: 10/02/2023
#=================================================================
"""
This module was built to extract oslo output.
The following essential files are required:
- SimulationName.oof (result file)
- CMD.exe
- osop.exe
- SimulationName.osop.lst (optional)

This module has been specifically designed to exclude all external packages so that
the code is compatible with Network Rail policy.

This module was modified to be fit into a OSLO add in app
"""
#=================================================================
# VERSION LOG
# V1.0 (Jieming Ye) - Initial Version converting from old 1.4 version from oslo extraciton
#=================================================================
# Set Information Variable
__author__ = "Jieming ye"
__copyright__ = "Copyright 2023, Network Rail Design Delivery"
__credits__ = "Jieming Ye"
__version__ = "1.0"
__email__ = "jieming.ye@networkrail.co.uk"
__status__ = "Deployed"

#import sys
import os
#import math
#import copy
# try:
#     from shared_contents import SharedMethods
# except ModuleNotFoundError:
#     from vision_oslo_extension.shared_contents import SharedMethods


# from shared_contents import SharedMethods
from vision_oslo_extension.shared_contents import SharedMethods

#import numpy as np # not supported by Network Rail Corp

#from subprocess import check_output # not support by Network Rail Corp

#import panda # not supported by Network Rail Corp

def main(simname, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):

    #User Interface - Welcome message:
    print("VISION/OSLO Default Extraction Process")
    print("")
    print("Copyright: NRDD 2023")
    print("")    

    # get simulation name name from input
    print("Checking Result File...")
    # simname = input()

    check = SharedMethods.check_oofresult_file(simname)
    #print(check)
    if check == False:
        return False
    
    if option_select == '0':
        print('Please select an Option to proceed...')
        return False

    # resultfile = simname + ".oof"

    # if not os.path.isfile(resultfile): # if the oof file exist
    #    print("Result file {} does not exist. Exiting...".format(resultfile))
    #    return False
    
    main_menu(simname, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)

    return True


    
#============Main Class: For Multiple Extraction================
def main_menu(simname, option, time_start, time_end, option_select, text_input, low_v,high_v, time_step):


    # # user input selection
    # print("\nPlease select from the list what you want to do:(awaiting input)")
    # print("1: Listing of electrical file")
    # print("2: Snapshot")
    # print("3: Individual train step output")
    # print("4: Maximum currents and minimum and maximum voltages")
    # print("5: Train high voltage summary")
    # print("6: Train low voltage summary")
    # print("7: Average MW and MVAr demoands in supply points, metering points, static VAr compensators and motor alternators")
    # print("8: Feeder step output")
    # print("9: Branch step output")
    # print("10: Transformer step output")
    # print("11: Smoothed feeder currents")
    # print("12: Smoothed branch currents")
    # print("13: Supply point persistent currents (development in progress)")
    # print("14: Output to data files")
    # print("15: One stop extraction - For AC Average Power Spreadsheet")
    # print("16: One stop extraction - For DC Smoothed Current Spreadsheet")
    # print("0: Exit the programme")
    
    option = option

    #print(option) # for debug

    if option not in ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16"]:
        print("Error: Contact Support. Issue in oslo_extraction.py --> main_menu")
        return False


    if option == "0":
        print("Warning: Please select an option and run again")
        return False

    if option == "1":
        list_extract(simname, time_start, time_end, option_select)
        
    elif option == "2":
        snapshot(simname, time_start)

    elif option == "3":
        train_step(simname, time_start, time_end, option_select, text_input)

    elif option == "4":
        min_max(simname)
        
    elif option == "5":
        train_highv(simname, option_select, high_v)

    elif option == "6":
        train_lowv(simname, option_select, low_v)

    elif option == "7":
        average_demand(simname, time_start, time_end, option_select, text_input, time_step)

    elif option == "8":
        feeder_step(simname, time_start, time_end, option_select, text_input)

    elif option == "9":
        branch_step(simname, time_start, time_end, option_select, text_input)

    elif option == "10":
        tranx_step(simname, time_start, time_end, option_select, text_input)

    elif option == "11":
        feeder_smooth(simname, option_select, text_input, time_step)

    elif option == "12":
        branch_smooth(simname, option_select, text_input, time_step)

    elif option == "13":
        persist_current(simname)

    elif option == "14":
        output_data(simname)

    # elif option == "15":
    #     print("Pre-check: Have you provided the ""FeederList.txt"" file?")
    #     print("Checking...")

    #     if not os.path.isfile("FeederList.txt"):
    #         print("Please provide the essential file. Exiting...")
    #     else:
    #         print("Essential file exist. Ready to go!")
    #         one_stop_AC_average(simname)
    
    # elif option == "16":
    #     print("Pre-check: Have you provided the ""BranchNodeList.txt"" file?")
    #     print("Checking...")

    #     if not os.path.isfile("BranchNodeList.txt"):
    #         print("Please provide the essential file. Exiting...")
    #     else:
    #         print("Essential file exist. Ready to go!")
    #         one_stop_DC_current_smooth(simname)

    print("")
    print("oslo extraction loop completed. Check information above")
    print("")
    # option = input()

    # if option == "0":
    #     return False  # Indicate that the process should not continue
    # else:
    #     main_menu(simname)
    #     return True  # Indicate that the process should continue
   
    return

#=============Option 1 List Extraction==========================
def list_extract(simname, time_start, time_end, option_select):

    print("List Input File Process" )
    print("\nOption selected --> Option {}".format(option_select))
    # print("1: List Input File" )
    # print("2: List Input File From Start to End")
    # print("3: List Input File Header Only")
    # print("0: Exit the Programme")

    option = option_select

    if option not in ["1","2","3","0"]:
        print("Error: Contact Support. oslo_extraction.py-->list_extract")
        return 

    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"
    
    if option == "1":
        # prepare the OPC file
        with open(opcname,"w") as fopc:
            fopc.writelines("LIST INPUT FILE\n")
        # Running the OSOP extraction
        SharedMethods.osop_running(cmdline)

    elif option == "2":
        # User defined time windows extraction
        print("\nThe selected 7 digit start time in DHHMMSS format{}".format(time_start))
        time_start = SharedMethods.time_input_process(time_start,1)
        print("\nThe selected 7 digit end time in DHHMMSS format{}".format(time_end))
        time_end = SharedMethods.time_input_process(time_end,1)

        if time_start == False or time_end == False:
            return False
        
        # prepare the OPC file
        with open(opcname,"w") as fopc:
            fopc.writelines("LIST INPUT FILE FROM "+time_start+" TO "+time_end+"\n")
        # Running the OSOP extraction
        SharedMethods.osop_running(cmdline)
        
    elif option == "3":
        # prepare the OPC file
        with open(opcname,"w") as fopc:
            fopc.writelines("LIST INPUT FILE HEADER ONLY\n")
        # Running the OSOP extraction
        SharedMethods.osop_running(cmdline)

    # elif option == "0":
    #     input("Exiting...Press anykey to close this window.")
    #     return False
        
    return

#=============Option 2 Snapshot==========================      
def snapshot(simname, time_start):

    print("\nThe 7 digit time in DHHMMSS format {}".format(time_start))
    time = SharedMethods.time_input_process(time_start,1)

    if time == False:
        return False

    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    with open(opcname,"w") as fopc:
        fopc.writelines("SNAPSHOT AT "+time+"\n")

    SharedMethods.osop_running(cmdline)
       
    return

#=============Option 3 Train Step Output==========================
def train_step(simname, time_start, time_end, option_select, text_input):

    # print("\nPlease select the option:(awaiting input)")
    # print("1: Single Train Step Output")
    # print("2: Multiple Train Step Output:")
    # print("   A text file named as ""TrainList"" is required")
    # print("3: Multiple Train Step Output:")
    # print("   Manually Input one by one")
    # print("0: Exit the Programme")
    print("\nOption selected --> Option {}".format(option_select))

    option = option_select

    # if option == "0":
    #     input("Exiting...Press anykey to close this window.")
    #     return False

    if option not in ["1","2","3","0"]:
        print("Error: Contact Support. oslo_extraction.py-->train_step")
        return

    # User defined time windows extraction
    print("\nThe selected 7 digit start time in DHHMMSS format{}".format(time_start))
    time_start = SharedMethods.time_input_process(time_start,1)
    print("\nThe selected 7 digit end time in DHHMMSS format{}".format(time_end))
    time_end = SharedMethods.time_input_process(time_end,1)

    if time_start == False or time_end == False:
        return False

    if option == "1":
        print("\nThe VISION train ID (1-9999): {}".format(text_input))
        train_id = int(text_input)
        train_step_one(simname,train_id,time_start,time_end)
    elif option == "2":
        print("\nProsessing trains listed in TrainList.txt")        
        # prepare the list file
        #print("\nPlease enter the branch list file name:(awaiting input)")
        #branch_name = input()
        #branch_list = branch_name + ".txt"
        train_list = "TrainList.txt"
##        if not os.path.isfile(train_list): # if the branch list file exist
##           input("Train list file {} does not exist. Please select another option.".format(train_list))
##           train_step(simname)
##
##        # reading the train list file
##        text_input = []
##        with open(train_list) as fbrlist:
##            for index, line in enumerate(fbrlist):
##                text_input.append(line[:50].strip())

        text_input = SharedMethods.file_read_import(train_list,simname)

        # processing the list
        for items in text_input:
            train_step_one(simname,int(items),time_start,time_end)

    elif option == "3":
        while True:   
            print("\nPlease enter the VISION train ID (1-9999) or 0 to Finish")
            finish = input()
            if finish == "0": break
            train_step_one(simname,int(finish),time_start,time_end)
           
    return

def train_step_one(simname,train_id,time_start,time_end):
    
    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    if 1 <= len(str(train_id)) <= 3:
        train_no = format(train_id,'03d')
    elif 4 <= len(str(train_id)) <= 5:
        train_no = format(train_id,'05d')

    #print(train_no)

    with open(opcname,"w") as fopc:
        fopc.writelines("TRAIN "+train_no+" STEPS FROM "+time_start+" TO "+time_end+"\n")

    SharedMethods.osop_running(cmdline)

    #rename the file
    old_name = simname + ".osop.ds1"
    new_name = simname + "_train_"+ train_no + ".osop.ds1"

    SharedMethods.file_rename(old_name,new_name)
        
    return

#=============Option 4 Min Max Value==========================      
def min_max(simname):

    print("\nMinimum and Maximum Values will be extracted...")

    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    with open(opcname,"w") as fopc:
        fopc.writelines("MINMAX VALUES REQUIRED\n")

    SharedMethods.osop_running(cmdline)

    
    return

#=============Option 5 High Voltage Summary==========================      
def train_highv(simname, option_select, high_v):

    print("\nThe 4 digits threshold in XX.X kV format {} kV".format(high_v))
    threshold = high_v

    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    with open(opcname,"w") as fopc:
        fopc.writelines("TRAIN VOLTS MAX "+threshold+" KV\n")

    SharedMethods.osop_running(cmdline)

    #rename the file
    old_name = simname + ".osop.vlt"
    new_name = simname + "_maxtime.osop.vlt"

    SharedMethods.file_rename(old_name,new_name)
       
    return

#=============Option 6 Low Voltage Summary==========================      
def train_lowv(simname, option_select, low_v):

    print("\nThe 4 digits threshold in XX.X kV format {} kV".format(low_v))
    threshold = low_v

    print("Low Voltage Summary" )
    print("\nOption selected --> Option {}".format(option_select))

    option = option_select

    if option == "0":
        print("Warning: Please select an option and run again")
        return

    if option not in ["1","2","0"]:
        print("Error: Contact Support. oslo_extraction.py")
        return

    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    if option == "1":
        with open(opcname,"w") as fopc:
            fopc.writelines("TRAIN VOLTS MIN "+threshold+" KV\n")

        SharedMethods.osop_running(cmdline)

        old_name = simname + ".osop.vlt"
        new_name = simname + "_mintime.osop.vlt"

        SharedMethods.file_rename(old_name,new_name)
    else:
        with open(opcname,"w") as fopc:
            fopc.writelines("TRAIN VOLTS MIN "+threshold+" KV DETAILED OUTPUT\n")

        SharedMethods.osop_running(cmdline)

        old_name = simname + ".osop.vlt"
        new_name = simname + "_mindetail.osop.vlt"

        SharedMethods.file_rename(old_name,new_name)
          
    return

#=============Option 7 average demand==========================      
def average_demand(simname, time_start, time_end, option_select, text_input, time_step):

    # print("\nPlease select the option:(awaiting input)")
    # print("1: Single Feeder Output")
    # print("2: Multiple Feeder Output:")
    # print("   A text file named as ""FeederList"" is required")
    # print("3: Multiple Feeder Output:")
    # print("   Manually input one by one")
    # print("0: Exit the Programme")

    print("Average Power Demand" )
    print("\nOption selected --> Option {}".format(option_select))

    option = option_select

    if option == "0":
        print("Warning: Please select an option and run again")
        return

    if option not in ["1","2","3","0"]:
        print("Error: Contact Support. oslo_extraction.py")
        return

    # User defined time windows extraction
    print("\nThe selected 7 digit start time in DHHMMSS format{}".format(time_start))
    time_start = SharedMethods.time_input_process(time_start,1)
    print("\nThe selected 7 digit end time in DHHMMSS format{}".format(time_end))
    time_end = SharedMethods.time_input_process(time_end,1)

    if time_start == False or time_end == False:
        return False

    # User defined time windows extraction
    print("\nThe time windows (in minutes) for average analysis (max 2 digits) {} min.".format(time_step))

    # time_step = input()
    time = time_step.rjust(2)

    if option == "1":
        print("\nThe Supply Point Name(maximum 4 digits): {}".format(text_input))
        feeder_id = text_input
        feeder_avg_one(simname,feeder_id,time_start,time_end,time)
    elif option == "2":
        print("\nProsessing feeders listed in FeederList.txt")        
        # prepare the list file

        feeder_list = "FeederList.txt"
##        if not os.path.isfile(feeder_list): # if the branch list file exist
##           input("Feeder list file {} does not exist. Please select another option.".format(feeder_list))
##           feeder_step(simname)
##
##        # reading the train list file
##        text_input = []
##        with open(feeder_list) as fbrlist:
##            for index, line in enumerate(fbrlist):
##                text_input.append(line[:50].strip())
##        #print(text_input)

        text_input = SharedMethods.file_read_import(feeder_list,simname)

        # processing the list
        for items in text_input:
            #print(items)
            feeder_avg_one(simname,items,time_start,time_end,time)

    elif option == "3":
        while True:   
            print("\nPlease enter the Supply Point Name(maximum 4 digits) or 0 to Finish")
            finish = input()
            if finish == "0": break
            feeder_avg_one(simname,finish,time_start,time_end,time)
           
    return

def feeder_avg_one(simname,feeder_id,time_start,time_end,time):
    
    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    feeder = feeder_id.rjust(4) # right justified 4 digits


    with open(opcname,"w") as fopc:
        fopc.writelines("POWER CALCS EVERY "+time+" MINUTES FROM "+time_start+" TO "+time_end+" FOR 01 ITEMS\n")
        fopc.writelines("           "+feeder+"\n")
    SharedMethods.osop_running(cmdline)

    #rename the file
    old_name = simname + ".osop.pwr"
    new_name = simname + "_"+ feeder + ".osop.pwr"

    SharedMethods.file_rename(old_name,new_name)
        
    return

#=============Option 8 Feeder Step Output==========================
def feeder_step(simname, time_start, time_end, option_select, text_input):

    # print("\nPlease select the option:(awaiting input)")
    # print("1: Single Feeder Step Output")
    # print("2: Multiple Feeder Step Output:")
    # print("   A text file named as ""FeederList"" is required")
    # print("3: Multiple Feeder Step Output:")
    # print("   Manually input one by one")
    # print("0: Exit the Programme")

    print("Feeder Step Output" )
    print("\nOption selected --> Option {}".format(option_select))

    option = option_select

    if option == "0":
        print("Warning: Please select an option and run again")
        return

    if option not in ["1","2","3","0"]:
        print("Error: Contact Support. oslo_extraction.py")
        return

    # User defined time windows extraction
    print("\nThe selected 7 digit start time in DHHMMSS format{}".format(time_start))
    time_start = SharedMethods.time_input_process(time_start,1)
    print("\nThe selected 7 digit end time in DHHMMSS format{}".format(time_end))
    time_end = SharedMethods.time_input_process(time_end,1)

    if time_start == False or time_end == False:
        return False

    if option == "1":
        print("\nThe Supply Point Name(maximum 4 digits): {}".format(text_input))
        feeder_id = text_input
        feeder_step_one(simname,feeder_id,time_start,time_end)
    elif option == "2":
        print("\nProsessing feeders listed in FeederList.txt")        
        # prepare the list file

        feeder_list = "FeederList.txt"
##        if not os.path.isfile(feeder_list): # if the branch list file exist
##           input("Feeder list file {} does not exist. Please select another option.".format(feeder_list))
##           feeder_step(simname)
##
##        # reading the train list file
##        text_input = []
##        with open(feeder_list) as fbrlist:
##            for index, line in enumerate(fbrlist):
##                text_input.append(line[:50].strip())
##        #print(text_input)

        text_input = SharedMethods.file_read_import(feeder_list,simname)

        # processing the list
        for items in text_input:
            #print(items)
            feeder_step_one(simname,items,time_start,time_end)

    elif option == "3":
        while True:   
            print("\nPlease enter the Supply Point Name(maximum 4 digits) or 0 to Finish")
            finish = input()
            if finish == "0": break
            feeder_step_one(simname,finish,time_start,time_end)
           
    return

def feeder_step_one(simname,feeder_id,time_start,time_end):
    
    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    feeder = feeder_id.ljust(4) # left justified 4 digits


    with open(opcname,"w") as fopc:
        fopc.writelines("FEEDER STEPS FROM "+time_start+" TO "+time_end+" FOR 01 ITEMS\n")
        fopc.writelines("           "+feeder+"\n")
    SharedMethods.osop_running(cmdline)

    #rename the file
    old_name = simname + ".osop.d4"
    new_name = simname + "_"+ feeder + ".osop.d4"

    SharedMethods.file_rename(old_name,new_name)
        
    return

#=============Option 9 Branch Step Output==========================
def branch_step(simname, time_start, time_end, option_select, text_input):

    # print("\nPlease select the option:(awaiting input)")
    # print("1: Single Branch Node Step Output")
    # print("2: Multiple Branch Node Step Output:")
    # print("   A text file named as ""BranchNodeList"" is required")
    # print("3: Multiple Branch Node Step Output:")
    # print("   Manually input one by one")
    # print("0: Exit the Programme")

    print("Branch Step Output" )
    print("\nOption selected --> Option {}".format(option_select))

    option = option_select

    if option == "0":
        print("Warning: Please select an option and run again")
        return

    if option not in ["1","2","3","0"]:
        print("Error: Contact Support. oslo_extraction.py")
        return

    # User defined time windows extraction
    print("\nThe selected 7 digit start time in DHHMMSS format{}".format(time_start))
    time_start = SharedMethods.time_input_process(time_start,1)
    print("\nThe selected 7 digit end time in DHHMMSS format{}".format(time_end))
    time_end = SharedMethods.time_input_process(time_end,1)

    if time_start == False or time_end == False:
        return False

    if option == "1":
        print("\nThe Branch Node Name(Format:XXXX/X): {}".format(text_input))
        branch_id = text_input
        branch_step_one(simname,branch_id,time_start,time_end)
    elif option == "2":
        print("\nProsessing branches listed in BranchNodeList.txt")        
        # prepare the list file

        branch_list = "BranchNodeList.txt"
##        if not os.path.isfile(branch_list): # if the branch list file exist
##           input("Branch list file {} does not exist. Please select another option.".format(branch_list))
##           branch_step(simname)
##
##        # reading the train list file
##        text_input = []
##        with open(branch_list) as fbrlist:
##            for index, line in enumerate(fbrlist):
##                text_input.append(line[:50].strip())
##        #print(text_input)

        text_input = SharedMethods.file_read_import(branch_list,simname)
        # processing the list
        for items in text_input:
            #print(items)
            branch_step_one(simname,items,time_start,time_end)

    elif option == "3":
        while True:   
            print("\nPlease enter the Branch Node Name(Format:XXXX/X) or 0 to Finish")
            finish = input()
            if finish == "0": break
            branch_step_one(simname,finish,time_start,time_end)
           
    return

def branch_step_one(simname,branch_id,time_start,time_end):
    
    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    if len(branch_id) < 6:
        branch = branch_id[:len(branch_id)-2].ljust(4)+branch_id[-2:]
    else:       
        branch = branch_id.rjust(6) # right justified 6 digits

    with open(opcname,"w") as fopc:
        fopc.writelines("BRANCH STEPS FROM "+time_start+" TO "+time_end+" FOR 01 ITEMS\n")
        fopc.writelines("           "+branch+"\n")
    SharedMethods.osop_running(cmdline)

    #rename the file
    old_name = simname + ".osop.d4"
    new_name = simname + "_"+ branch[:4]+"-"+ branch[-1:]+ ".osop.d4"

    SharedMethods.file_rename(old_name,new_name)
        
    return

#=============Option 10 Transformer Step Output==========================
def tranx_step(simname, time_start, time_end, option_select, text_input):

    # print("\nPlease select the option:(awaiting input)")
    # print("1: Single Transformer Step Output")
    # print("2: Multiple Transformer Step Output:")
    # print("   A text file named as ""TransformerList"" is required")
    # print("3: Multiple Transformer Step Output:")
    # print("   Manually input one by one")
    # print("0: Exit the Programme")

    print("Transformer Step Output" )
    print("\nOption selected --> Option {}".format(option_select))

    option = option_select

    if option == "0":
        print("Warning: Please select an option and run again")
        return

    if option not in ["1","2","3","0"]:
        print("Error: Contact Support. oslo_extraction.py")
        return

    # User defined time windows extraction
    print("\nThe selected 7 digit start time in DHHMMSS format{}".format(time_start))
    time_start = SharedMethods.time_input_process(time_start,1)
    print("\nThe selected 7 digit end time in DHHMMSS format{}".format(time_end))
    time_end = SharedMethods.time_input_process(time_end,1)

    if time_start == False or time_end == False:
        return False

    if option == "1":
        print("\nThe Transformer Name(maximum 4 digits): {}".format(text_input))
        tranx_id = text_input
        tranx_step_one(simname,tranx_id,time_start,time_end)
    elif option == "2":
        print("\nProsessing tranx listed in TransformerList.txt")        
        # prepare the list file

        tranx_list = "TransformerList.txt"
##        if not os.path.isfile(tranx_list): # if the branch list file exist
##           input("Transformer list file {} does not exist. Please select another option.".format(feeder_list))
##           tranx_step(simname)
##
##        # reading the train list file
##        text_input = []
##        with open(tranx_list) as fbrlist:
##            for index, line in enumerate(fbrlist):
##                text_input.append(line[:50].strip())
##        #print(text_input)
        
        text_input = SharedMethods.file_read_import(tranx_list,simname)

        # processing the list
        for items in text_input:
            #print(items)
            tranx_step_one(simname,items,time_start,time_end)

    elif option == "3":
        while True:   
            print("\nPlease enter the Supply Point Name(maximum 4 digits) or 0 to Finish")
            finish = input()
            if finish == "0": break
            tranx_step_one(simname,finish,time_start,time_end)
           
    return

def tranx_step_one(simname,tranx_id,time_start,time_end):
    
    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    tranx = tranx_id.rjust(4) # right justified 4 digits


    with open(opcname,"w") as fopc:
        fopc.writelines("TRANSFORMER STEPS FROM "+time_start+" TO "+time_end+" FOR 01 ITEMS\n")
        fopc.writelines("           "+tranx+"\n")
    SharedMethods.osop_running(cmdline)

    #rename the file
    old_name = simname + ".osop.d4"
    new_name = simname + "_"+ tranx + ".osop.d4"

    SharedMethods.file_rename(old_name,new_name)
        
    return

#=============Option 11 Smoothed Feeder Current==========================
def feeder_smooth(simname, option_select, text_input, time_step):

    # print("\nPlease select the option:(awaiting input)")
    # print("1: Single Feeder Smoothed Current Output")
    # print("2: Multiple Feeder Smoothed Current Output:")
    # print("   A text file named as ""FeederList"" is required")
    # print("3: Multiple Feeder Smoothed Current Output:")
    # print("   Manually input one by one")
    # print("0: Exit the Programme")

    print("Feeder Smoothed Output" )
    print("\nOption selected --> Option {}".format(option_select))

    option = option_select

    if option == "0":
        print("Warning: Please select an option and run again")
        return

    if option not in ["1","2","3","0"]:
        print("Error: Contact Support. oslo_extraction.py")
        return

    # print("\nPlease select the analysis option:(awaiting input)")
    # print("1: Normal direction of real power flow")
    # print("2: Reverse direction of real power flow")

    # option1 = input()
    option1 = "all"

    # if option1 not in ["1","2"]:
    #     input("Invalid Selection. Press select agian!")
    #     feeder_smooth(simname)

    # User defined time windows extraction
    print("\nThe time steps analysied for (max 3 digits): {} steps".format(time_step))

    # time_step = input()

    time = time_step.rjust(3)


    if option == "1":
        print("\nThe Supply Point Name(maximum 4 digits): {}".format(text_input))
        feeder_id = text_input
        feeder_smooth_one(simname,feeder_id,time,option1)
    elif option == "2":
        print("\nProsessing feeders listed in FeederList.txt")        
        # prepare the list file

        feeder_list = "FeederList.txt"
##        if not os.path.isfile(feeder_list): # if the branch list file exist
##           input("Feeder list file {} does not exist. Please select another option.".format(feeder_list))
##           feeder_smooth(simname)
##
##        # reading the train list file
##        text_input = []
##        with open(feeder_list) as fbrlist:
##            for index, line in enumerate(fbrlist):
##                text_input.append(line[:50].strip())
##        #print(text_input)

        text_input = SharedMethods.file_read_import(feeder_list,simname)

        # processing the list
        for items in text_input:
            #print(items)
            feeder_smooth_one(simname,items,time,option1)

    elif option == "3":
        while True:   
            print("\nPlease enter the Supply Point Name(maximum 4 digits) or 0 to Finish")
            finish = input()
            if finish == "0": break
            feeder_smooth_one(simname,finish,time,option1)
           
    return

def feeder_smooth_one(simname,feeder_id,time,option1):
    
    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    feeder = feeder_id.rjust(4) # right justified 4 digits

    # if option1 == "1":
    #     add = ""
    # else:
    #     add = " (R)"
    
    add = ""
    with open(opcname,"w") as fopc:
        fopc.writelines("FEEDER AMPS OVER "+time+" STEPS FOR 01 ITEMS"+add+"\n")
        fopc.writelines("           "+feeder+"\n")
    SharedMethods.osop_running(cmdline)

    #rename the file
    old_name = "fort.12"
    new_name = feeder + "_normal_fort.12"

    SharedMethods.file_rename(old_name,new_name)

    add = " (R)"
    with open(opcname,"w") as fopc:
        fopc.writelines("FEEDER AMPS OVER "+time+" STEPS FOR 01 ITEMS"+add+"\n")
        fopc.writelines("           "+feeder+"\n")
    SharedMethods.osop_running(cmdline)

    #rename the file
    old_name = "fort.12"
    new_name = feeder + "_reverse_fort.12"

    SharedMethods.file_rename(old_name,new_name)
        
    return

#=============Option 12 Branch Smoothed Output==========================
def branch_smooth(simname, option_select, text_input, time_step):

    # print("\nPlease select the option:(awaiting input)")
    # print("1: Single Branch Node Smoothed Current Output")
    # print("2: Multiple Branch Node Smoothed Current Output:")
    # print("   A text file named as ""BranchNodeList"" is required")
    # print("3: Multiple Branch Node Smoothed Current Output:")
    # print("   Manually input one by one")
    # print("0: Exit the Programme")

    print("Branch Smoothed Output" )
    print("\nOption selected --> Option {}".format(option_select))


    option = option_select

    if option == "0":
        print("Warning: Please select an option and run again")
        return

    if option not in ["1","2","3","0"]:
        print("Error: Contact Support. oslo_extraction.py")
        return

    # User defined time windows extraction
    print("\nThe time steps analysied for (max 3 digits): {} steps".format(time_step))

    # time_step = input()

    time = time_step.rjust(3)

    if option == "1":
        print("\nThe Branch Node Name(Format:XXXX/X): {}".format(text_input))
        branch_id = text_input
        branch_smooth_one(simname,branch_id,time)
    elif option == "2":
        print("\nProsessing branches listed in BranchNodeList.txt")        
        # prepare the list file

        branch_list = "BranchNodeList.txt"
##        if not os.path.isfile(branch_list): # if the branch list file exist
##           input("Branch list file {} does not exist. Please select another option.".format(branch_list))
##           branch_smooth(simname)
##
##        # reading the train list file
##        text_input = []
##        with open(branch_list) as fbrlist:
##            for index, line in enumerate(fbrlist):
##                text_input.append(line[:50].strip())
        #print(text_input)

        text_input = SharedMethods.file_read_import(branch_list,simname)

        # processing the list
        for items in text_input:
            #print(items)
            branch_smooth_one(simname,items,time)

    elif option == "3":
        while True:   
            print("\nPlease enter the Branch Node Name(Format:XXXX/X) or 0 to Finish")
            finish = input()
            if finish == "0": break
            branch_smooth_one(simname,finish,time)
           
    return

def branch_smooth_one(simname,branch_id,time):
    
    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    if len(branch_id) < 6:
        branch = branch_id[:len(branch_id)-2].ljust(4)+branch_id[-2:]
    else:       
        branch = branch_id.rjust(6) # right justified 6 digits


    with open(opcname,"w") as fopc:
        fopc.writelines("BRANCH AMPS OVER "+time+" STEPS FOR\n")
        fopc.writelines(branch+"\n")
    SharedMethods.osop_running(cmdline)

    #rename the file
    old_name = simname + ".osop.mxn"
    new_name = simname + "_"+ branch[:4]+"-"+ branch[-1:]+ ".osop.mxn"

    SharedMethods.file_rename(old_name,new_name)
        
    return

#=============Option 13 in progress==========================      
def persist_current(simname):

    print("\nMinimum and Maximum Values will be extracted...")

    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    with open(opcname,"w") as fopc:
        fopc.writelines("MINMAX VALUES REQUIRED\n")

    SharedMethods.osop_running(cmdline)

    
    return

#=============Option 14 Output Data==========================      
def output_data(simname):

    print("\nOutput d1 and d3 file...")

    # define the default osop command
    cmdline = "osop " + simname    
    opcname = simname + ".opc"

    with open(opcname,"w") as fopc:
        fopc.writelines("DATA FILE OUTPUT\n")

    SharedMethods.osop_running(cmdline)

    
    return


#==========================================================================

# to exit the programme.
def issue_exit():
    input("Fatal error occurs. Please contact support! Press any key to exit...")
    return False

# run osop command
# def osop_running(cmdline):
#     with open("batch_run.bat","w") as fba:
#         fba.writelines(cmdline)
#     os.system("batch_run.bat")


# rename files
# def file_rename(old_name,new_name):
#     try:
#         os.rename(old_name,new_name)
#         print("File {} successfully created. Processing Continue...".format(new_name))
#     except FileExistsError:
#         os.remove(new_name)
#         os.rename(old_name,new_name)
#         print("File {} successfully replaced. Processing Continue...".format(new_name))
#     except FileNotFoundError:
#         print("\nFile {} FAILED as the OSOP extraction fail. Check Input...".format(new_name))

# # write to text file
# def file_write(header,creatname,listname):
#     with open(creatname, 'w') as fw:
#         fw.write(header)
#         for items in listname:
#             string_line = map(str,items) # string all item
#             result_line = ",".join(string_line) # join item removing brackets/quotes
#             fw.write("%s\n" % result_line) # print out

# # module to read the text file input    
# def SharedMethods.file_read_import(filename,modulename,simname):
    
#     if not os.path.isfile(filename): # if the file exist
#        input("Train list file {} does not exist. Please select another option.".format(filename))
#        modulename(simname)

#     # reading the train list file
#     text_input = []
#     with open(filename) as fbrlist:
#         for index, line in enumerate(fbrlist):
#             text_input.append(line[:50].strip())

#     return text_input
    
# module to check user input time
# def time_input_process(time_string):
    
#     #time_string = input()

#     if not len(time_string) == 7:
#         print("Invalid data input. Press reenter the 7 digit time.")
#         return False
#         # print("OR enter 0 to exit the programme.")
#         # time_string = input()
#         # if time_string == "0":
#         #     return False
#         # else:
#         #     SharedMethods.time_input_process(time_string)
            
#     day = int(time_string[:1])
#     hour = int(time_string[1:3])
#     minute = int(time_string[3:5])
#     second = int(time_string[5:7])

#     if not 0 <= day <= 9:
#         print("Invalid Day input. Press reenter the 7 digit time.")
#         return False
#         # print("OR enter 0 to exit the programme.")
#         # time_string = input()
#         # if time_string == "0":
#         #     return False
#         # else:
#         #     SharedMethods.time_input_process(time_string)
            
#     if not 0 <= hour <= 23:
#         print("Invalid Hour input. Press reenter the 7 digit time.")
#         return False
#         # print("OR enter 0 to exit the programme.")
#         # time_string = input()
#         # if time_string == "0":
#         #     return False
#         # else:
#         #     SharedMethods.time_input_process(time_string)
            
#     if not 0 <= minute <= 60:
#         print("Invalid Minute input. Press reenter the 7 digit time.")
#         return False
#         # print("OR enter 0 to exit the programme.")
#         # time_string = input()
#         # if time_string == "0":
#         #     return False
#         # else:
#         #     SharedMethods.time_input_process(time_string)
            
#     if not 0 <= second <= 60:
#         print("Invalid Second input. Press reenter the 7 digit time.")
#         return False
#         # print("OR enter 0 to exit the programme.")
#         # time_string = input()
#         # if time_string == "0":
#         #     return False
#         # else:
#         #     SharedMethods.time_input_process(time_string)


#     #debug purpose
#     #print(seconds_int)
#     # Return the second integer number as same used in the list file           
#     return time_string


# # copy from online to calculate averages without calling numpy
# # since numpy is not supported by default
# def calculate_averages(list_2d):
#     cell_total = list()
#     row_totals = dict()
#     column_totals = dict()
#     for row_idx, row in enumerate(list_2d):
#         for cell_idx, cell in enumerate(row):
#             # is cell a number?
#             if type(cell) in [int, float, complex]:
#                 cell_total.append(cell)                
#                 if row_idx in row_totals:
#                     row_totals[row_idx].append(cell)
#                 else:
#                     row_totals[row_idx] = [cell]
#                 if cell_idx in column_totals:
#                     column_totals[cell_idx].append(cell)
#                 else:
#                     column_totals[cell_idx] = [cell]
#     per_row_avg = [sum(row_totals[row_idx]) / len(row_totals[row_idx]) for row_idx in row_totals]
#     per_col_avg = [sum(column_totals[col_idx]) / len(column_totals[col_idx]) for col_idx in column_totals]
#     row_avg = sum(per_row_avg) / len(per_row_avg)
#     col_avg = sum(per_col_avg) / len(per_col_avg)
#     return {'cell_average': sum(cell_total) / len(cell_total),
#             'per_row_average': per_row_avg,
#             'per_column_average': per_col_avg,
#             'row_average': row_avg,
#             'column_average': col_avg}

# Check if the script is run as the main module
if __name__ == "__main__":
    # Add your debugging code here
    simname = "StraightLine1"  # Provide a simulation name or adjust as needed
    main_option = "6"  # Adjust as needed
    time_start = "0070000"  # Adjust as needed
    time_end = "0080000"  # Adjust as needed
    option_select = "1"  # Adjust as needed
    text_input = "1"  # Adjust as needed
    low_v = '.488'  # Adjust as needed
    high_v = None  # Adjust as needed
    time_step = None  # Adjust as needed

    # Call your main function with the provided parameters
    main(simname, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)

