

#import tkinter as tk
import os
import pkg_resources
import shutil
import sys


class SharedVariables:
    # this class will store all shared varibles
    sim_variable = None
    main_option = None
    
    # varible to be updated following version upgrade:
    # Replace 'your_package_name' with the actual name of your package
    package_name = 'vision_oslo_extension'
    support_name = 'support'
    
class Local_Shared:
    # this class will store all local shared varibles
    option_select = None
    time_start = None
    time_end = None
    text_input = None
    low_threshold = None
    high_threshold = None
    time_step = None

class SharedMethods:

    def copy_example_files(filename):
        distribution = pkg_resources.get_distribution(SharedVariables.package_name)
        # Get the path to the package
        #package_path = distribution.location + "\\" + SharedVariables.package_name
        package_path_root = os.path.join(distribution.location, SharedVariables.package_name)

        package_path = os.path.join(package_path_root, SharedVariables.support_name)

        # Get the absolute path of the file in the package location
        file_in_package = os.path.join(package_path, filename)


        current_path = os.getcwd() # get current path

        check_file = os.path.join(current_path, filename)

        if os.path.exists(check_file):
            print(f"File '{filename}' already exists in the current working directory. Skipping copy...")
        else:
            # Copy the file to the current working directory
            shutil.copy(file_in_package,current_path)
            print(f"File '{filename}' copied to the current working directory. Config as required...")



    def check_existing_file(filename):
        print("Checking File {}...".format(filename))
        current_path = os.getcwd() # get current path
        # print(current)
        file_path = os.path.join(current_path,filename) # join the file path
        # print(file_path)
        if not os.path.isfile(file_path): # if the oof file exist
            print("ERROR: Required file {} does not exist. Exiting...".format(filename))
            return False
        return True
    

    def folder_file_check(subfolder,filename):
        print("Checking File {} in {}...".format(filename,subfolder))
        current_path = os.getcwd() # get current path

        # Create the complete folder path
        folder_path = os.path.join(current_path, subfolder)
        
        # Check if the folder exists
        if not os.path.exists(folder_path):
            print("ERROR: Required folder {} does not exist. Exiting...".format(subfolder))
            return False
        
        # file path
        file_path = os.path.join(folder_path,filename) # join the file path
        # print(file_path)
        if not os.path.isfile(file_path):
            print("ERROR: Required file {} does not exist at {}. Exiting...".format(filename,subfolder))
            return False
        return True



    def check_oofresult_file(simname):
        # if getattr(sys, 'frozen', False):
        # # PyInstaller creates a temp folder and stores path in _MEIPASS
        #     application_path = sys._MEIPASS
        # else:
        #     # Regular Python execution
        #     application_path = os.path.dirname(os.path.abspath(__file__))

        # resultfile = simname + ".oof"
        # file_path = os.path.join(application_path,resultfile)
        # print(file_path)
        resultfile = simname + ".oof"
        if not SharedMethods.check_existing_file(resultfile):
            return False

        return True
        

    def osop_running(cmdline):
        # Replace 'your_package_name' with the actual name of your package
        # package_name = 'vision_oslo_extension'
        # Get the distribution object for your package
        distribution = pkg_resources.get_distribution(SharedVariables.package_name)
        # Get the path to the package
        package_path = distribution.location + "\\" + SharedVariables.package_name
        #print(f"The path to '{package_name}' is: {package_path}")

        with open("batch_run.bat","w") as fba:
            fba.writelines("@echo off\n")
            fba.writelines("set PATH=%PATH%;" + package_path + "\n")
            fba.writelines("@echo on\n")
            fba.writelines(cmdline)
        os.system("batch_run.bat")

    # rename files
    def file_rename(old_name,new_name):
        try:
            os.rename(old_name,new_name)
            print("File {} successfully created. Processing Continue...".format(new_name))
        except FileExistsError:
            os.remove(new_name)
            os.rename(old_name,new_name)
            print("File {} successfully replaced. Processing Continue...".format(new_name))
        except FileNotFoundError:
            print("\nFile {} FAILED as the OSOP extraction fail. Check Input...".format(new_name))

    # module to check 7 digit user input time
    def time_input_process(time_string,option_back):
        #option_back = 1: return string
        #option_back = 2: return seconds
        #time_string = input()
        

        if not len(time_string) == 7:
            print("Invalid data input. Press reenter the 7 digit time.")
            return False
            # print("OR enter 0 to exit the programme.")
            # time_string = input()
            # if time_string == "0":
            #     return False
            # else:
            #     time_input_process(time_string)

        seconds_int = 0        
        day = int(time_string[:1])
        hour = int(time_string[1:3])
        minute = int(time_string[3:5])
        second = int(time_string[5:7])

        if not 0 <= day <= 9:
            print("Invalid Day input. Press reenter the 7 digit time.")
            return False
            # print("OR enter 0 to exit the programme.")
            # time_string = input()
            # if time_string == "0":
            #     return False
            # else:
            #     time_input_process(time_string)
                
        if 0 <= hour <= 24:
            seconds_int += hour*60*60
        else:
            print("Invalid Hour input. Press reenter the 7 digit time.")
            return False
            # print("OR enter 0 to exit the programme.")
            # time_string = input()
            # if time_string == "0":
            #     return False
            # else:
            #     time_input_process(time_string)
                
        if 0 <= minute <= 60:
            seconds_int += minute*60
        else:
            print("Invalid Minute input. Press reenter the 7 digit time.")
            return False
            # print("OR enter 0 to exit the programme.")
            # time_string = input()
            # if time_string == "0":
            #     return False
            # else:
            #     time_input_process(time_string)
                
        if 0 <= second <= 60:
            seconds_int += second
        else:
            print("Invalid Second input. Press reenter the 7 digit time.")
            return False
            # print("OR enter 0 to exit the programme.")
            # time_string = input()
            # if time_string == "0":
            #     return False
            # else:
            #     time_input_process(time_string)

        if option_back == 1:
            return time_string
        else:
            return seconds_int
        #debug purpose
        #print(seconds_int)
        # Return the second integer number as same used in the list file           
        # return time_string
    
    # def time_input_process_sec(time_string):
    #     seconds_int = 0
    #     hour = int(time_string[:2])
    #     minute = int(time_string[3:5])
    #     second = int(time_string[6:8])
        
    #     if 0 <= hour <= 24:
    #         seconds_int += hour*60*60
    #     else:
    #         input("Invalid HOUR input. Press any key to exit the programme")
    #         sys.exit()

    #     if 0 <= minute <= 60:
    #         seconds_int += minute*60
    #     else:
    #         input("Invalid MINUTE input. Press any key to exit the programme")
    #         sys.exit()

    #     if 0 <= second <= 60:
    #         seconds_int += second
    #     else:
    #         input("Invalid SECOND input. Press any key to exit the programme")
    #         sys.exit()

    #     #debug purpose
    #     #print(seconds_int)
    #     # Return the second integer number as same used in the list file           
    #     return seconds_int
    
    # copy from online to calculate averages without calling numpy

    def check_lst_file(simname): # check the exist of proper list file of the model
        cmdline = "osop " + simname
        filename = simname + ".osop.lst"
        opcname = simname + ".opc"

        with open(opcname,"w") as fopc:
            fopc.writelines("LIST INPUT FILE\n")
    
        # Create batch file for list command and run the batch file
        # and define the lst file name to process the information
        # generate List file
        if not os.path.isfile(filename):
            SharedMethods.osop_running(cmdline)
        lst_file_size = os.path.getsize(filename)
        
        if lst_file_size < 10000: # a random size (bytes) to check if lst should be redone (10000 bytes = 10 kb)
            SharedMethods.osop_running(cmdline)
    

    # module to read the text file input    
    def file_read_import(filename,simname):
        
        if not os.path.isfile(filename): # if the file exist
            input("Required input file {} does not exist. Please select another option.".format(filename))
        #modulename(simname)

        # reading the train list file
        text_input = []
        with open(filename) as fbrlist:
            for index, line in enumerate(fbrlist):
                text_input.append(line[:50].strip())

        return text_input
    
    # write to text file (not used)
    def file_write(header,creatname,listname):
        with open(creatname, 'w') as fw:
            fw.write(header)
            for items in listname:
                string_line = map(str,items) # string all item
                result_line = ",".join(string_line) # join item removing brackets/quotes
                fw.write("%s\n" % result_line) # print out
    

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
        

    # since numpy is not supported by default (not used)
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