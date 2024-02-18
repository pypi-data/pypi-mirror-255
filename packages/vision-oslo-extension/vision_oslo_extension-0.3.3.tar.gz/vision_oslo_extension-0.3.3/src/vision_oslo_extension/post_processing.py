#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: April 2022
# Last update: April 2023
#=================================================================
"""
This module was built to post processing the VISION/OSLO output.
The following essential files are required:
- SimulationName.oof (result file)
- CMD.exe
- osop.exe
- SimulationName.lst.txt (input list file)
- SimulationName.osop.lst (optional)

This module has been specifically designed to exclude all external packages so that
the code is compatible with Network Rail policy.
"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version converting from old 1.6 version from listprocessor
#=================================================================
# Set Information Variable
__author__ = "Jieming Ye"
__copyright__ = "Copyright 2023, Network Rail Design Delivery"
__credits__ = "Jieming Ye"
__version__ = "1.0"
__email__ = "jieming.ye@networkrail.co.uk"
__status__ = "under test"

import sys
import os
import math
import copy
import csv

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
    print("VISION/OSLO Post-Processing (no call osop)")
    print("")
    print("Copyright: NRDD 2022")
    print("")    

    #define the file name and check if the file exist or not

    # get simulation name name from input
    print("Checking Result File...")
    # simname = input()
    check = SharedMethods.check_oofresult_file(simname)
    if check == False:
        return False

    # resultfile = simname + ".oof"

    # if not os.path.isfile(resultfile): # if the oof file exist
    #    print("Result file {} does not exist. Exiting...".format(resultfile))
    #    return False
    
    main_menu(simname, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)

    return True
    
# Main Menu
def main_menu(simname, option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):

    # resultfile = simname + ".oof"
    # user input selection
    print("\nOption Selected --> Option {}".format(option_select))
    # print("1: Extract Train List Only")
    # print("2: Umeanuseful Calculation Only")
    # print("3: All of the Above")
    # print('4: Summary Report of Low Voltage Occurances(whole simulation)')
    # print('5: Summary Report of Low Voltage in Branches (whole simulation)')

    time_increment = 5

    
    if option not in ["0", "1","2","3","4","5"]:
        print("Error: Contact Support. Issue in post_processing.py")
        return False

    if option == "0":
        print("Warning: Please select an option and run again")
        return False

    if option == "1":
        list_train_data(simname, time_start, time_end, option_select, text_input)
        
    elif option == "2":
        low_voltage_analysis(simname, time_start, time_end, option_select, text_input, low_v)

    # elif option == "3":
    #     average_power(simname, time_start, time_end, option_select, text_input)

    elif option == "4":
        umean_useful(simname, time_start, time_end, option_select, text_input,time_increment)
        
    # elif option == "5":
    #     train_highv(simname, option_select, high_v)

    print("")
    print("Processing loop completed. Check information above")
    print("")
    return

#==================================================================================
# seleciton 1 list train data
def list_train_data(simname, time_start, time_end, option_select, text_input):

    br_list_input = []
    # branch_name = ""

    if option_select not in ["0","1","2","3","4"]:
        print("Error: Contact Support. Issue in post_processing.py --> list_train_data")
        return False

    if option_select in ["3","4"]:
        # prepare the list file
        print("\nCheck Branch List File...")
        # branch_name = input()
        branch_list = text_input + ".txt"
        if not os.path.isfile(branch_list): # if the branch list file exist
           print("Branch list file {} does not exist. Exiting...".format(branch_list))
           return False

        # reading the branch list file     
        with open(branch_list) as fbrlist:
            for index, line in enumerate(fbrlist):
                br_list_input.append(line[:50].strip())
        print(br_list_input)
    
    if option_select in ["2","4"]:
        # User defined time windows extraction
        print("\nThe analysis start time in DHHMMSS format is: {}".format(time_start))
        time_start = SharedMethods.time_input_process(time_start,2)
        print("\nThe analysis end time in DHHMMSS format: {}".format(time_end))
        time_end = SharedMethods.time_input_process(time_end,2)
        
        if time_start == False or time_end == False:
            return False

    time_info_sum = [option_select, time_start, time_end, br_list_input]

    # check the list file
    SharedMethods.check_lst_file(simname)

    filename = simname + ".osop.lst"
    # define essential list to be updated
    train_info = ["VISION ID","BHTPBANK"] # train basic information 
    train_e =[]

    branch_lookup = {} # dictionary data type
    u_branch_lookup = {} #dictonary data type for umean useful branch recognition

    # analysis list file
    lst_data_reading_process(filename,train_e,train_info,branch_lookup,u_branch_lookup)
    # List Train Information
    csv_train_info(train_e,branch_lookup,br_list_input,u_branch_lookup,time_info_sum,text_input)

# train information sort and output    
def csv_train_info(train_e,branch_lookup,br_list_input,u_branch_lookup,time_info_sum,branch_name):
    
    # select the output data
    if time_info_sum[0] == "1":
        sorted_train_e = copy.deepcopy(train_e) # memory consuming but want to avoid touching train_e
        output_name = 'train_list.csv'

    elif time_info_sum[0] == "2":
        output_name = 'train_list_'+str(time_info_sum[1])+"-"+str(time_info_sum[2])+'.csv'
        sorted_train_e = []

        print("Sorting the data within the selected time window...")
        
        
        for row in train_e:
            if time_info_sum[1] <= row[1] <= time_info_sum[2]:
                sorted_train_e.append(row)

        sorted_train_e = copy.deepcopy(sorted_train_e)

    elif time_info_sum[0] == "3":
        output_name = 'train_list_'+ branch_name +'.csv'
        sorted_train_e = []
        branch_id = []

        print("Sorting the data within the selected branches...")
        

        # get OSLO ID for branch input
        for item in br_list_input:
            branch_id.append(u_branch_lookup.get(item))
            
        for row in train_e:
            if row[12] in branch_id:
                sorted_train_e.append(row)
        sorted_train_e = copy.deepcopy(sorted_train_e)

    else:
        output_name = 'train_list_'+branch_name+ "_" + str(time_info_sum[1])+"-"+str(time_info_sum[2])+'.csv'
        stage_train_e = []
        sorted_train_e = []
        branch_id = []
        
        print("Sorting the data within the selected time window...")
        
        for row in train_e:
            if time_info_sum[1] <= row[1] <= time_info_sum[2]:
                stage_train_e.append(row)
        
        print("Sorting the data within the selected branches...")


        # get OSLO ID for branch input
        for item in br_list_input:
            branch_id.append(u_branch_lookup.get(item))
            
        for row in stage_train_e:
            if row[12] in branch_id:
                sorted_train_e.append(row)
        
        sorted_train_e = copy.deepcopy(sorted_train_e)
        
         
    # list data sorting with train No.
    sorted_train_e.sort(key=lambda row: (row[0], row[1]), reverse=False)

    # replace branch ID to branch Name from OSLO
    for row in range(len(sorted_train_e)):
        sorted_train_e[row][12] = branch_lookup.get(sorted_train_e[row][12])
     

##    sorted_train_e.insert(0, ["VO_ID","T_STEP","TIME","V_Re","V_Im","V_T", \
##                                  "I_Re","I_Im","I_T","P_Re","P_Im","P_T","BRANCH", \
##                                  "DELTA","E_TE","PERC%","DIS_GONE","INS_SPD","AV_SPD"])          
    #print(train_e)
    # write information to a text file
    print("Data Extraction Completed. Writing to csv file...")

    with open(output_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1
        writer.writerow(["VO_ID", "T_STEP", "TIME", "V_Re", "V_Im", "V_T", "I_Re", "I_Im", "I_T", \
                         "P_Re", "P_Im", "P_T", "BRANCH", "DELTA", "E_TE", "PERC%", "DIS_GONE", "INS_SPD", "AV_SPD"])
        row = row + 1
        writer.writerows(sorted_train_e)
        # for items in sorted_train_e:
        #     string_line = map(str,items) # string all item
        #     result_line = " ".join(string_line) # join item removing brackets/quotes
        #     fw.write("%s\n" % result_line) # print out

#=====================================================================================
# selection 2 low votlage analysis
def low_voltage_analysis(simname, time_start, time_end, option_select, text_input, low_v):

    print("\nThe voltage threshold in XXXXX format (V): {}".format(low_v))
    v_limit = float(low_v)
    if v_limit <= 0  or v_limit >= 30000:
        print("Error: invalid threshold. Please reenter a voltage threshold between 0 - 30000")
        return False

    br_list_input = []
    
    if option_select not in ["0","1","2","3"]:
        print("Error: Contact Support. Issue in post_processing.py -->low_voltage_analysis")
        return False

    if option_select in ["3"]:
        # prepare the list file
        print("\nCheck Branch List File...")
        # branch_name = input()
        branch_list = text_input + ".txt"
        if not os.path.isfile(branch_list): # if the branch list file exist
           print("Branch list file {} does not exist. Exiting...".format(branch_list))
           return False

        # reading the branch list file     
        with open(branch_list) as fbrlist:
            for index, line in enumerate(fbrlist):
                br_list_input.append(line[:50].strip())
        print(br_list_input)
    
    if option_select in ["2"]:
        # User defined time windows extraction
        print("\nThe analysis start time in DHHMMSS format is: {}".format(time_start))
        time_start = SharedMethods.time_input_process(time_start,2)
        print("\nThe analysis end time in DHHMMSS format: {}".format(time_end))
        time_end = SharedMethods.time_input_process(time_end,2)

    # # to be developed in the future
    # option_select = "1"

    time_info_sum = [option_select, time_start, time_end, br_list_input]
    #print(time_info_sum)
    # check the list file
    SharedMethods.check_lst_file(simname)

    filename = simname + ".osop.lst"
    # define essential list to be updated
    train_info = ["VISION ID","BHTPBANK"] # train basic information 
    train_e =[]

    branch_lookup = {} # dictionary data type
    u_branch_lookup = {} #dictonary data type for umean useful branch recognition
    
    # analysis list file
    lst_data_reading_process(filename,train_e,train_info,branch_lookup,u_branch_lookup)

    low_voltage_sum(simname,train_e,v_limit,branch_lookup,u_branch_lookup,time_info_sum,text_input)
    return

# 2nd module to check and output low votlage summary grouped by branches instead of trains
def low_voltage_sum(simname, train_e,v_limit,branch_lookup,u_branch_lookup,time_info_sum,branch_name):
    # select the output data

    print("Finding out information below threshold...")
    sorted_train_e = []
    for row in train_e:
        if row[5] < v_limit:
            sorted_train_e.append(row)

    sorted_train_e = copy.deepcopy(sorted_train_e)

    # list data sorting with train No.
    sorted_train_e.sort(key=lambda row: (row[0], row[1]), reverse=False)

    # replace branch ID to branch Name from OSLO
    for row in range(len(sorted_train_e)):
        sorted_train_e[row][12] = branch_lookup.get(sorted_train_e[row][12])
     
    # write information to a text file

    #run function to give a summary of the lowest voltage recorded on each branch
    branch_sum = get_branch_summary(sorted_train_e)

    #run function to give a summary of the lowest voltage recorded on each train
    train_sum = get_train_summary(sorted_train_e)

    print("Data Extraction Completed. Writing to text file...")

    #write list of low voltage instances
    with open(simname + '_train_list_below_' + str(int(v_limit))+'.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1

        header = ["VO_ID", "T_STEP", "TIME", "V_Re", "V_Im", "V_T", "I_Re", "I_Im", "I_T", "P_Re", "P_Im", "P_T", "BRANCH", "DELTA", "E_TE", "PERC%", "DIS_GONE", "INS_SPD", "AV_SPD"]
        writer.writerow(header)
        row = 2

        for items in sorted_train_e:
            writer.writerow(items)
            row = row + 1   

    #write train low voltage summary
    with open(simname + '_train_sum_below_' + str(int(v_limit))+'.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1

        header = ["Train No", "No. of instances", "Branch min V", "VO_ID", "T_STEP", "TIME", "V_Re", "V_Im", "V_T", "I_Re", "I_Im", "I_T", "P_Re", "P_Im", "P_T", "BRANCH", "DELTA", "E_TE", "PERC%", "DIS_GONE", "INS_SPD", "AV_SPD"]
        writer.writerow(header)
        row = 2

        for items in train_sum:
            writer.writerow(items)
            row = row + 1  

    #write branch low voltage summary
    with open(simname+'_branch_list_below_' + str(int(v_limit))+'.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1

        header = ["BRANCH", "No. of instances", "Branch min V", "VO_ID", "T_STEP", "TIME", "V_Re", "V_Im", "V_T", "I_Re", "I_Im", "I_T", "P_Re", "P_Im", "P_T", "BRANCH", "DELTA", "E_TE", "PERC%", "DIS_GONE", "INS_SPD", "AV_SPD"]
        writer.writerow(header)
        row = 2

        for items in branch_sum:
            writer.writerow(items)
            row = row + 1  
    return

#define function to give a summary of the low voltage occurances in a branch. 
def get_branch_summary(data):

  branch_dict = {}

  for row in data:
    branch_name = row[12]
    v_t = row[5]
    detail_in = row

    if branch_name not in branch_dict:
      branch_dict[branch_name] = {"count": 0, "min_v_t": v_t,"in":detail_in}
    
    branch_dict[branch_name]["count"] += 1
    if v_t < branch_dict[branch_name]["min_v_t"]:
        branch_dict[branch_name]["min_v_t"] = v_t
        branch_dict[branch_name]["in"] = detail_in

  summary = []
  for branch, info in branch_dict.items():
    line = [branch, info["count"], info["min_v_t"]]
    for item in info["in"]:
        line.append(item)

    summary.append(line)

  return summary

#define function to give a summary of the low voltage occurances of the train. 
def get_train_summary(data):

  train_dict = {}

  for row in data:
    train_name = row[0]
    v_t = row[5]
    detail_in = row

    if train_name not in train_dict:
      train_dict[train_name] = {"count": 0, "min_v_t": v_t,"in":detail_in}
    
    train_dict[train_name]["count"] += 1
    if v_t < train_dict[train_name]["min_v_t"]:
        train_dict[train_name]["min_v_t"] = v_t
        train_dict[train_name]["in"] = detail_in

  summary = []
  for train, info in train_dict.items():
    line = [train, info["count"], info["min_v_t"]]
    for item in info["in"]:
        line.append(item)
        
    summary.append(line)

  return summary


#======================================================================================
# selection 4 umeanuseful
def umean_useful(simname, time_start, time_end, option_select, text_input,time_increment):
    br_list_input = []
    # branch_name = ""

    if option_select not in ["0","1","2"]:
        print("Error: Contact Support. Issue in post_processing.py --> umean_useful")
        return False

    print("\nCheck Branch List File...")
    # branch_name = input()
    branch_list = text_input + ".txt"
    if not os.path.isfile(branch_list): # if the branch list file exist
        print("Branch list file {} does not exist. Please Enter the correct branch file name.".format(branch_list))
        return False

    # reading the branch list file     
    with open(branch_list) as fbrlist:
        for index, line in enumerate(fbrlist):
            br_list_input.append(line[:50].strip())
    print(br_list_input)

    
    if option_select == "2":
        # User defined time windows extraction
        print("\nThe analysis start time in DHHMMSS format is: {}".format(time_start))
        time_start = SharedMethods.time_input_process(time_start,2)
        print("\nThe analysis end time in DHHMMSS format: {}".format(time_end))
        time_end = SharedMethods.time_input_process(time_end,2)
    
    time_info_sum = [option_select, time_start, time_end, br_list_input]
    
    # check the list file
    SharedMethods.check_lst_file(simname)

    filename = simname + ".osop.lst"
    # define essential list to be updated
    train_info = ["VISION ID","BHTPBANK"] # train basic information 
    train_e =[]
    branch_lookup = {} # dictionary data type
    u_branch_lookup = {} #dictonary data type for umean useful branch recognition

    # analysis list file
    lst_data_reading_process(filename,train_e,train_info,branch_lookup,u_branch_lookup)

    # List Train Information
    umean_useful_process(train_e,br_list_input,u_branch_lookup,time_info_sum,text_input,time_increment)

    return

# Umean useful calculation process
def umean_useful_process(train_e,br_list_input,u_branch_lookup,time_info_sum,branch_name,time_increment):
    print("Umean useful calculation start:")
    time_increase = int(time_increment)
    # create umeanuseful list file
    umean_train_vs = {} # dictionary type to save the total voltage sum
    umean_train_time = {} # ditctionary type to save the total time sum
    branch_id = [] # branch list integer ID
    
    umean_zone = [] # 1d list
    umeanuseful_train = [] #list type

    # get OSLO ID for branch input
    for item in br_list_input:
        branch_id.append(u_branch_lookup.get(item))
    
    # calculate umean useful (Umean zone consider the selected time windows, Umean train consider the whole period)
    if time_info_sum[0] == "2": 
        output_name = 'umeanuseful_result_'+branch_name+'_'+str(time_info_sum[1])+"-"+str(time_info_sum[2])+'.csv'
        for row in range(len(train_e)):
            #print(train_e[row][12],train_e[row][1])
            # umean zone: save all pantograph voltage point in a list within time window
            if (train_e[row][12] in branch_id) and (time_info_sum[1] <= train_e[row][1]) and (train_e[row][1] <= time_info_sum[2]):
                umean_zone.append(train_e[row][5])

            # umean train:
            if (train_e[row][12] in branch_id) and (train_e[row][14]>0):
                train_id = train_e[row][0]
                if train_id not in umean_train_vs:
                    umean_train_vs[train_id] = train_e[row][5]
                    umean_train_time[train_id] = 1
                else:
                    umean_train_vs[train_id] = train_e[row][5] + umean_train_vs.get(train_id)
                    umean_train_time[train_id] += 1
    else:
        output_name = 'umeanuseful_result_'+branch_name+'_full.csv'
        for row in range(len(train_e)):
            # umean zone: save all pantograph voltage point in a list
            if train_e[row][12] in branch_id:
                umean_zone.append(train_e[row][5])
                
            # umean train:
            # data format now: umean_train = {Train ID: [Sum of Volt]}
            # data format now: Umean_train_list = [Train ID, UV, TimeSpan]
            if (train_e[row][12] in branch_id) and (train_e[row][14]>0):
                train_id = train_e[row][0]
                if train_id not in umean_train_vs:
                    umean_train_vs[train_id] = train_e[row][5]
                    umean_train_time[train_id] = 1
                else:
                    umean_train_vs[train_id] = train_e[row][5] + umean_train_vs.get(train_id)
                    umean_train_time[train_id] += 1
    

    #print(umean_zone[0])
    #print(umean_train_list[0])
                
    #print(umean_train_vs) = sum / item no
    umeanuseful_zone = round(sum(umean_zone)/len(umean_zone)/1000, 2)

    #print(umean_train) = sum / time step no
    for train_index, volt in umean_train_vs.items():
        umeanuseful_train.append([train_index, \
                                  round(volt/umean_train_time.get(train_index)/1000,2)])

    #print(umeanuseful_train)

    # sort umean useful train in decesending order
    umeanuseful_train.sort(key=lambda row: (row[1]), reverse=False)

    # # adding addtional information about the train
    for row in range(len(umeanuseful_train)):
        # umeanuseful_train[row][1] = str(umeanuseful_train[row][1]) + " kV"
        # umeanuseful_train[row].append(str(umean_train_time.get(umeanuseful_train[row][0])*5)+" s")
        umeanuseful_train[row].append(str(umean_train_time.get(umeanuseful_train[row][0])*time_increase))
        
    #print(umeanuseful_train)

    print("U mean useful Calculation Completed")
    print("U mean zone is {} kV".format(umeanuseful_zone))
    print("U mean train is {} kV".format(umeanuseful_train[0][1]))

    # write umeanuseful result to text file
    # print("Writing umeanuseful to text file...")
    # with open(output_name, 'w') as fw:
    #     fw.write("Umean useful zone is:\n")
    #     fw.write("%s kV\n" % umeanuseful_zone)
    #     fw.write("Umean useful train is (in ascending order):\n")
    #     fw.write("VISION_ID Umean(train) kV +TE_Time s\n")
    #     for items in umeanuseful_train:
    #         string_line = map(str,items) # string all item
    #         result_line = " ".join(string_line) # join item removing brackets/quotes
    #         fw.write("%s\n" % result_line) # print out
    
    with open(output_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1
        writer.writerow(["Umean useful zone (in kV)"])
        row = row + 1
        writer.writerow([umeanuseful_zone])
        row = row + 1
        writer.writerow([""])
        row = row + 1
        writer.writerow(["Umean useful train list (in ascending order)"])
        row = row + 1
        writer.writerow(["VISION ID","Umean(train) (kV)","Traction Time (s)"])
        row = row + 1
        writer.writerows(umeanuseful_train)

#=================================================================================
# define list data process
def lst_data_reading_process(filename,train_e,train_info,branch_lookup,u_branch_lookup):
    #define essential variables
    lst_section = ""  # list section ID
    ins_sec = 0     # instant second
    ins_time = ""   # instant time

    # open text file to get the total line information (best way i can think of)
    # although it require reading the file twice
    print("Analysing lst file....")
    with open(filename) as fp:
        total_line = sum(1 for line in enumerate(fp))

    print("Extracting information from lst file....")
    print("")
    # open .osop.lst file
    with open(filename) as fp:

        for index, line in enumerate(fp):
            # decide which section the code is looking
            if line[:50].strip() == '':
                continue
            if line[:7].strip() == "NNODE":
                lst_section = "NNODE"
            if line[:7].strip() == "NFEED":
                lst_section = "NFEED"
            if line[:7].strip() == "NLINK":
                lst_section = "NLINK"
            if line[:7].strip() == "NFIXC":
                lst_section = "NFIXC"
            if line[:7].strip() == "NSTATV":
                lst_section = "NSTATV"
            if line[:7].strip() == "NMOTA":
                lst_section = "NMOTA"
            if line[:7].strip() == "NTRANS":
                lst_section = "NTRANS"
            if line[:7].strip() == "NMETER":
                lst_section = "NMETER"
            if line[8:12].strip() == "XRLS":
                lst_section = "XRLS"
            if line[:7].strip() == "NMETER":
                lst_section = "NMETER"
            if line[18:32].strip() == "LINE  SECTION":
                lst_section = "LINESECTION"
            if line[:7].strip() == "NBAND":
                lst_section = "NBAND"
            if line[11:17].strip() == "DBNAME":
                lst_section = "DBNAME"
            if line[:7].strip() == "INCSEC":
                lst_section = "INCSEC"
                ins_sec = int(line[8:14].strip()) # get current time steps
                ins_time = line[20:28].strip()  # get current time (day data not implemented)
            if line[:7].strip() == "TRAIN":
                lst_section = "TRAIN"
            if line[:14].strip() == "Run completed.":
                lst_section = ""

            # excute action
            lst_data_action(line,lst_section,ins_sec,ins_time,train_e,train_info,branch_lookup,u_branch_lookup)

            # print processing information
            if index  % (round(0.01*total_line)) == 0:
                finish_mark = int(index / (round(0.01*total_line))*1)
                print("{} % completed.".format(finish_mark))

# Action on the data list based on the section selection
def lst_data_action(line, lst_section, ins_sec, ins_time, train_e,train_info,branch_lookup,u_branch_lookup):
    if lst_section == "NNODE":
        #print(line.rstrip()) # remove training space
        return

    if lst_section == "NFEED":
        return
    
    if lst_section == "NLINK":  # branch ID vs branch Name lookup table
        if line[:7].strip() == "NLINK":
            return
        elif line[:7].strip()== "":
            return
        else:
            branch_lookup[int(line[:8].strip())] = line[8:14].strip()
            u_branch_lookup[line[8:14].strip()] = int(line[:8].strip())
    
    if lst_section == "NFIXC":
        return
    
    if lst_section == "NSTATV":
        return
    
    if lst_section == "NMOTA":
        return
    
    if lst_section == "NTRANS":
        return
    
    if lst_section == "NMETER":
        return
    
    if lst_section == "XRLS":
        return
    
    if lst_section == "NMETER":
        return
    
    if lst_section == "LINESECTION":
        return
    
    if lst_section == "NBAND":
        return
    
    if lst_section == "DBNAME": # add train electrical information (BHTPBANK list)
        if line[11:17].strip() == "DBNAME":
            return
        
        words = line.strip().split() # split the line into words based on space
        if len(words) == 4:
            train_info.append([int(words[0]),words[1]])
        else:
            train_info.append([int(words[0]),"NOT_USED"])      
    
    if lst_section == "INCSEC":
        return
    
    if lst_section == "TRAIN":  # processing train information by timestep
        if line[:7].strip() == "TRAIN":
            return
        else:
            # get related varible
            index = int(line[:7].strip())
            ins_vr = float(line[8:15].strip())
            ins_vi = float(line[15:23].strip())
            ins_va = math.sqrt(ins_vr**2 + ins_vi**2)
            ins_ir = float(line[27:34].strip())
            ins_ii = float(line[34:42].strip())
            ins_ia = math.sqrt(ins_ir**2 + ins_ii**2)
            ins_pr = ins_vr*ins_ir
            ins_pi = ins_vi*ins_ii
            ins_pa = math.sqrt(ins_pr**2 + ins_pi**2)
            
            dis_gone = float(line[123:131].strip())
            bran_num = int(line[57:63].strip())
            delta = float(line[63:70].strip())

            ins_speed = float(line[72:79].strip())
            av_speed = float(line[80:88].strip())
            te_used = float(line[90:99].strip())
            te_perc = float(line[103:109].strip())

##            train_e = ["VO_ID","T_STEP","TIME","V_Re","V_Im","V_T","I_Re","I_Im","I_T", \
##               "P_Re","P_Im","P_T","BRANCH","DELTA","TE/BE","PERC%","DIS_GONE", \
##               "INS_SPD","AV_SPD"]  # For Information Only
            train_e.append([index,ins_sec,ins_time, \
                            ins_vr,ins_vi,ins_va,ins_ir,ins_ii,ins_ia, \
                            ins_pr,ins_pi,ins_pa,bran_num,delta,te_used,te_perc, \
                            dis_gone,ins_speed,av_speed])
    
    if lst_section == "":
        return






    

# # programme running
# if __name__ == '__main__':
#     main()
# Check if the script is run as the main module
if __name__ == "__main__":
    # Add your debugging code here
    simname = "StraightLine1"  # Provide a simulation name or adjust as needed
    main_option = "4"  # Adjust as needed
    time_start = "0070000"  # Adjust as needed
    time_end = "0080000"  # Adjust as needed
    option_select = "1"  # Adjust as needed
    text_input = "BranchList"  # Adjust as needed
    low_v = None  # Adjust as needed
    high_v = None  # Adjust as needed
    time_step = None  # Adjust as needed

    # Call your main function with the provided parameters
    main(simname, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
