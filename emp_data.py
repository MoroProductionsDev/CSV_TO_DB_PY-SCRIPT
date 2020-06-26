# @author:  Raul Rivero Rubio (TA)
# @date:    06/24/2020
# @version: 1.0
# @note:
#       Data Object with multiple static and dynamic sql statements

SQL_STATEMENT = {'Create':
                    [
                        'CREATE TABLE IF NOT EXISTS employees ('\
                            'emp_no INT NOT NULL,'\
                            'birth_date DATE NOT NULL,'\
                            'first_name VARCHAR NOT NULL,'\
                            'last_name VARCHAR NOT NULL,'\
                            'gender VARCHAR NOT NULL,'\
                            'hire_date DATE NOT NULL,'\
                            'PRIMARY KEY (emp_no)'\
                        ');'
                    ,
                        'CREATE TABLE IF NOT EXISTS departments ('\
                            'dept_no VARCHAR(4) NOT NULL,'\
                            'dept_name VARCHAR(40) NOT NULL,'\
                            'PRIMARY KEY (dept_no),'\
                            'UNIQUE (dept_name)'\
                        ');'
                    ,
                        'CREATE TABLE IF NOT EXISTS dept_emp ('\
                            'emp_no INT NOT NULL,'\
                            'dept_no VARCHAR(4) NOT NULL,'\
                            'from_date DATE NOT NULL,'\
                            'to_date DATE NOT NULL,'\
                            'FOREIGN KEY (emp_no) REFERENCES employees (emp_no),'\
                            'FOREIGN KEY (dept_no) REFERENCES departments (dept_no),'\
                            'PRIMARY KEY (emp_no, dept_no)'\
                        ');'
                    ,
                        'CREATE TABLE IF NOT EXISTS dept_manager ('\
                            'dept_no VARCHAR(4) NOT NULL,'\
                            'emp_no INT NOT NULL,'\
                            'from_date DATE NOT NULL,'\
                            'to_date DATE NOT NULL,'\
                            'FOREIGN KEY (emp_no) REFERENCES employees (emp_no),'\
                            'FOREIGN KEY (dept_no) REFERENCES departments (dept_no),'\
                            'PRIMARY KEY (emp_no, dept_no)'\
                        ');'
                    ,
                        'CREATE TABLE IF NOT EXISTS salaries ('\
                            'emp_no INT NOT NULL,'\
                            'salary INT NOT NULL,'\
                            'from_date DATE NOT NULL,'\
                            'to_date DATE NOT NULL,'\
                            'FOREIGN KEY (emp_no) REFERENCES employees (emp_no),'\
                            'PRIMARY KEY (emp_no)'\
                        ');'
                    ,
                        'CREATE TABLE IF NOT EXISTS titles ('\
                            'emp_no INT NOT NULL,'\
                            'title VARCHAR(50) NOT NULL,'\
                            'from_date DATE NOT NULL,'\
                            'to_date DATE,'\
                            'FOREIGN KEY (emp_no) REFERENCES employees (emp_no),'\
                            'PRIMARY KEY (emp_no, title, from_date)'\
                        ');'
                    ],
                 'Insert' : [
                        'Insert INTO employees(emp_no, birth_date, first_name, last_name, gender, hire_date)'\
                        'Values(%s, %s, %s, %s, %s, %s);'
                    ,
                        'Insert INTO departments(dept_no, dept_name)'\
                        'Values(%s, %s);'
                    ,
                        'Insert INTO dept_emp(emp_no, dept_no, from_date, to_date)'\
                        'Values(%s, %s, %s, %s);'
                    ,
                        'Insert INTO dept_manager(dept_no, emp_no, from_date, to_date)'\
                        'Values(%s, %s, %s, %s);'
                    ,
                        'Insert INTO salaries(emp_no, salary, from_date, to_date)'\
                        'Values(%s, %s, %s, %s);'
                    ,
                        'Insert INTO titles(emp_no, title, from_date, to_date)'\
                        'Values(%s, %s, %s, %s);'
                    ],
                 'Drop' : [
                        'DROP TABLE IF EXISTS employees CASCADE;'
                    ,
                        'DROP TABLE IF EXISTS departments CASCADE;'
                    ,
                        'DROP TABLE IF EXISTS dept_emp CASCADE;'
                    ,
                        'DROP TABLE IF EXISTS dept_manager CASCADE;'
                    ,
                        'DROP TABLE IF EXISTS salaries CASCADE;'
                    ,
                        'DROP TABLE IF EXISTS titles CASCADE;'
                    ]
                 }

