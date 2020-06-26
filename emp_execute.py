# @author:  Raul Rivero Rubio (TA)
# @date:    06/24/2020
# @version: 1.0
# @note:
#       This program creates PH-Employee tables and attempts to import the
#       the csv file data into the tables.

# src:https://www.dataquest.io/blog/loading-data-into-postgres/

# local dependencies
import emp_data as EMPDATA

# python module dependencies
import time
import os
import csv
import platform
import importlib
import re
import pkg_resources
from enum import IntEnum

# will hold the postgres server module 
psycopg2 = None

# src: https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# this works with tbe default buffer.
# If the defualt buffer is reset, it does not work.

#enums
#src: https://docs.python.org/3/library/enum.html
class Employee_IDX(IntEnum):
    EMPLOYEE = 0
    DEPARTMENTS = 1
    DEPT_EMPLOYEE = 2
    DEPT_MANAGER = 3
    SALARIES = 4
    TITLES = 5

#src: https://stackoverflow.com/questions/107705/disable-output-buffering
class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

import sys
sys.stdout = Unbuffered(sys.stdout)

# Global variables
DELIMETER = ','
DOT_RANGE= [1, 2, 3, 4, 5]
POSTGRESS_FILENAME = 'postgress_settings.txt'
postgress_keys = ['host', 'dbname', 'user', 'port']
postgress_dict = {}
EMPLOYEE_TABLES = ['employees', 'departments', 'dept_emp', 'dept_manager',
               'salaries', 'titles']
EMPLOYEE_CSV = ['employees.csv', 'departments.csv', 'dept_emp.csv', 'dept_manager.csv',
               'salaries.csv', 'titles.csv']
REQUIRED_PACKAGES = { 'pip' : 'pip'}
REQUIRED_MODULES = {'psycopg2' : 'psycopg2'}

# Infor about the current OS enviroment
env = None

# Class that information about the current Os enviroment
class System():
    os_name = None

    #python constructor 
    def __init__(self):
        self.os_name = platform.system()

    def console_clear(self):
        if(env != None):
            if(self.os_name == 'Windows'):
                os.system('CLS')
            else:
                os.system('clear')
                    
def main():
    con = None      # server connector
    global env      # Global var for the OS enviroment
    env = System()  # instance of the current OS

    header()

    import_modules()    # attempt to import the required module(s)
    
    try:
        read_postgress_settings()       #read the postgress connection settings
        con = establish_server_con()    # establish a connection and return a setting

        if menu() == 1:
            check_for_packages()
            check_for_modules()
            create_tables(con)
            insert_data_csv_to_table(con)
        else:
            delete_tables(con)
            
        close_server_con(con);  # close the connection    
    except psycopg2.Error as e:
        print(f"EXCEPTION: main()\n{e}")
        close_server_con(con);  # close the connection
        print('Exiting the program', end='')
        exit()

    print('Exiting the program', end='')
    print_dot(DOT_RANGE[2])
    clear(0)
    

# @note: Function checks if the required packages are installed
#       in the current version of python
def check_for_packages():
    found = False
    
    installed_packages = pkg_resources.working_set
    installed_packages_list = sorted(["%s==%s" % (i.key, i.version)\
        for i in installed_packages])

    #required packages
    for req_pack in REQUIRED_PACKAGES:
        found = False
        print(f'Looking for package [{req_pack}]')
        
        for pckg in installed_packages_list:
            if(bool(re.search(req_pack, pckg))):
                found = True
                print(f'package \'{pckg}\' is installed')

    # Only for pip
    if(found != True):
        command = 'python -m pip install -U pip'
        os.system(command);
        
    print('continue', end='')
    print_dot(DOT_RANGE[2])
    clear(0)

# @note: Function attempts to import the the required module
#       in the current version of python
# @exception: ModuleNotFoundError   action: download and install currect module
def import_modules():
    # Import the "Database Driver" library to connect to the database.
    global psycopg2
    
    try:
        import psycopg2 
    except ModuleNotFoundError:
        install_module('psycopg2')
        
        print('continue', end='')
        print_dot(DOT_RANGE[2])
        clear(0)


# @note: Function checks for the required module
def check_for_modules():
    found = False

    for req_mod in REQUIRED_MODULES:
        found = False
        print(f'Looking for module [{req_mod}]')
        if importlib.util.find_spec(req_mod) != None:
            found = True
            print(f'module \'{req_mod}\' found\n')
        else:
            install_module(req_mod)
    print('continue', end='')
    print_dot(DOT_RANGE[2])
    clear(0)

# @note: Function downloads and required current module
#
# @param: arg   the argument for the command to download and
#               install the module
def install_module(arg):
    # Import the "Database Driver" library to connect to the database.
    global psycopg2
    
    command = 'pip install '
    
    print(f'installing module: [{arg}]')
    os.system(command + arg)
    
    import psycopg2  

# @note: Program header information
def header():
    clear(0)
    print('title: PH-EmployeeDB: CSV -> DB TABLES\n'\
          'author: Raul Rivero Rubio (TA)\n\n')
    time.sleep(1)
 
    print('This program creates the PH-EmployeeDB <tables> and\n'\
          'imports the corrersponding csv file to the PH-EmployeeDB <tables>.\n')
    clear(5)

# @note: Program menu
def menu():
    confirmed = False
    option = None
    answer = 'n'

    print('Menu:')
    while (option == 2 and not confirmed) or option == None:
        confirmed = False
        while option != 1 and option != 2 or option == None:
            try: 
                option = int(input('Enter a number for an option:\n'\
                '(0)\tEXIT PROGRAM\n'\
                '(1)\tCreate All tables of [PH-EmployeeDB] and\n\tImport csv data into the tables\n'\
                '(2)\tDelete All tables of [PH-EmployeeDB] -> ').strip())
                if(option == 0):
                    print('exiting', end='')
                    print_dot(DOT_RANGE[0])
                    clear(0)
                    exit() 
                elif (option != 1 and option != 2):
                    print(f'INVALID: Only the number (1) or (2) is allowed! [{option}]\n')
            except ValueError as valerr:
                print("EXCEPTION: option()\nMust be a [NUMERIC] value!\n")
                clear(2)
        if option == 1:
            confirmed = True
        elif option == 2:
            answer = input('Are you sure? (y | n): ').strip().lower()
            if(answer != 'y'):
                option = None
                confirmed = False
            else:
                confirmed = True
        clear(2)

    return option

# @note: Function reads the file setting properties and stores it a
# global (postgress) dictionary
def read_postgress_settings():
    exit = 0
    print(f'Reading from the \"{POSTGRESS_FILENAME}\" file for\n'\
          'the postgress driver settings...\n')
    try:
        file = open(POSTGRESS_FILENAME, 'r')

        for i,line in enumerate(file):
            postgress_dict.update({postgress_keys[i]: line.rstrip('\n')}) # get rid of the newline

        print('Data fetch\t[Successful]')
        print('closing file', end='')
        print_dot(DOT_RANGE[2])
        
        file.close()    # close the file 
    except FileNotFoundError:
        print(f'EXCEPTION: read_postgress_settings()\nNo such file or directory: {POSTGRESS_FILENAME}')
        print('exiting', end='')
        print_dot(DOT_RANGE[2])
        exit()

    clear(0)
    
# @note: Function establishes a connection with the postgress server and returns the connection
#
# @return   postgres server connector
def establish_server_con():
    connected = False
    MAX_ATTEMPT = 3;
    attpt_cnt = 1;
    while(not connected and attpt_cnt <= MAX_ATTEMPT):
        try:
            # Variable has an establish connection with the database server
            con = psycopg2.connect(dbname=postgress_dict['dbname'],
                            user=postgress_dict['user'],
                            password=input(f'Attempt {attpt_cnt} : MAX[{MAX_ATTEMPT}]\n<your postgress password>: ').strip(),
                            host=postgress_dict['host'],
                            port=postgress_dict['port']);
            connected = True
        except:
            attpt_cnt += 1
            print(f'Password authentication failed for user [{postgress_dict["user"]}]')
            clear(2)

    if(attpt_cnt > MAX_ATTEMPT):
        print(f'\nSurpassed the MAXIMUM ATTEMPTS: {MAX_ATTEMPT}')
        print('Abort: exiting')
        print_dot(DOT_RANGE[2])
        clear(0)
        exit()
    
    print('\nServer Connection Established\t[Successful]')
    print(con)
    print('continue', end='')
    print_dot(DOT_RANGE[2])
    clear(0)
    
    return con

# @note: Function closes the connection with postgres server
# @param    con     connector.
def close_server_con(con):
    global env
    
    # Variable has an establish connection with the database server
    con.close()
    print('Server Connection Closed!\t[Successful]\n')
    time.sleep(1)

# @note: Function creates database for the 'PH-EMPLOYEEDB'
# @param    con     connector.
def create_database_name(con):
    # Variable Cursor object with a stringified SQL command.
    cur = con.cursor()

    #Preparing query to create a database
    sql = '''CREATE DATABASE "PH-EMPLOYEEDB"'''

    print("Database created\t[Successful]\n")

    clear(2)

# @note: Function creates all required tables for the 'PH-EMPLOYEEDB database'
# @param    con     connector.
def create_tables(con):
    # Variable Cursor object with a stringified SQL command.
    cur = con.cursor()
      
    print('IF NOT EXISTS ', end='')
    print_dot(DOT_RANGE[1])
    
    # Creating tables for PH-EmployeeDB
    for enum in Employee_IDX:
        cur.execute(EMPDATA.SQL_STATEMENT['Create'][enum.value])
        print(f'\tCreates: \"{EMPLOYEE_TABLES[enum.value]}\"')
    print('Completed!\t[Successful]\n')

    # commit the transaction
    con.commit()

    clear(2)

# @note: Function deletes all required tables for the 'PH-EMPLOYEEDB database including
#           the integral relations between them.
# @param    con     connector.
def delete_tables(con):
    # Variable Cursor object with a stringified SQL command.
    cur = con.cursor()

    print('IF EXISTS ', end='')
    print_dot(DOT_RANGE[1])

    for enum in Employee_IDX:
        cur.execute(EMPDATA.SQL_STATEMENT['Drop'][enum.value])
        print(f'\tDrop: \"{EMPLOYEE_TABLES[enum.value]}\"')
    print('Completed!\t[Successful]\n')

    # commit the transaction
    con.commit()

    clear(2)

# @note: Function inserts data from csv to tables of the 'PH-EMPLOYEEDB' database
# @param    con     connector.
def insert_data_csv_to_table(con):
    cur = con.cursor();
    start = 1 #skip header

    # iterate throug all required csv files
    for i in range(0, len(EMPLOYEE_CSV)):
        print(f'Inserting in table [{EMPLOYEE_TABLES[i]}]', end='')
        print_dot(DOT_RANGE[2])
        with open(os.path.join('.', 'csv', EMPLOYEE_CSV[i])) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = DELIMETER)
            row_count = sum(1 for row in csv_reader) - 1
            csv_file.close()

            #inserting
            if Employee_IDX.EMPLOYEE  == i:
                into_employees(cur, EMPLOYEE_CSV[i], row_count)
            elif Employee_IDX.DEPARTMENTS == i:
                into_departments(cur, EMPLOYEE_CSV[i], row_count)
            elif Employee_IDX.DEPT_EMPLOYEE == i:
                into_dept_emp(cur, EMPLOYEE_CSV[i], row_count)
            elif Employee_IDX.DEPT_MANAGER == i:
                into_dept_manager(cur, EMPLOYEE_CSV[i], row_count)
            elif Employee_IDX.SALARIES  == i:
                into_salaries(cur, EMPLOYEE_CSV[i], row_count)
            elif Employee_IDX.TITLES == i:
                into_titles(cur, EMPLOYEE_CSV[i], row_count)

        print('continue', end='')
        print_dot(DOT_RANGE[2])
        print()
        clear(0)

    con.commit() # commit the insertion if there is not errors
    print('Inserted!\t[Successful]\n')

    clear(3)

# @note: Function inserts data from [employees]csv to [employees]table of the 'PH-EMPLOYEEDB' database
# @param    con     connector.
# @param    filename    the csv filename
# @param    r_count     total count of rows in the csv file  
def into_employees(cur, filename, r_count):
    COLUMN_COUNT = 6
    start = 1; # skip header

    # enumarting indexes
    empkey = {'emp_no' : 0,
                'birth_date': 1,
                'first_name': 2,
                'last_name': 3,
                'gender': 4,
                'hire_date': 5}
    
    empval = [None] * COLUMN_COUNT


    with open(os.path.join('.', 'csv', filename)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = DELIMETER)

        for r, record in enumerate(csv_reader):
            #skip the header row
            if(r < start):
                continue
            
            for c, cell in enumerate(record):
                if (c == empkey['emp_no']):
                    empval[c] = int(cell) # cast to int
                else:
                    empval[c] = cell

            cur.execute(EMPDATA.SQL_STATEMENT['Insert'][Employee_IDX.EMPLOYEE],
                                            (empval[empkey['emp_no']],
                                             empval[empkey['birth_date']],
                                             empval[empkey['first_name']],
                                             empval[empkey['last_name']],
                                             empval[empkey['gender']],
                                             empval[empkey['hire_date']]))
            print(f'row: {[r]} of {r_count}')
        csv_file.close()
    
# @note: Function inserts data from [departments]csv to [departments]table of the 'PH-EMPLOYEEDB' database
# @param    con     connector.
# @param    filename    the csv filename
# @param    r_count     total count of rows in the csv file  
def into_departments(cur, filename, r_count):
    COLUMN_COUNT = 2
    start = 1; # skip header

    # enumarting indexes
    empkey = {'dept_no' : 0,
                'dept_name': 1
              }

    empval = [None] * COLUMN_COUNT

    with open(os.path.join('.', 'csv', filename)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = DELIMETER)

        for r, record in enumerate(csv_reader):
            #skip the header row
            if(r < start):
                continue            
                       
            for c, cell in enumerate(record):
                empval[c] = cell
                

            cur.execute(EMPDATA.SQL_STATEMENT['Insert'][Employee_IDX.DEPARTMENTS],
                                                (empval[empkey['dept_no']],
                                                empval[empkey['dept_name']]))
            print(f'row: {[r]} of {r_count}')
        csv_file.close()
        
# @note: Function inserts data from [dept_emp]csv to [dept_emp]table of the 'PH-EMPLOYEEDB' database
# @param    con     connector.
# @param    filename    the csv filename
# @param    r_count     total count of rows in the csv file  
def into_dept_emp(cur, filename, r_count):
    COLUMN_COUNT = 4
    start = 1; # skip header

    # enumarting indexes
    empkey = {'emp_no' : 0,
                'dept_no': 1,
                'from_date': 2,
                'to_date': 3
              }

    empval = [None] * COLUMN_COUNT

    with open(os.path.join('.', 'csv', filename)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = DELIMETER)
        
        for r, record in enumerate(csv_reader):
            #skip the header row
            if(r < start):
                continue   

            for c, cell in enumerate(record):
                if (c == empkey['emp_no']):
                    empval[c] = int(cell) # cast to int
                else:
                    empval[c] = cell

            cur.execute(EMPDATA.SQL_STATEMENT['Insert'][Employee_IDX.DEPT_EMPLOYEE],
                                            (empval[empkey['emp_no']],
                                             empval[empkey['dept_no']],
                                             empval[empkey['from_date']],
                                             empval[empkey['to_date']]))
            print(f'row: {[r]} of {r_count}')
        csv_file.close()
    
# @note: Function inserts data from [dept_manager]csv to [dept_manager]table of the 'PH-EMPLOYEEDB' database
# @param    con     connector.
# @param    filename    the csv filename
# @param    r_count     total count of rows in the csv file
def into_dept_manager(cur, filename, r_count):
    COLUMN_COUNT = 4
    start = 1; # skip header

    # enumarting indexes
    empkey = {'dept_no' : 0,
                'emp_no': 1,
                'from_date': 2,
                'to_date' : 3
              }

    empval = [None] * COLUMN_COUNT

    with open(os.path.join('.', 'csv', filename)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = DELIMETER)
        for r, record in enumerate(csv_reader):
            #skip the header row
            if(r < start):
                continue   

            for c, cell in enumerate(record):
                if (c == empkey['emp_no']):
                    empval[c] = int(cell) # cast to int
                else:
                    empval[c] = cell

            cur.execute(EMPDATA.SQL_STATEMENT['Insert'][Employee_IDX.DEPT_MANAGER],
                                    (empval[empkey['dept_no']],
                                    empval[empkey['emp_no']],
                                    empval[empkey['from_date']],
                                    empval[empkey['to_date']]))
            print(f'row: {[r]} of {r_count}')
        csv_file.close()

# @note: Function inserts data from [salaries]csv to [salaries]table of the 'PH-EMPLOYEEDB' database
# @param    con     connector.
# @param    filename    the csv filename
# @param    r_count     total count of rows in the csv file
def into_salaries(cur, filename, r_count):
    COLUMN_COUNT = 4
    start = 1; # skip header

    # enumarting indexes
    empkey = {'emp_no' : 0,
                'salary': 1,
                'from_date': 2,
                'to_date' : 3
              }

    empval = [None] * COLUMN_COUNT

    with open(os.path.join('.', 'csv', filename)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = DELIMETER)

        for r, record in enumerate(csv_reader):
            #skip the header row
            if(r < start):
                continue   

            for c, cell in enumerate(record):
                if (c == empkey['emp_no'] or c == empkey['salary']):
                    empval[c] = int(cell) # cast to int
                else:
                    empval[c] = cell

            cur.execute(EMPDATA.SQL_STATEMENT['Insert'][Employee_IDX.SALARIES],
                            (empval[empkey['emp_no']],
                            empval[empkey['salary']],
                            empval[empkey['from_date']],
                            empval[empkey['to_date']]))
            print(f'row: {[r]} of {r_count}')
        csv_file.close()

# @note: Function inserts data from [titles]csv to [titles]table of the 'PH-EMPLOYEEDB' database
# @param    con     connector.
# @param    filename    the csv filename
# @param    r_count     total count of rows in the csv file
def into_titles(cur, filename, r_count):
    COLUMN_COUNT = 4
    start = 1; # skip header
    
    # enumarting indexes
    empkey = {'emp_no' : 0,
                'title': 1,
                'from_date': 2,
                'to_date' : 3
              }

    empval = [None] * COLUMN_COUNT

    with open(os.path.join('.', 'csv', filename)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = DELIMETER)

        for r, record in enumerate(csv_reader):
            #skip the header row
            if(r < start):
                continue
            
            for c, cell in enumerate(record):
                if (c == empkey['emp_no']):
                    empval[c] = int(cell) # cast to int
                else:
                    empval[c] = cell

            cur.execute(EMPDATA.SQL_STATEMENT['Insert'][Employee_IDX.TITLES],
                            (empval[empkey['emp_no']],
                            empval[empkey['title']],
                            empval[empkey['from_date']],
                            empval[empkey['to_date']]))
            print(f'row: {[r]} of {r_count}')
        csv_file.close()

# @note: Functions clear the console
def clear(sec):
    global env
    time.sleep(sec)
    env.console_clear()
    
# @note: Function prints 3 dots animation on the same line
def print_dot(dot_range):
    for i in range(0, dot_range):
        for j in range(0, dot_range):
            print('.', end='')
            time.sleep(0.3)
        if i < dot_range - 1:
            for k in range(0, dot_range):
                print('\b \b', end='')
            time.sleep(0.3)
    print()

# Execute the main function to begin the program
# src: https://realpython.com/python-main-function/
if __name__ == "__main__":
    main()
