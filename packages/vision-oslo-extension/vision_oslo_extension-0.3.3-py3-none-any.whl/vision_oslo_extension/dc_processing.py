#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: 27/01/2023
# Last Modified: Sep/2023
#=================================================================
"""
This module was built to process DC result.
The following essential files are required:
- all d4 files output by extraction
- FeederList.txt

This module has been designed requiring some third party packages.

"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version
# V1.1 (Jieming Ye) - Update on user interface
# V1.2 (Jieming Ye) - Update main menu log + summary ready sheet for TRU Assessment
# V1.3 (Jieming Ye) - Add feature of branch information process
#                     including step extraction and RMS calculation
# V1.4 (Jieming Ye) - Add feature of feeder information process (to be rewrite)
#                     Fix bugs when maximum list is empty
# V1.5 (Jieming Ye) - For TRU assessment from list file
#                     Process feeder information automatically 
# V1.6 (Jieming Ye) - Fix bugs in RMS calculation. Add line 1063
#                     Empty the list before reassign the value and append.
#=================================================================
# Set Information Variable
__author__ = "Jieming ye"
__copyright__ = "Copyright 2023, Network Rail Design Delivery"
__credits__ = "Jieming Ye"
__version__ = "1.6"
__email__ = "jieming.ye@networkrail.co.uk"
__status__ = "under test"

# Default
#from ast import Continue
import sys
import os
import math
import csv

#from numpy import True_
#import copy

# Third Party
#import matplotlib.pyplot as plt
#import tkinter
#from tkinter import messagebox
#from PIL import Image
#import numpy as np 
#from subprocess import check_output 
#import panda 

def main():

    #User Interface - Welcome message:
    print("DC RMS Processing Tool")
    print("")
    print("Copyright: NRDD 2023")
    print("")

    print("This programme was developed to process DC simulation result")
    print("User Acceptance Test has NOT been carried out")
    print("Please contact support if unexpected exit happens")
    print("") 
 

    #define the file name and check if the file exist or not
    print("Please enter the simulation name:(awaiting input)")
    simname = input()

    main_menu_process(simname)

    

# main menu
def main_menu_process(simname):
    # Ask if the Grid data calcualtion is needed
    # user input selection
    print("\nPlease select from the list what you want to do:(awaiting input)")
    print("1: Process RMS current (1,4,5,30,60,120,180 min) and average power (30 min). (FeederList.txt is required)")
    print("2: Grid Calculation (GridAllocation.csv input file is required)")
    print("3: Option1 + Option2")
    print("4: Branch current process (.osop.lst is required)")
    print("5: Feeder current process for RTU assessment (.osop.lst is required) (same as Option 1)")

    option = input()
    # option check and prepare
    if option not in ["1","2","3","4","5"]:
        input("Invalid Selection. Press any key to exit the programme")
        sys.exit()   

    if option == "1":
        # check all d4 file exist. and return the supply point list
        feeder_list = d4_file_check("FeederList.txt",simname)      
        print("Pre-checking completed. Ready to GO!")

    if option == "2":
        # read the grid allocation csv
        grid_list = grid_allocation('GridAllocation.csv')
        print("")
        print("Pre-checking completed. Ready to GO!")

    if option == "3":
        feeder_list = d4_file_check("FeederList.txt",simname)
        grid_list = grid_allocation('GridAllocation.csv')
        print("")
        print("Pre-checking completed. Ready to GO!")

    if option == "4":
        filename = simname + ".osop.lst"
        if not os.path.isfile(filename):
            input("Please provide the essential file. Exiting...")
            sys.exit()
        else:
            print("List input file exist. Continue...")
        print("Pre-checking completed. Ready to GO!")
    
    if option == "5":
        filename = simname + ".osop.lst"
        if not os.path.isfile(filename):
            input("Please provide the essential file. Exiting...")
            sys.exit()
        else:
            print("List input file exist. Continue...")
        print("Pre-checking completed. Ready to GO!")

    # Processing start
    print("\nProcessing Initiated...")

    # Create Essential Data Set
    # result for RMS value
    RMS_1min_list = []
    RMS_4min_list = []
    RMS_5min_list = []
    RMS_30min_list = []
    RMS_60min_list = []
    RMS_120min_list = []
    RMS_180min_list = []

    ave_30min_P_list = []

    # grid summary
    grid_sum1 = [] # simple summary
    grid_sum2 = [] # detailed summary

    if option == "1" or option == "3":
        # Open d4 file one by one and excute the process
        for index, feeder in enumerate(feeder_list):

            print("Processing {}...".format(feeder))

            time = d4_file_process(simname,feeder,RMS_1min_list,RMS_4min_list,RMS_5min_list,RMS_30min_list, \
                RMS_60min_list,RMS_120min_list,RMS_180min_list,ave_30min_P_list)

        # writing summary to csv file    
        print('')
        print('Write summary to csv file...')
        sum_to_csv('1min_RMScurrent_sum',RMS_1min_list,simname,time,feeder_list)
        sum_to_csv('4min_RMScurrent_sum',RMS_4min_list,simname,time,feeder_list)     
        sum_to_csv('5min_RMScurrent_sum',RMS_5min_list,simname,time,feeder_list)
        sum_to_csv('30min_RMScurrent_sum',RMS_30min_list,simname,time,feeder_list)
        sum_to_csv('60min_RMScurrent_sum',RMS_60min_list,simname,time,feeder_list)
        sum_to_csv('120min_RMScurrent_sum',RMS_120min_list,simname,time,feeder_list)
        sum_to_csv('180min_RMScurrent_sum',RMS_180min_list,simname,time,feeder_list)
        sum_to_csv('30min_AVEpower_sum',ave_30min_P_list,simname,time,feeder_list)

        RTUsum_to_csv(simname,time,feeder_list,RMS_1min_list,RMS_4min_list,RMS_5min_list, \
            RMS_30min_list,RMS_60min_list,RMS_120min_list,RMS_180min_list,5)

        if option == '3':
            # process the grid calculation
            print('\nProcessing Grid Calculation...')
            grid_calculation(simname,time,grid_list,grid_sum1,grid_sum2)

    if option == '2':

        #selection = input()
        time = read_time(simname)

        # process the grid calculation
        print('\nProcessing Grid Calculation...')
        grid_calculation(simname,time,grid_list,grid_sum1,grid_sum2)
    
    if option == '4':
        branch_data_process(simname,filename)
    
    if option == '5':
        feeder_data_process(simname,filename,RMS_1min_list,RMS_4min_list,RMS_5min_list, \
            RMS_30min_list,RMS_60min_list,RMS_120min_list,RMS_180min_list,ave_30min_P_list)

        
    input("\nProcessing Completed. Press any key to close this window.")

# module to check d4 file exist or not  
def d4_file_check(filename,simname):
    print('')
    print("Pre-check: Have you provided the ""FeederList.txt"" file?")
    print("Checking...")

    if not os.path.isfile(filename):
        input("Please provide the essential file. Exiting...")
        sys.exit()
    else:
        print("FeederList input file exist. Continue...")

    print("Checking essential d4 files...")
    
    # reading the Feeder List file
    text_input = []
    with open(filename) as fbrlist:
        for index, line in enumerate(fbrlist):
            text_input.append(line[:50].strip())

    for items in text_input:
        name = simname + "_" + items + ".osop.d4"
    
        if not os.path.isfile(name): # if the d4 file exist
            input("Supply Point d4 file {} does not exist. Please double check.".format(name))
            sys.exit()

    return text_input

# process single d4 files
def d4_file_process(simname,feeder,RMS_1min_list,RMS_4min_list,RMS_5min_list, \
    RMS_30min_list,RMS_60min_list,RMS_120min_list,RMS_180min_list,ave_30min_P_list):
    time = []
    pow_real = []
    pow_imag =[]
    volt_abs = []
    volt_angle = []
    cur_abs = []
    cur_angle = []

    name = simname + "_" + feeder + ".osop.d4"
    # Open the bhtpbank and read data
    with open(name) as fp:
        for index1, line in enumerate(fp):
            # decide which section the code is looking            
            if line[:4].strip() == feeder:
                time_string = line[10:17].strip()
                time_format = time_convert(time_string)
                time.append(time_format)

                pow_real.append(line[18:26].strip())
                pow_imag.append(line[27:35].strip())
                volt_abs.append(line[36:43].strip())
                volt_angle.append(line[44:50].strip())
                cur_abs.append(line[51:59].strip())
                cur_angle.append(line[60:66].strip())

        d4_to_csv(simname,feeder,time,pow_real,pow_imag,volt_abs,volt_angle,cur_abs,cur_angle)
        
        #temp_list = []
        #rms_temp_list = [None]*len(time)
        #
        # # update the summary info list
        # for index2, i in enumerate(cur_abs):
        #     steps = int(60/5)
        #     if index2 >= steps:
        #         temp_list = cur_abs[index2-steps:index2]
        #         RMS_value = calculate_RMS(temp_list)
        #         rms_temp_list[index2] = RMS_value
        # RMS_1min_list.append(rms_temp_list)
        print("1 min current")
        RMS_current(60,5,cur_abs,RMS_1min_list,time)
        print("4 min current")
        RMS_current(240,5,cur_abs,RMS_4min_list,time)
        print("5 min current")
        RMS_current(300,5,cur_abs,RMS_5min_list,time)
        print("30 min current")
        RMS_current(1800,5,cur_abs,RMS_30min_list,time)
        print("60 min current")
        RMS_current(3600,5,cur_abs,RMS_60min_list,time)
        print("120 min current")
        RMS_current(7200,5,cur_abs,RMS_120min_list,time)
        print("180 min current")
        RMS_current(10800,5,cur_abs,RMS_180min_list,time)
        print("30 min power")
        AVE_power(1800,5,pow_real,ave_30min_P_list,time)
        print("")
        
    return time

# module to convert 7 digits time to time format 
def time_convert(time_string):
    
    #time_string = input()          
    day = int(time_string[:1])
    hour = int(time_string[1:3])
    minute = int(time_string[3:5])
    second = int(time_string[5:7])

    if not day == 0:
        day = day # to be updated to process info at a later stage

    time = str(hour) + ":" + str(minute) + ":" + str(second)        

    #debug purpose
    #print(seconds_int)
    # Return the second integer number as same used in the list file           
    return time

# write d4 file to csv with proper calculation
def d4_to_csv(simname,feeder,time,pow_real,pow_imag,volt_abs,volt_angle,cur_abs,cur_angle):
    with open(simname+"_"+feeder+'.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1
        writer.writerow(['Summary of Result for Feeder OSLO ID: '+feeder])
        row = row + 1
        writer.writerow('')
        row = row + 1

        writer.writerow(['OSLO ID','Type','Time','Active Power (MW)','Reactive Power (kVAr)', \
            'Voltage (kV)','Angle (degree)','Current (A)','Angle (degree)','','Current Square', \
                'I-RMS 1-min (A)','I-RMS 4-min (A)','I-RMS 5-min (A)','I-RMS 30-min (A)', \
                    'I-RMS 60-min (A)','I-RMS 120-min (A)','I-RMS 180-min (A)','','P-AVE 30 min (MW)'])
        row = row + 1

        last_row = str(len(time)+5)

        equ1 = '=offset(C5,match(L5,L6:L'+ last_row + ',0),0)'
        equ2 = '=offset(C5,match(M5,M6:M'+ last_row + ',0),0)'
        equ3 = '=offset(C5,match(N5,N6:N'+ last_row + ',0),0)'
        equ4 = '=offset(C5,match(O5,O6:O'+ last_row + ',0),0)'
        equ5 = '=offset(C5,match(P5,P6:P'+ last_row + ',0),0)'
        equ6 = '=offset(C5,match(Q5,Q6:Q'+ last_row + ',0),0)'
        equ7 = '=offset(C5,match(R5,R6:R'+ last_row + ',0),0)'
        equ8 = '=offset(C5,match(T5,T6:T'+ last_row + ',0),0)'

        writer.writerow(['','','','','','','','','','Time','',equ1,equ2,equ3,equ4,equ5,equ6,equ7,'',equ8])
        row = row + 1

        equ1 = '=max(L6:L'+ last_row +')'
        equ2 = '=max(M6:M'+ last_row +')'
        equ3 = '=max(N6:N'+ last_row +')'
        equ4 = '=max(O6:O'+ last_row +')'
        equ5 = '=max(P6:P'+ last_row +')'
        equ6 = '=max(Q6:Q'+ last_row +')'
        equ7 = '=max(R6:R'+ last_row +')'
        equ8 = '=max(T6:T'+ last_row +')'

        writer.writerow(['','','','','','','','','','Maximum','',equ1,equ2,equ3,equ4,equ5,equ6,equ7,'',equ8])
        row = row + 1

        for index,items in enumerate(time):
            equ1 = '=H'+str(row)+'^2' # square of current
            equ2 = '=sqrt(average(K'+str(row)+':K'+str(int(row-60/5)+1) +'))' # 1 min RMS current
            equ3 = '=sqrt(average(K'+str(row)+':K'+str(int(row-240/5)+1) +'))' # 4 min RMS current
            equ4 = '=sqrt(average(K'+str(row)+':K'+str(int(row-300/5)+1) +'))' # 5 min RMS current
            equ5 = '=sqrt(average(K'+str(row)+':K'+str(int(row-1800/5)+1) +'))' # 30 min RMS current
            equ6 = '=sqrt(average(K'+str(row)+':K'+str(int(row-3600/5)+1) +'))' # 60 min RMS current
            equ7 = '=sqrt(average(K'+str(row)+':K'+str(int(row-7200/5)+1) +'))' # 120 min RMS current
            equ8 = '=sqrt(average(K'+str(row)+':K'+str(int(row-10800/5)+1) +'))' # 180 min RMS current

            equ9 = '=average(D'+str(row)+':D'+str(int(row-1800/5)+1) +')' # 30 min average power

            if index < int(60/5)-1: # down to 1 min data not available
                data = [feeder,'SP',items,pow_real[index],pow_imag[index],volt_abs[index],volt_angle[index], \
                    cur_abs[index],cur_angle[index],'',equ1]
                writer.writerow(data)
                row = row + 1

            elif index < int(240/5)-1: # down to 4 min data not available
                data = [feeder,'SP',items,pow_real[index],pow_imag[index],volt_abs[index],volt_angle[index], \
                    cur_abs[index],cur_angle[index],'',equ1,equ2]
                writer.writerow(data)
                row = row + 1

            elif index < int(300/5)-1: # down to 5 min data not available
                data = [feeder,'SP',items,pow_real[index],pow_imag[index],volt_abs[index],volt_angle[index], \
                    cur_abs[index],cur_angle[index],'',equ1,equ2,equ3]
                writer.writerow(data)
                row = row + 1

            elif index < int(1800/5)-1: # down to 30 min data not available
                data = [feeder,'SP',items,pow_real[index],pow_imag[index],volt_abs[index],volt_angle[index], \
                    cur_abs[index],cur_angle[index],'',equ1,equ2,equ3,equ4]
                writer.writerow(data)
                row = row + 1

            elif index < int(3600/5)-1: # down to 60 min data not available
                data = [feeder,'SP',items,pow_real[index],pow_imag[index],volt_abs[index],volt_angle[index], \
                    cur_abs[index],cur_angle[index],'',equ1,equ2,equ3,equ4,equ5,'','','','',equ9]
                writer.writerow(data)
                row = row + 1

            elif index < int(7200/5)-1: # down to 120 min data not available
                data = [feeder,'SP',items,pow_real[index],pow_imag[index],volt_abs[index],volt_angle[index], \
                    cur_abs[index],cur_angle[index],'',equ1,equ2,equ3,equ4,equ5,equ6,'','','',equ9]
                writer.writerow(data)
                row = row + 1
            
            elif index < int(10800/5)-1: # down to 180 min data not available
                data = [feeder,'SP',items,pow_real[index],pow_imag[index],volt_abs[index],volt_angle[index], \
                    cur_abs[index],cur_angle[index],'',equ1,equ2,equ3,equ4,equ5,equ6,equ7,'','',equ9]
                writer.writerow(data)
                row = row + 1

            else: # got all time info
                data = [feeder,'SP',items,pow_real[index],pow_imag[index],volt_abs[index],volt_angle[index], \
                    cur_abs[index],cur_angle[index],'',equ1,equ2,equ3,equ4,equ5,equ6,equ7,equ8,'',equ9]
                writer.writerow(data)
                row = row + 1
                       
        writer.writerow('')
        row = row + 1

    return

# calculate RMS value of a list
def calculate_RMS(temp_list):
    total = 0
    number_list = map(float,temp_list)
    for i in number_list:
        total = total + i*i # square of a value
    RMS_value = math.sqrt(total/len(temp_list))

    return RMS_value

# calculate ave value of a list
def calculate_AVE(temp_list):
    total = 0
    number_list = map(float,temp_list)
    for i in number_list:
        total = total + i # square of a value
    
    AVE_value = total/len(temp_list)

    return AVE_value

# write list summary information to csv file
def sum_to_csv(title,data_list,simname,time,feeder_list):

    # manipulate data list so that ready for csv file
    final_list = [None] * (len(time)+3)
    final_list[0] = [None]
    final_list[0].append('OSLO ID')
    final_list[1] = [None]
    final_list[1].append('Maximum')
    final_list[2] = [None]
    final_list[2].append('time of max')

    for index in range(len(data_list)):
        final_list[0].append(feeder_list[index]) # feeder OSLO ID on top
        count = 0
        temp_list = []
        for d in data_list[index]:
            if d == None:
                count=count+1
            else:
                temp_list.append(d)

        if temp_list == []:
            max_value = 0
            final_list[1].append(None)
            final_list[2].append(None)
        else:
            max_value = max(temp_list)
            t_index = temp_list.index(max_value) + count
            final_list[1].append(max_value)
            final_list[2].append(time[t_index])

    for index1, i in enumerate(time):
        final_list[index1+3] = [None]
        final_list[index1+3].append(i) # Time on the first column
        for index2, line in enumerate(data_list):
            if len(line) > index:  # in case there is a empty list           
                final_list[index1+3].append(line[index1]) # data for the line
            else:
                final_list[index1+3].append(None)

    # write summary info to CSV file
    with open(simname+'_'+ title +'.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1

        for final_line in final_list:
            writer.writerow(final_line)
            row = row + 1

    return

# write a summary ready for RTU assessment
def RTUsum_to_csv(simname,time,feeder_list,RMS_1min_list,RMS_4min_list,RMS_5min_list, \
    RMS_30min_list,RMS_60min_list,RMS_120min_list,RMS_180min_list,steps):
    
    # manipulate data list so that ready for csv file
    final_list = [None] * (len(feeder_list)+2)
    final_list[0] = [None,'Time Windows','1-min max','4-min max','5-min max','30-min max', \
        '60-min max','120-min max','180-min max','End time of Max']

    final_list[1] = [None,'OSLO ID','1','4','5','30','60','120','180','1','4','5','30','60','120','180']


    for index, f in enumerate(feeder_list):
        final_list[index+2] = [None]
        final_list[index+2].append(f)
        
        if RMS_1min_list[index] == []: # if the data does not exist
            final_list[index+2] = [None,f,0,0,0,0,0,0,0,None,None,None,None,None,None,None]

        else:
            # find the max value of each RMS list
            write_RMS(RMS_1min_list,final_list,index,60,steps,2)
            write_RMS(RMS_4min_list,final_list,index,240,steps,2)
            write_RMS(RMS_5min_list,final_list,index,300,steps,2)
            write_RMS(RMS_30min_list,final_list,index,1800,steps,2)
            write_RMS(RMS_60min_list,final_list,index,3600,steps,2)
            write_RMS(RMS_120min_list,final_list,index,7200,steps,2)
            write_RMS(RMS_180min_list,final_list,index,10800,steps,2) 

            # find the index of max and return time
            write_RMS_time(RMS_1min_list,final_list,index,time,steps,2,0)
            write_RMS_time(RMS_4min_list,final_list,index,time,steps,2,1)
            write_RMS_time(RMS_5min_list,final_list,index,time,steps,2,2)
            write_RMS_time(RMS_30min_list,final_list,index,time,steps,2,3)
            write_RMS_time(RMS_60min_list,final_list,index,time,steps,2,4)
            write_RMS_time(RMS_120min_list,final_list,index,time,steps,2,5)
            write_RMS_time(RMS_180min_list,final_list,index,time,steps,2,6)

    # write summary info to CSV file
    with open(simname+'_RMSCurrent_Sum.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1

        for final_line in final_list:
            writer.writerow(final_line)
            row = row + 1

    return

# regulate 1
def write_RMS(result_list,final_list,index,time,steps,shift):
    empty_row = int(time/steps)-1
    if len(result_list[0]) < empty_row:
        final_list[index+shift].append(None)
    else:
        final_list[index+shift].append(max(result_list[index][empty_row:]))
    return

# regulate 2
def write_RMS_time(result_list,final_list,index1,time,steps,shift,cshift):
    if final_list[index1+2][shift+cshift] == None:
        time_happen = None
    else:
        time_happen = time[result_list[index1].index(final_list[index1+2][shift+cshift])]    
    final_list[index1+2].append(time_happen)
    return
    
# calculate RMS list
def RMS_current(time_sec,steps,cur_abs,RMS_list,time):

    temp_list = []
    rms_temp_list = [None]*len(time)

    # update the summary info list
    for index2, i in enumerate(cur_abs):
        iteration = int(time_sec/steps)-1
        if index2 >= iteration:
            temp_list = cur_abs[index2-iteration:index2+1]
            RMS_value = calculate_RMS(temp_list)
            rms_temp_list[index2] = RMS_value
    RMS_list.append(rms_temp_list)

# calculate average power list
def AVE_power(time_sec,steps,cur_abs,ave_list,time):

    temp_list = []
    ave_temp_list = [None]*len(time)

    # update the summary info list
    for index2, i in enumerate(cur_abs):
        iteration = int(time_sec/steps)-1
        if index2 >= iteration:
            temp_list = cur_abs[index2-iteration:index2+1]
            RMS_value = calculate_AVE(temp_list)
            ave_temp_list[index2] = RMS_value
    ave_list.append(ave_temp_list)

# calculate grid average power
def Grid_AVE_power(time_sec,steps,instant_info,time):

    temp_list = []
    total_list = []
    ave_temp_list = [None]*len(time)
    # get the total list
    for data in instant_info:
        total_list.append(data[-1])

    # update the summary info list
    for index2, i in enumerate(time):
        iteration = int(time_sec/steps)-1 # because python index start from 0
        if index2 >= iteration:
            temp_list = total_list[index2-iteration:index2+1]
            RMS_value = calculate_AVE(temp_list)
            ave_temp_list[index2] = RMS_value

    return ave_temp_list

# define the file to read the file
def read_time(simname):
    time = []
    filename = simname + '_30min_AVEpower_sum.csv'
    print("Pre-check: checking {} ....".format(filename))
    if not os.path.isfile(filename):
        input("Please selection option 3. Exiting...")
        sys.exit()

    file = open(filename,'r')
    data = list(csv.reader(file,delimiter= ','))
    file.close()

    for index, row in enumerate(data):
        if row == []: continue

        if index <= 2: continue #jump three lines
        else:
            time.append(row[1])

    return time

# read allcation csv file and return the list
def grid_allocation(name):
    print("")
    print("Checking input files...")
    if not os.path.isfile(name):
        input("Please provide the GridAllocation.csv. Exiting...")
        sys.exit()        

    grid_list = []
    id = 0
    file = open(name,'r')
    data = list(csv.reader(file,delimiter= ','))
    file.close()

    for index, row in enumerate(data):
        if index == 0:
            continue
        if index == 1:
            grid_list.append([row[2],row[1]])
        else:
            flag = True
            for index1, row1 in enumerate(grid_list):
                if row[2] == row1[0]:
                    id = index1
                    flag = False

            if flag == True:
                grid_list.append([row[2],row[1]])
            else:
                grid_list[id].append(row[1])            

    return grid_list

# grid calculation module
def grid_calculation(simname,time,grid_list,grid_sum1,grid_sum2):

    for grid in grid_list: # each grid is a grid with associated OSLO id
        sub_total = 0
        instant_info = []
        calcu_info = []
        sum_info0 = ['Substation'] # substation name
        sum_info1 = ['OSLO ID'] # OSLO ID
        sum_info2 = ['Time of Maximum'] # index (time) maximum number of each sub
        sum_info3 = ['Maximum Value for This Sub'] # maximum number of each sub
        
        # process information
        for index,items in enumerate(grid): # for each substation for this grid
            if index == 0:
                for t in time:
                    instant_info.append([t]) # write down time in the first column
                continue
            
            resultname = simname+'_'+items+'.csv'
            if not os.path.isfile(resultname):
                print("Warning: {} result file does not exist! Ignored!".format(items))
            else:
                sub_total = sub_total + 1
                sum_info1.append(items)
                
                file = open(resultname,'r')
                data = list(csv.reader(file,delimiter= ','))
                file.close()

                info_row = 0
                value_list = []
                # if it is an empty file
                if data[5] == []:
                    for t in time:
                        value_list.append(0) # relavent MW power list
                        instant_info[info_row].append(0) # read the relavent MW power in to main list
                        info_row = info_row + 1
                else:
                    for info in data:
                        if info == []: continue
                        if info[0] == items:
                            value_list.append(float(info[3])) # relavent MW power list
                            instant_info[info_row].append(info[3]) # read the relavent MW power in to main list
                            info_row = info_row + 1
                
                # if value_list == []:
                #     max_value = 0 # find the maximum value
                #     sum_info2.append("00:00:00")
                #     sum_info3.append(max_value)
                # else:
                max_value = max(value_list) # find the maximum value
                t_index = value_list.index(max_value) # find the maximum time index
                sum_info2.append(time[t_index])
                sum_info3.append(max_value)
        
        # sum the list
        if sub_total == 0:
            print("Warning: No substation identified for {}".format(grid[0]))

        if sub_total == 1:
            for i in range(len(time)):
                instant_info[i].append(float(instant_info[i][1]))
            
            summary_process(sum_info1,sum_info2,sum_info3,time,instant_info,grid_sum1,grid_sum2,grid,simname)
            sum_info1.append('Total_instant')
            sum_info1.append('Total_30 min')
            
        if sub_total > 1:            
            # calculate the instant total value
            for i in range(len(time)):
                sum_list = map(float,instant_info[i][0-sub_total:])
                instant_info[i].append(sum(sum_list))
            
            summary_process(sum_info1,sum_info2,sum_info3,time,instant_info,grid_sum1,grid_sum2,grid,simname)
            sum_info1.append('Total_instant')
            sum_info1.append('Total_30 min')          

        # each grid information summary
        if sub_total > 0:
            with open(simname+'_'+ grid[0] +'.csv','w',newline='') as csvfile:
                row = 0
                writer = csv.writer(csvfile) # create the csv writer
                writer.writerow(sum_info1)
                writer.writerow(sum_info2)
                writer.writerow(sum_info3)
                
                for lines in instant_info: writer.writerow(lines)
   
    # gird 30 min summary
    with open(simname+'_30min_GRID_Summary.csv','w',newline='') as csvfile:
        row = 0
        writer = csv.writer(csvfile) # create the csv writer

        writer.writerow(['Summary of HV Grid 30 min Average Power'])
        writer.writerow(['Grid Name','Time','Maximum Power (MW)','','', \
            'Grid Name','Time','Power (MW)','Substation','Power(MW)','Contribution (%)'])
      
        for index_csv, lines in enumerate(grid_sum2):
            equ = '=J'+str(index_csv+3)+'/H'+ str(index_csv+3) + '*100'
            if index_csv < len(grid_sum1):
                writer.writerow(grid_sum1[index_csv]+ ['',''] +lines+[equ])       
            else:
                writer.writerow(['','','','','']+lines+[equ])
                     
    return

# define the grid information summary process:
def summary_process(sum_info1,sum_info2,sum_info3,time,instant_info,grid_sum1,grid_sum2,grid,simname):

    filename = simname + '_30min_AVEpower_sum.csv'

    file = open(filename,'r')
    data = list(csv.reader(file,delimiter= ','))
    file.close()

    sum_info2.append('TBC')
    sum_info3.append('TBC')
    
    calcu_info = Grid_AVE_power(1800,5,instant_info,time)

    # find the max and save info
    p_max_list = []
    n_count = 0
    for value in calcu_info:
        if value == None: 
            n_count = n_count+1
            continue
        else: p_max_list.append(value)
    
    max_power = max(p_max_list)
    t_index = p_max_list.index(max_power)

    sum_info2.append(time[t_index+n_count])
    sum_info3.append(max_power)

    for i in range(len(time)):
        instant_info[i].append(calcu_info[i])
    
    # write summary information in sum
    for index3, subs in enumerate(sum_info1):

        if index3 == 0:
            grid_sum1.append([grid[0],time[t_index+n_count],max_power])
            
        else:
            # loop data list
            for col, id in enumerate(data[0]):
                if id == subs: column_index = col

            # 3 addtional lines above time
            grid_sum2.append([grid[0],time[t_index+n_count],max_power,subs,data[t_index+n_count+3][column_index]])

    return

# option 4 main sub function for data extraction
def branch_data_process(simname,filename):

    print("\nPlease select from the following options:(awaiting input)")
    print("1: All branch step output extraction")
    print("2: All branch rolling RMS current")
    print("3: All branch Maximum rolling RMS current summary")
    print("4: All option 1-3")
    print("5: Customised branch step output extraction (BranchNodeList.txt is required)")
    print("6: Customised branch rolling RMS current (BranchNodeList.txt is required)")
    print("7: Customised branch Maximum rolling RMS current summary (BranchNodeList.txt is required)")
    print("Option 5-7 is under development and should NOT be selected!")

    option1 = input()
    # option check and prepare
    if option1 not in ["1","2","3","4"]:
        input("Invalid Selection. Press any key to exit the programme")
        sys.exit() 

    if option1 in ["2","3"]:
        print("\nPlease input the time window in seconds (0 - 86400) (awaiting input): ")
        second = int(input())
        if second < 0 or second > 86400:
            input("Invalid input. Press any key to exit the programme")
            sys.exit() 


    branch_list = [] # initialise branch list
    sim_time = [] # Time list for reading
    step_branch_output = [] # step branch output information (2D list)
    step_branch_sum_c = [] # total current for each time step (2D list)
    branch_rms_list = [] # branch rms list 
    branch_rms_max = [] # bracnh RMS maximum summary list
    
    # get all branches in the model
    section_flag = False # judge if N-Link section is reached

    print('\nInitialising...')
    with open(filename) as fp:
        total_line = sum(1 for line in enumerate(fp)) # get the total line number

    with open(filename) as fp:
        print('\nReading Branch Information...')
        for index, line in enumerate(fp):            
            if line[:7].strip() == '':
                continue
            if line[:7].strip() == 'NLINK':
                section_flag = True
                continue

            if line[:7].strip() == 'NFIXC':
                section_flag = False
                break
            
            if section_flag == True:
                branch_temp = line[10:14].strip()
                branch_list.append(branch_temp) # Save branches in a list file
                step_branch_output.append([branch_temp])
                step_branch_sum_c.append([branch_temp])
    
    branch_read_flag = False
    time_count = 0 # time counter
    branch_count = 0 # branch counter
    
    print('\nProcess branch information...')
    with open(filename) as fp:
        for index, line in enumerate(fp):
            # flag judgement
            if line[:7].strip() == 'INCSEC':
                time_count = time_count + 1
                temp_time = line[20:22].strip()+":"+line[23:25].strip()+":"+line[26:28].strip()
                sim_time.append(temp_time)
                branch_read_flag = True
                continue
            if line[:7].strip() == 'TRAIN':
                branch_count = 0
                branch_read_flag = False
            
            # write down information
            if branch_read_flag == True:
                if line[76:82].strip() == '':
                    continue

                if line[:7].strip() == '':
                    branch_count = branch_count + 1
                    c_start_real = float(line[85:95].strip())
                    c_start_imag = float(line[95:105].strip())
                    c_end_real = float(line[110:120].strip())
                    c_end_imag = float(line[120:130].strip())

                    c_start_total = math.sqrt(math.pow(c_start_real,2)+math.pow(c_start_imag,2))
                    c_end_total = math.sqrt(math.pow(c_end_real,2)+math.pow(c_end_imag,2))

                    temp_line = [temp_time,c_start_real,c_start_imag,c_end_real,c_end_imag]
                    step_branch_output[branch_count-1].append(temp_line)

                    temp_line = [c_start_total,c_end_total]
                    step_branch_sum_c[branch_count-1].append(temp_line)
                else:
                    continue

            if index  % (round(0.01*total_line)) == 0:
                finish_mark = int(index / (round(0.01*total_line))*1)
                print("{} % completed.".format(finish_mark))

    if option1 == "1":
        print('\nSaving branch step output summary...')
        branch_step_csv_out(simname,sim_time,branch_list,step_branch_sum_c)
    
    if option1 == "2":
        print("\nProcessing RMS calculation...")
        branch_list_RMS_process(simname,sim_time,branch_list,step_branch_sum_c,second,5,branch_rms_list,branch_rms_max)
        branch_RMS_csv_out(simname,sim_time,branch_list,branch_rms_list,second)
    
    if option1 == "3":
        print("\nProcessing RMS calculation...")
        branch_list_RMS_process(simname,sim_time,branch_list,step_branch_sum_c,second,5,branch_rms_list,branch_rms_max)
        branch_RMS_sum_csv_out(simname,sim_time,branch_list,branch_rms_max,second)


    return

# Write branch step output information to csv file
def branch_step_csv_out(simname,sim_time,branch_list,step_branch_sum_c):
    # manipulate data list so that ready for csv file
    final_list = [['OSLO Branch Step Output']] # first line info
    final_list.append(['Time','Branch Start Node: BranchID/S, Branch End Node: BranchID/E']) # sencond line
    final_list.append(['hh:mm:ss']) # third line

    for br in branch_list:
        final_list[2].append(br+'/S')
        final_list[2].append(br+'/E')
    
    for index, time in enumerate(sim_time):
        newline = [time]
        for info in step_branch_sum_c:
            newline.append(info[index+1][0]) # start node current
            newline.append(info[index+1][1]) # end node current
        
        final_list.append(newline)

    # write summary info to CSV file
    with open(simname+'_branch_step_sum.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1

        for index, final_line in enumerate(final_list):
            writer.writerow(final_line)
            row = row + 1
        
    print('\nBranch Step Output Summary Completed.')

    return

# branch RMS output information to csv file
def branch_RMS_csv_out(simname,sim_time,branch_list,branch_rms_list,second):
    final_list = [['OSLO Branch RMS Output','Rolling '+str(second)+' seconds']] # first line info
    final_list.append(['Time','Branch Start Node: BranchID/S, Branch End Node: BranchID/E']) # sencond line
    final_list.append(['hh:mm:ss']) # third line

    for br in branch_list: # second row
        final_list[2].append(br+'/S')
        final_list[2].append(br+'/E')
    
    for index, time in enumerate(sim_time):
        newline = [time]
        for info in branch_rms_list:
            newline.append(info[index]) # 

        final_list.append(newline)

    # write summary info to CSV file
    with open(simname+'_branch_'+str(second)+'_rms_sum.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1
        
        for index, final_line in enumerate(final_list):
            writer.writerow(final_line)
            row = row + 1
        
    print('\nBranch RMS Output Summary Completed.')

    return

# branch RMS summary output information to csv file
def branch_RMS_sum_csv_out(simname,sim_time,branch_list,branch_rms_max,second):
    final_list = [['OSLO Branch RMS Output','Rolling '+str(second)+' seconds']] # first line info
    final_list.append(['Branch','Node','Start Time (hh:mm:ss)','End Time (hh:mm:ss)','Maximum Value(A)']) # sencond line

    for br in branch_list: # second row
        final_list.append([br,br+'/S'])
        final_list.append([br,br+'/E'])
    
    for index, info in enumerate(branch_rms_max):
        final_list[index+2].append(info[0]) # Time/max
        final_list[index+2].append(info[1]) # Time/max
        final_list[index+2].append(info[2]) # Time/max

    # write summary info to CSV file
    with open(simname+'_branch_'+str(second)+'_rms_sum_max.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1
        
        for index, final_line in enumerate(final_list):
            writer.writerow(final_line)
            row = row + 1
        
    print('\nBranch RMS Output Summary Completed.')

    return

# process branch list RMS calculation
def branch_list_RMS_process(simname,sim_time,branch_list,step_branch_sum_c,second,steps,branch_rms_list,branch_rms_max):
    total_number = len(branch_list)

    iteration = int(second/steps)

    for index, br in enumerate(step_branch_sum_c):
        print("Processing {}.....({}/{})....".format(br[0],index+1,total_number))
        rms_temp_list = [None]*len(sim_time)
        
        temp_step_list_s = []
        temp_step_list_e = []        
        for index1, t in enumerate(sim_time):
            temp_step_list_s.append(br[index1+1][0]) # start node current
            temp_step_list_e.append(br[index1+1][1]) # end node current
        
        temp_list = []
        temp_max_list = [] # ready for max calculation
        temp_time_list = [] # ready for time match
        for index2, t in enumerate(sim_time):
            if index2 + 1 >= iteration:
                temp_list = temp_step_list_s[index2+1-iteration:index2+1]
                RMS_value = calculate_RMS(temp_list)
                temp_time_list.append(t)
                temp_max_list.append(RMS_value)
                rms_temp_list[index2] = RMS_value
        branch_rms_list.append(rms_temp_list) # start node RMS
        if temp_max_list:
            temp_max = max(temp_max_list) # find the maximum
            time_of_max_s = temp_time_list[temp_max_list.index(temp_max)-iteration+1]
            time_of_max_e = temp_time_list[temp_max_list.index(temp_max)]
            branch_rms_max.append([time_of_max_s,time_of_max_e,temp_max])

        rms_temp_list = [None]*len(sim_time)
        temp_list = []
        temp_max_list = [] # ready for max calculation
        temp_time_list = [] # ready for time match
        for index2, t in enumerate(sim_time):
            if index2 + 1 >= iteration:
                temp_list = temp_step_list_e[index2+1-iteration:index2+1]
                RMS_value = calculate_RMS(temp_list)
                temp_time_list.append(t)
                temp_max_list.append(RMS_value)
                rms_temp_list[index2] = RMS_value
        branch_rms_list.append(rms_temp_list) # End node RMS
        if temp_max_list:
            temp_max = max(temp_max_list) # find the maximum
            time_of_max_s = temp_time_list[temp_max_list.index(temp_max)-iteration+1]
            time_of_max_e = temp_time_list[temp_max_list.index(temp_max)]
            branch_rms_max.append([time_of_max_s,time_of_max_e,temp_max])
    
    return

# option 5 main sub function for data extraction (to be rewrite)
def feeder_data_process(simname,filename,RMS_1min_list,RMS_4min_list,RMS_5min_list, \
    RMS_30min_list,RMS_60min_list,RMS_120min_list,RMS_180min_list,ave_30min_P_list):

    print("This programme will only perform the default calculation for TRU assessment for DC modelling")
    print("A further customsed programme is to be devleoped")

    print("\nPlease select from the following options:(awaiting input)")
    print("1: Feeder current step output extraction")
    print("2: TRU Summary")

    option1 = input()
    # option check and prepare
    if option1 not in ["1","2"]:
        input("Invalid Selection. Press any key to exit the programme")
        sys.exit() 

    feeder_list = [] # initialise branch list
    feeder_link_id_list = [] #linked branch id
    sim_time = [] # Time list for reading
    step_branch_output = [] # step branch output information (2D list)
    step_branch_sum_c = [] # total current for each time step (2D list)
    feeder_rms_list = [] # branch rms list 
    feeder_rms_max = [] # bracnh RMS maximum summary list
    feeder_branch_s_link = [] # feeder link with branch end
    feeder_branch_e_link = [] # feeder link with branch end
    feeder_current = [] # feeder current list

    time = []
    pow_real = []
    pow_imag =[]
    volt_abs = []
    volt_angle = []
    cur_abs = []
    cur_angle = []
    
    # get all feeders in the model
    section_flag = False # judge if N-Feed section is reached
    section_flag_1 = False # judeg if Nlink section is reached
    print('\nInitialising...')
    with open(filename) as fp:
        total_line = sum(1 for line in enumerate(fp)) # get the total line number

    with open(filename) as fp:
        print('\nReading Feeder Information...')
        for index, line in enumerate(fp):            
            if line[:7].strip() == '':
                continue
            if line[:7].strip() == 'NFEED':
                section_flag = True
                continue

            if line[:7].strip() == 'NLINK':
                for i in range(len(feeder_list)):
                    feeder_branch_s_link.append([])
                    feeder_branch_e_link.append([])
                section_flag = False
                section_flag_1 = True
                continue
                
            if line[:7].strip() == 'NFIXC':
                section_flag_1 = False
                break
            
            if section_flag == True:
                feeder_temp = line[15:20].strip()
                feeder_list.append(feeder_temp) # Save feeder in a list file
                id_temp = line[8:13].strip()
                feeder_link_id_list.append(id_temp) # save feeder id in a list file

            if section_flag_1 == True:
                temp_node_s = line[65:70].strip()
                temp_node_e = line[73:78].strip()
                temp_branch = line[10:14].strip()
                for index, id in enumerate(feeder_link_id_list):
                    if temp_node_s == id:
                        feeder_branch_s_link[index].append(temp_branch)   # branch start connection to feeder
                    if temp_node_e == id:
                        feeder_branch_e_link[index].append(temp_branch)   # branch end connection to feeder


    feeder_read_flag = False
    time_count = 0 # time counter
    branch_count = 0 # branch counter
    
    print('\nReading feeder step output information...')
    with open(filename) as fp:
        for index, line in enumerate(fp):
            # flag judgement
            if line[:7].strip() == 'INCSEC':
                time_count = time_count + 1
                temp_time = line[20:22].strip()+":"+line[23:25].strip()+":"+line[26:28].strip()
                sim_time.append(temp_time)
                feeder_read_flag = True
                if time_count > 1: # copy last time step information and clear the temp
                    feeder_current.append(temp_feeder_sum)
                    # feeder current = [[F1_t1,F2+t1,F3_t1],[F1_t2,F2_t2,F3_t2],[F1_t3,F2_t3,F3_t3]]
                temp_feeder_sum = [0] * len(feeder_list)
                continue
            if line[:7].strip() == 'TRAIN':
                branch_count = 0
                feeder_read_flag = False
            
            if line[:7].strip() == 'Run com': # when reaching the last line
                feeder_current.append(temp_feeder_sum)
            
            # write down information
            if feeder_read_flag == True:
                if line[76:82].strip() == '':
                    continue

                if line[:7].strip() == '':
                    branch_count = branch_count + 1
                    temp = line[77:81].strip()
                    c_start_real = float(line[85:95].strip())
                    c_start_imag = float(line[95:105].strip())
                    c_end_real = float(line[110:120].strip())
                    c_end_imag = float(line[120:130].strip())

                    if c_start_real >= 0:
                        c_start_total = math.sqrt(math.pow(c_start_real,2)+math.pow(c_start_imag,2))
                    else:
                        c_start_total = -(math.sqrt(math.pow(c_start_real,2)+math.pow(c_start_imag,2)))
                    
                    if c_end_real >= 0:
                        c_end_total = math.sqrt(math.pow(c_end_real,2)+math.pow(c_end_imag,2))
                    else:
                        c_end_total = -(math.sqrt(math.pow(c_end_real,2)+math.pow(c_end_imag,2)))

                    # temp_line = [temp_time,c_start_real,c_start_imag,c_end_real,c_end_imag]
                    # step_branch_output[branch_count-1].append(temp_line)

                    # temp_line = [c_start_total,c_end_total]
                    # step_branch_sum_c[branch_count-1].append(temp_line)

                    # check if this branche start node is part of the feeder current or not
                    # for the branch start it's plus, for the branch ends it's minus.
                    for index1, link_id  in enumerate(feeder_branch_s_link):
                        if temp in link_id:
                            temp_feeder_sum[index1] = temp_feeder_sum[index1] + (c_start_total)
                            break
                    for index1, link_id  in enumerate(feeder_branch_e_link):
                        if temp in link_id:
                            temp_feeder_sum[index1] = temp_feeder_sum[index1] + (-c_end_total)
                            break                  
                else:
                    continue


            if index  % (round(0.01*total_line)) == 0:
                finish_mark = int(index / (round(0.01*total_line))*1)
                print("{} % completed.".format(finish_mark))
        
    if option1 == "1":
        print('\nSaving feeder step output summary...')
        feeder_step_csv_out(simname,sim_time,feeder_current,feeder_list)
    
    if option1 == "2":
        print("\nProcessing RMS calculation...")
        feeder_list_RMS_process(simname,sim_time,feeder_current,feeder_list,5,RMS_1min_list, \
            RMS_4min_list,RMS_5min_list,RMS_30min_list,RMS_60min_list,RMS_120min_list,RMS_180min_list,ave_30min_P_list)
        


    return

# feeder step output summary
def feeder_step_csv_out(simname,sim_time,feeder_current,feeder_list):
    # manipulate data list so that ready for csv file
    final_list = [['OSLO Feeder Step Output']] # first line info
    final_list.append(['Time','Feeder ID']) # sencond line
    final_list.append(['hh:mm:ss']) # third line

    for fe in feeder_list:
        final_list[2].append(fe)
    
    for index, time in enumerate(sim_time):
        newline = [time]
        for index1, fe in enumerate(feeder_list):
            newline.append(feeder_current[index][index1]) # start node current       
        
        final_list.append(newline)

    # write summary info to CSV file
    with open(simname+'_feeder_step_sum.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile) # create the csv writer
        lock = 0
        row = 1

        for index, final_line in enumerate(final_list):
            writer.writerow(final_line)
            row = row + 1
        
    print('\nFeeder Step Output Summary Completed.')


    return

# feeder RMS process and output
def feeder_list_RMS_process(simname,sim_time,feeder_current,feeder_list,step,RMS_1min_list, \
    RMS_4min_list,RMS_5min_list,RMS_30min_list,RMS_60min_list,RMS_120min_list,RMS_180min_list,ave_30min_P_list):

    
    for x, feeder in enumerate(feeder_list):
        print("Processing {}...".format(feeder))
        cur_abs = []
        for y, time in enumerate(sim_time):
            cur_abs.append(feeder_current[y][x]) #create a cur_bas list [d1,d2,d3....] per feeder
            
        RMS_current(60,step,cur_abs,RMS_1min_list,sim_time)        
        RMS_current(240,step,cur_abs,RMS_4min_list,sim_time)        
        RMS_current(300,step,cur_abs,RMS_5min_list,sim_time)        
        RMS_current(1800,step,cur_abs,RMS_30min_list,sim_time)        
        RMS_current(3600,step,cur_abs,RMS_60min_list,sim_time)       
        RMS_current(7200,step,cur_abs,RMS_120min_list,sim_time)       
        RMS_current(10800,step,cur_abs,RMS_180min_list,sim_time)
    
    # writing summary to csv file    
    print('')
    print('Write summary to csv file...')
    sum_to_csv('1min_RMScurrent_sum',RMS_1min_list,simname,sim_time,feeder_list)
    sum_to_csv('4min_RMScurrent_sum',RMS_4min_list,simname,sim_time,feeder_list)     
    sum_to_csv('5min_RMScurrent_sum',RMS_5min_list,simname,sim_time,feeder_list)
    sum_to_csv('30min_RMScurrent_sum',RMS_30min_list,simname,sim_time,feeder_list)
    sum_to_csv('60min_RMScurrent_sum',RMS_60min_list,simname,sim_time,feeder_list)
    sum_to_csv('120min_RMScurrent_sum',RMS_120min_list,simname,sim_time,feeder_list)
    sum_to_csv('180min_RMScurrent_sum',RMS_180min_list,simname,sim_time,feeder_list)

    RTUsum_to_csv(simname,sim_time,feeder_list,RMS_1min_list,RMS_4min_list,RMS_5min_list, \
        RMS_30min_list,RMS_60min_list,RMS_120min_list,RMS_180min_list,step)

    return

# copy from online to calculate averages without calling numpy
# since numpy is not supported by default
def calculate_averages(list_2d):
    cell_total = list()
    row_totals = dict()
    column_totals = dict()
    for row_idx, row in enumerate(list_2d):
        for cell_idx, cell in enumerate(row):
            # is cell a number?
            if type(cell) in [int, float, complex]:
                cell_total.append(cell)                
                if row_idx in row_totals:
                    row_totals[row_idx].append(cell)
                else:
                    row_totals[row_idx] = [cell]
                if cell_idx in column_totals:
                    column_totals[cell_idx].append(cell)
                else:
                    column_totals[cell_idx] = [cell]
    per_row_avg = [sum(row_totals[row_idx]) / len(row_totals[row_idx]) for row_idx in row_totals]
    per_col_avg = [sum(column_totals[col_idx]) / len(column_totals[col_idx]) for col_idx in column_totals]
    row_avg = sum(per_row_avg) / len(per_row_avg)
    col_avg = sum(per_col_avg) / len(per_col_avg)
    return {'cell_average': sum(cell_total) / len(cell_total),
            'per_row_average': per_row_avg,
            'per_column_average': per_col_avg,
            'row_average': row_avg,
            'column_average': col_avg}

# programme running
if __name__ == '__main__':
    main()

