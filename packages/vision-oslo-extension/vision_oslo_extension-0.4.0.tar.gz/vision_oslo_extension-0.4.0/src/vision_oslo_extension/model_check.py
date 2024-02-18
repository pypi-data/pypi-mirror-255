#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye , Jacky Lai
# Created on: April 2022
# Last Update: March 2023
#=================================================================
"""
This module was built summarise the electrical connections from the list file
Pre-requisite:
- Name.lst.txt (lst file auto generated following run)


This module has been specifically designed to exclude all external packages so that
the code is compatible with Network Rail default Python package.
"""
#=================================================================
# VERSION CONTROL
# Versions of Model Check tool of which this was derived from
# V1.0 (Jieming Ye) - Initial Version from old connection report v2.0

#=================================================================
# Set Information Variable
__author__ = "Jieming Ye"
__copyright__ = "Copyright 2023, Network Rail Design Delivery"
__credits__ = "Jieming Ye"
__version__ = "1.0"
__email__ = "jieming.ye@networkrail.co.uk"
__status__ = "in testing"

import sys
import os
import csv
import math
import copy
#import numpy as np # not supported by Network Rail Corp

#from subprocess import check_output # not support by Network Rail Corp

#import panda # not supported by Network Rail Corp

def main(simname, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):

    #User Interface - Welcome message:
    print("Model Process....")
    print("")
    print("Copyright: NRDD 2023")
    print("")

    print("This programme was developed to check a working model and generate a connection report")
    print("Software error message should be cleared before using this programme")
    print("Please contact support if unexpected exit happens")
    print("")    

    #define the file name and check if the file exist or not
    # get simulation name name from input
    print("The simulation name is {}.".format(simname))
    # simname = input()
    filename = simname + ".lst.txt"
    current_path = os.getcwd()
    file_path = os.path.join(current_path,filename)

    if not os.path.isfile(file_path): # if the lst.txt file exist
       print("Default list file {} does not exist. Please go back to VISION and click run first. This should auto generate the required file.".format(filename))
       return False

    main_menu(simname, filename, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)

    #print("\nProcessing Completed. Back to GUI")

# main function to be called
def main_menu(simname, filename, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
    # user input selection
    # print("\nPlease select from the list what you want to do:(awaiting input)")
    # print("1: Model verficiation report.")
    # print("2: Connection Report")
    # print("3: TBC - Development in progress")

    option = main_option

    #print(option) # for debug

    if option not in ["0","1","2","3"]:
        print("Error: Contact Support. Error in model_check.py --> main_menu")
        return False
    
    #define essential variables
    section_flag = ""   # Identify the section
    section_id = 0  # section Id by default
    #train_id = 0   # Train ID
    #change_no = 0  # change number

    # define essential list to be updated
    branch_id = 0
    branch_list = [] # branch basic info
    branch_line_list = []   # branch info with route section id
    trans_list = [] # transformer basic info added v1.2
    trans_list_a = [] #transformer list for intermediate steps added v1.2
    branch_list_t = [] # branch list with transformers added as branches added v1.2
    sp_list = []    # list to store supply point information
    sp_connection_sum = [] # list to process supply point connection information , added v1.2
    
    errorwarning_list = []  # error and warning list

    #train_e =[]

    #umean_info = [] #Essential information to be used as for umeanuseful calculation

    lst_data_read(filename,branch_list,branch_line_list,sp_list,trans_list,trans_list_a,branch_list_t,errorwarning_list)
    


    if option == "1":
        summary_check_option(simname,branch_list,branch_line_list,branch_list_t,sp_list,trans_list,errorwarning_list,option_select)

    if option == "2":
        sp_connect = connection_info_built(simname,branch_line_list,sp_list,option_select)

    return sp_connect
    

# option 1 to check the summary
def summary_check_option(simname,branch_list,branch_line_list,branch_list_t,sp_list,trans_list,errorwarning_list,option_select):
    node_connection = []  # list to process node connection information

    # branch checking process
    # v1.2 branch_list_t added as input added transformers as branches to branch_line_list
    print("\nBranch Summary Cross Checking...")
    check_branch_info(branch_list,branch_line_list,branch_list_t)

    # Node Name Listing
    print("\nNode Connection Listing...")
    node_connection = check_node_info(branch_line_list)

    # added in v2.0 to give node connection summary 
    print("\nNode Map Creating")
    node_connection_map = node_track_id_connection(branch_list_t)

    # sort the data
    sorted_branch_line = sorted(branch_line_list, key=lambda row:row[0], reverse =False)
    sorted_node_connection = sorted(node_connection, key=lambda row:row[0], reverse =False)
    sorted_node_connection_map = sorted(node_connection_map, key=lambda row:row[0], reverse =False)
    sorted_branch = sorted(branch_list_t, key=lambda row:row[0], reverse =False) #test branch_list_t
    sorted_sp = sorted(sp_list, key=lambda row:row[0], reverse =False)
    sorted_trans = sorted(trans_list, key=lambda row:row[0], reverse =False)


    # with open(simname + '_summary.txt', 'w') as fw:
    #     fw.write("BranchID,Branch_Name,Start_Node,End_Node,Start_Node_Dis," \
    #              "End_Node_Dis,Branch_Resistance,Branch_Reactance,Branch_Susceptance,Comment," \
    #              "Line_Section_ID,Line_Section_Start_Dis,Line_Section_End_Dis," \
    #              "Branch_Start_Location(Relative_to_Line_Origin),Line_Length,Direction\n")
        
    #     for items in sorted_branch_line:
    #         string_line = map(str,items) # string all item
    #         result_line = ",".join(string_line) # join item removing brackets/quotes
    #         fw.write("%s\n" % result_line) # print out
    
    if option_select == "1":

        with open(simname + '_branch_detail.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile) # create the csv writer
            lock = 0
            row = 1
            writer.writerow(["BranchID","Branch_Name","Start_Node","End_Node","Start_Node_Dis", \
                            "End_Node_Dis","Branch_Resistance","Branch_Reactance","Branch_Susceptance","Comment", \
                            "VISION_Line_Section_ID","VISION_LS_Start_Dis","VISION_LS_End_Dis", \
                            "Branch_Start_Location(Relative_to_Line_Origin)","VISION_Line_Length","Direction"])
            row = row + 1
            writer.writerows(sorted_branch_line)

        # with open(simname + '_node_connection.txt', 'w') as fw:
        #     fw.write("No,Node_ID,Connection,Associated_Line_Section\n")

        #     for items in sorted_node_connection:
        #         string_line = map(str,items) # string all item
        #         result_line = ",".join(string_line) # join item removing brackets/quotes
        #         fw.write("%s\n" % result_line) # print out

        max_column = 0
        for items in sorted_node_connection:
            if len(items) > max_column:
                max_column = len(items)
        max_column = int((max_column-2)/2)

        header = ["No","Node_ID"]
        for i in range(0,max_column):
            header.append("Connection")
            header.append("VISION_Line_Section")
        
        with open(simname + '_node_connection.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile) # create the csv writer
            lock = 0
            row = 1
            writer.writerow(header)
            row = row + 1
            writer.writerows(sorted_node_connection)
        
        #Added in v2.0
        #Output Node connection map txt
        # with open(simname + '_node_map.txt', 'w') as fw:

        #     for node in node_connection_map:
        #         string_line = str(node_connection_map[node])
        #         string_line2 = str(node)
        #         result_line = string_line2 + "-->" + "," + string_line
        #         fw.write("%s\n" % result_line) # print out
        

        with open(simname + '_node_map.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile) # create the csv writer
            lock = 0
            row = 1
            writer.writerow(["Node ID","Branch ID","Branch Start/End","Connected Node ID"])
            row = row + 1
            for node in node_connection_map:
                linked = node_connection_map[node]
                for string_line in linked:
                    string_line.insert(0,node)
                    writer.writerow(string_line)
                    row = row + 1

            #writer.writerows(sorted_node_connection)
        

        # with open(simname + '_branch.txt', 'w') as fw:
        #     fw.write("BranchID,Branch_Name,Start_Node,End_Node,Start_Node_Dis," \
        #              "End_Node_Dis,Branch_Resistance,Branch_Reactance,Branch_Susceptance,Comment\n")

        #     for items in sorted_branch:
        #         string_line = map(str,items) # string all item
        #         result_line = ",".join(string_line) # join item removing brackets/quotes
        #         fw.write("%s\n" % result_line) # print out
        
        with open(simname + '_branch.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile) # create the csv writer
            lock = 0
            row = 1
            writer.writerow(["BranchID","Branch_Name","Start_Node","End_Node","Start_Node_Dis", \
                            "End_Node_Dis","Branch_Resistance","Branch_Reactance","Branch_Susceptance","Comment"])
            row = row + 1
            writer.writerows(sorted_branch)
        

        # with open(simname + '_supply_point.txt', 'w') as fw:
        #     fw.write("No,SP_Name,SP_Node_ID,No-load_Volt(kV),Phase_Angle(deg)," \
        #         "Output_Resistance,Output_Reactance,Comment\n")

        #     for items in sorted_sp:
        #         string_line = map(str,items) # string all item
        #         result_line = ",".join(string_line) # join item removing brackets/quotes
        #         fw.write("%s\n" % result_line) # print out
        
        with open(simname + '_supply_point.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile) # create the csv writer
            lock = 0
            row = 1
            writer.writerow(["No","SP_Name","SP_Node_ID","No-load_Volt(kV)","Phase_Angle(deg)", \
                            "Output_Resistance","Output_Reactance","Comment"])
            row = row + 1
            writer.writerows(sorted_sp)
                
        #Added in v1.2
        #Create Transformer List
        # with open(simname + '_transformer.txt', 'w') as fw:
        #     fw.write("No,Trans_Name,Type,In_Node,In_Voltage,Out_Node,Out_Voltage," \
        #         "Output_Resistance,Output_Reactance\n")

        #     for items in sorted_trans:
        #         string_line = map(str,items) # string all item
        #         result_line = ",".join(string_line) # join item removing brackets/quotes
        #         fw.write("%s\n" % result_line) # print out
        
        with open(simname + '_transformer.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile) # create the csv writer
            lock = 0
            row = 1
            writer.writerow(["No","Trans_Name","Type","In_Node","In_Voltage","Out_Node","Out_Voltage", \
                            "Output_Resistance","Output_Reactance"])
            row = row + 1
            writer.writerows(sorted_trans)

        
        with open(simname + '_error_warning.txt', 'w') as fw:
            fw.write("Error and Warning Summary\n")

            for items in errorwarning_list:
                fw.write("%s\n" % items) # print out

# option 2 to genearte various connection map
def connection_info_built(simname,branch_line_list,sp_list,option_select):
    connection_sum = []  # list to process node connection information
    

    # Node connection summary added in V1.1
    # Transformers now added as branches to branch_line_list in V1.2
    #treat transformers as branches to create connection summary
    print("\nConnection Summary...")
    connection_sum = node_connect(branch_line_list)

    # Supply Points Node connection added in V1.2
    print("\nSupply Points Connection Summary...")
    supply_connection_sum = supply_node_connect(sp_list,connection_sum) 

    # sort the data
    sorted_sp_c = sorted(supply_connection_sum, key=lambda row:row[0], reverse =False)
    sorted_connection_sum = sorted(connection_sum, key=lambda row:row[0], reverse =False)

    # with open(simname + '_connection_sum.txt', 'w') as fw:
    #     fw.write("No,Node_ID\n")

    #     for items in sorted_connection_sum:
    #         string_line = map(str,items) # string all item
    #         result_line = ",".join(string_line) # join item removing brackets/quotes
    #         fw.write("%s\n" % result_line) # print out
    if option_select == "1":

        with open(simname + '_branches_connection_summary.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile) # create the csv writer
            lock = 0
            row = 1
            writer.writerow(["No","Node_ID"])
            row = row + 1
            writer.writerows(sorted_connection_sum)
        
        #Added in v1.2
        #Create Supply point list with summary of its connected nodes
        # with open(simname + '_supply_point_connection.txt', 'w') as fw:
        #     fw.write("No,SP_Name,SP_Node_ID,Connected_Node_ID\n")

        #     for items in sorted_sp_c:
        #         string_line = map(str,items) # string all item
        #         result_line = ",".join(string_line) # join item removing brackets/quotes
        #         fw.write("%s\n" % result_line) # print out
        
        with open(simname + '_supply_point_connection_summary.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile) # create the csv writer
            lock = 0
            row = 1
            writer.writerow(["No","SP_Name","SP_Node_ID","Connected_Node_ID"])
            row = row + 1
            writer.writerows(sorted_sp_c)
    
    return sorted_sp_c


# processing the list data:
def lst_data_read(filename,branch_list,branch_line_list,sp_list,trans_list,trans_list_a,branch_list_t,errorwarning_list):
    #define essential variables
    section_flag = ""   # Identify the section
    section_id = 0  # section Id by default
    # open text file to get the total line information (best way i can think of)
    # although it require reading the file twice
    print("Analysing LST file....")
    with open(filename) as fp:
        total_line = sum(1 for line in enumerate(fp))

    print("Extracting information from LST file....")
    print("")
    # open lst file
    with open(filename) as fp:

        for index, line in enumerate(fp):
            if line[:4].strip() == "***":
                errorwarning_list.append(line)
                continue
            if line[:4]== "    ":
                continue

            # Get Header Info
            section_flag = line[:6].strip()    # Get the line header (assume 6 digits should be enough)
            if section_flag == "*ELECT":
                section_id = 1
                continue
            elif section_flag == "*BRANC":
                section_id = 2
                continue
            elif section_flag == "*SUPPL":
                section_id = 3
                continue
            elif section_flag == "*TRANS":
                section_id = 5
                continue
            elif section_flag == "*LINES":
                section_id = 4
                continue
            elif section_flag == "*END O":
                section_id = 0


            # excute action
            lst_data_action(line,section_id,branch_list,branch_line_list,sp_list,trans_list,trans_list_a,branch_list_t)

            # print processing information
            if index  % (round(0.01*total_line)) == 0:
                finish_mark = int(index / (round(0.01*total_line))*1)
                print("{} % completed.".format(finish_mark))
    
    print("100 % completed.")
    print("LST Processing Completed. Data Processing...")


# Action on the CIF based on the Header selection
def lst_data_action(line,section_id,branch_list,branch_line_list,sp_list,trans_list,trans_list_a,branch_list_t):
    if section_id == 0: # no information process required
        #print(line.rstrip()) # remove training space
        return

    # if section_id == "TI": # TIPLOC insert record
    #     return
    
    # if section_id == "TA":  # TIPLOC amend record
    #     return

    # if section_id == "TD": # TIPLOC delete record
    #     return
    
    if section_id == 1: # Electrical traction data section
        return
    
    if section_id == 2: #  branch list
        
        info1 = line[:5].strip()  # Branch Name
        info2 = line[5:10].strip()  # Branch Start Node ID
        info3 = line[10:15].strip()  # Branch End Node ID
        info4 = line[17:25].strip()  # Branch Start Distance (always 0)
        info5 = line[25:33].strip()  # Branch End Distance / Branch Length
        info6 = line[33:41].strip()  # Branch Resistance
        info7 = line[41:49].strip()  # Branch Reactance
        info8 = line[49:57].strip()  # Branch Susceptance
        info9 = line[59:80].strip()  # Comment
        
        branch_list.append([len(branch_list)+1,info1,info2,info3,info4,info5,info6,info7,info8,info9])      #create branch list
        
        branch_list_t.append([len(branch_list_t)+1,info1,info2,info3,info4,info5,info6,info7,info8,info9])  #create branch list where transformers will be added as branches 
        
        #print(train_info[train_id-1])
        
        return
    
    if section_id == 3: #  Supply Points List
        
        info1 = line[:5].strip()  # Suppy Point Name
        info2 = line[5:10].strip()  # OSLO node energised
        info3 = line[10:20].strip()  # No Load Voltage
        info4 = line[20:30].strip()  # Phase angle in degree
        info5 = line[30:40].strip()  # Output resistance
        info6 = line[40:50].strip()  # Output reactance
        info7 = line[50:90].strip()  # Comment
        

        sp_list.append([len(sp_list)+1,info1,info2,info3,info4,info5,info6,info7])

        return
    
    if section_id == 4: #  Lines/branches cross reference table
        
        info1 = line[:10].strip()  # Route Section ID
        info2 = line[10:25].strip()  # Route section start location
        info3 = line[25:40].strip()  # Route Section end location
        info4 = line[40:50].strip()  # Branch included
        info5 = line[50:65].strip()  # Branch_Start_Location(Relative_to_Line_Origin)
        info6 = line[65:80].strip()  # Branch / lines same direction

        if info6 == "0":
            info6 = "Stub_Fed"
        elif info6 == "+1":
            info6 = "Branch/Line_Same_Direction"
        elif info6 == "-1":
            info6 = "Branch/Line_Oppo_Direction"

        for lists in branch_list:
            if lists[1] == info4:
                branch_line_list.append([lists[0],lists[1],lists[2],lists[3],lists[4],lists[5],lists[6],\
                    lists[7],lists[8],lists[9],info1,info2,info3,info5,abs(int(info3)-int(info2)),info6])

        return

#added transformer reading ability v1.2
    
    if section_id == 5: #  Transformer list
        
        info1 = line[:5].strip()  # Transformer Name
        info2 = line[5:6].strip() # Type of Transformer
        #print("T info",info2)

        if info2 == "A" or info2 =="N": #Determine if this is the first line (transformer information are listed in 2 lines)
            #print("first",info1)       #For development 
            info3 = line[7:12].strip()  #Primary Winding Node
            info4 = line[12:21].strip() #Primary Winding Voltage 
            info5 = line[21:26].strip() #Secondary Winding Node
            info6 = line[26:36].strip() #Secondary Winding Voltage
                        
            trans_list_a.append([len(trans_list_a)+1,info1,info2,info3,info4,info5,info6]) # write to trans_list_a

        else:                           #This will be in the second line
            #print("second",info1)      #For development
            info8 = line[8:15].strip()  #Transformer Resistance
            info9 = line[15:25].strip() #Transformer Reactance

            for lists in trans_list_a:  #Match first line info with name of second line
                if lists[1] == info1:   
                    trans_list.append([lists[0],lists[1],lists[2],lists[3],lists[4],lists[5],lists[6],\
                        info8, info9])  #join first line and second line information
                                        #write to trans_list output for transformers summary txt

                    branch_list_t.append([len(branch_list_t)+1,lists[1],lists[3],lists[5],0,1,info8,info9,0,"Transformer"])
                    #add transformer information to branch list t 
        return        
        
        #print(train_info[train_id-1])  #For development
    
    
    if section_id == "ZZ":
        print("CIF file reading completed")
        return
    
    
    if section_id == "":
        return

# module to check branch information
# module to add all branches to branch_line_list ; it is the list used for cheking node connection summary
# in v1.2 changes made to include transformer by using branch list t
def check_branch_info(branch_list,branch_line_list,branch_list_t):
    for lists in branch_list:
        branch = lists[1]
        if any(branch in sublist for sublist in branch_line_list): # if the branch name exist in the final branch line list
            continue
        else:
            branch_line_list.append([lists[0],lists[1],lists[2],lists[3],lists[4],lists[5],\
                        lists[6],lists[7],lists[8],"","","","","","","Cables/ATF"])

    #added in v1.2
    #insert transformer as branches to branch_line_list
    for lists in branch_list_t:
        branch = lists[1]
        if any(branch in sublist for sublist in branch_line_list): # if the branch name exist in the final branch line list
            continue
        else:
            branch_line_list.append([lists[0],lists[1],lists[2],lists[3],lists[4],lists[5],\
                        lists[6],lists[7],lists[8],"","","","","","","Transformer branch"])
            
    return

# module to check node connection
def check_node_info(branch_list):
    
    node_connection = []
    if len(node_connection) == 0:
        node_connection = [[1,branch_list[0][2],branch_list[0][3],branch_list[0][10]]]

    for list1 in branch_list: # check all start node one by one
        new_flag = True
        for index, list2 in enumerate(node_connection):
            if list1[2] == list2[1]:
                new_flag = False
                if list1[3] in list2:
                    break
                else:
                    list2.append(list1[3])
                    list2.append(list1[10])
                    node_connection[index] = list2
                    break
        if new_flag == True:
            list2 = [len(node_connection)+1,list1[2],list1[3],list1[10]]
            node_connection.append(list2)

    for list1 in branch_list: # check all end node one by one
        new_flag = True
        for index, list2 in enumerate(node_connection):
            if list1[3] == list2[1]:
                new_flag = False
                if list1[2] in list2:
                    break
                else:
                    list2.append(list1[2])
                    list2.append(list1[10])
                    node_connection[index] = list2
                    break
        if new_flag == True:
            list2 = [len(node_connection)+1,list1[3],list1[2],list1[10]]
            node_connection.append(list2)

    return node_connection         

# module to check node connection summary
def node_connect(branch_list):
    
    connection_sum = []
    total_line = len(branch_list)
    if len(connection_sum) == 0:
        connection_sum = [[1,branch_list[0][2],branch_list[0][3]]]

    for index, list1 in enumerate(branch_list): # check all branches
        new_flag = True
       
        for list2 in connection_sum:
            next_flag = True
            while next_flag:
                origin_len = len(list2)
                for list3 in branch_list:
                    if list3[2] in list2:
                        if list3[3] not in list2:
                            list2.append(list3[3])
                    else:
                        if list3[3] in list2:
                            if list3[2] not in list2:
                                list2.append(list3[2])
                new_len = len(list2)
                if origin_len == new_len: next_flag = False
        
        if any(list1[2] in sublist for sublist in connection_sum) or \
            any(list1[3] in sublist for sublist in connection_sum):
        # if any([list1[2],list1[3]] in sublist for sublist in connection_sum):
            new_flag = False

        if new_flag == True:
            list2 = [len(connection_sum)+1,list1[2],list1[3]]
            connection_sum.append(list2)
        
        # print processing information
        if round(0.01*total_line) != 0:
            if index  % (round(0.01*total_line)) == 0:
                finish_mark = int((index+1) / total_line *100)
                print("{} % completed.".format(finish_mark))

    return connection_sum

# Module to check Supply point node connections
# added v1.2
def supply_node_connect(supply_list,con_sum):   #take inputs from supply point list and connection summary
    
    sp_connection_sum = []
    total_line = len(supply_list)
    cs_len = len(con_sum)                       #the number of lines in connection summary (number of individual feeding sections)
    print("Node groups len",cs_len)             #for development
    cs2_len = len(supply_list)                  #the number of lines in supply point list
    print("Supply len", cs2_len)                #for development

    i=0
    
    while i < cs2_len:                                      #check for each supply point
        list2 = [i+1, supply_list[i][1],supply_list[i][2]]  #read supply point name and energised node id

        for list1 in con_sum:                               #read for all individual feeding sections
            if list2[2] in list1:                           #check if the feeding section contains the energised node for the supply point

                cs3_len = len(list1)
                j=1
                
                while j <cs3_len:                           #append all nodes of the feeding section against the supply point
                    if list2[2] != list1[j]:                        
                        list2.append(list1[j])


                        
                    j +=1
                    
                    
                #list2.append(list1)

        sp_connection_sum.append(list2)                     #append list 2 to output array

        i +=1

        #print processing informaiton
        finish_mark = int((i/cs2_len)*100)              
        print("{} % completed.".format(finish_mark))
        
    return sp_connection_sum
 

# module to check user input time and covert to seconds for processing
def time_input_process(time_string):
    seconds_int = 0
    hour = int(time_string[:2])
    minute = int(time_string[3:5])
    second = int(time_string[6:8])
    
    if 0 <= hour <= 24:
        seconds_int += hour*60*60
    else:
        input("Invalid HOUR input. Press any key to exit the programme")
        sys.exit()

    if 0 <= minute <= 60:
        seconds_int += minute*60
    else:
        input("Invalid MINUTE input. Press any key to exit the programme")
        sys.exit()

    if 0 <= second <= 60:
        seconds_int += second
    else:
        input("Invalid SECOND input. Press any key to exit the programme")
        sys.exit()

    #debug purpose
    #print(seconds_int)
    # Return the second integer number as same used in the list file           
    return seconds_int

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

#new function in v2.0 for node connection summary 
def node_track_id_connection(branch_list):
    nodes = set() #create a set storing all node names
    for branch in branch_list:
        nodes.add(branch[2])
        nodes.add(branch[3])

    connections = {} #create a dictionary to store connections from all nodes
    for node in nodes:
        connections[node] = [] #create a blank entry for all nodes

    for branch in branch_list: #go through all the branches and added the branch names and connected nodes to the dictionary 
        connections[branch[2]].append([branch[1],"S",branch[3]]) 
        connections[branch[3]].append([branch[1],"E",branch[2]])

    return connections



#new function 



# programme running
if __name__ == "__main__":
    # Add your debugging code here
    simname = "StraightLine1"  # Provide a simulation name or adjust as needed
    main_option = "2"  # Adjust as needed
    time_start = "0070000"  # Adjust as needed
    time_end = "0080000"  # Adjust as needed
    option_select = "1"  # Adjust as needed
    text_input = "BranchList"  # Adjust as needed
    low_v = None  # Adjust as needed
    high_v = None  # Adjust as needed
    time_step = None  # Adjust as needed

    # Call your main function with the provided parameters
    main(simname, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)

