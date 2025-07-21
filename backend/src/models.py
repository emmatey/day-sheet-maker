class Store:
    def __init__(self, store_number):
        self.store_number = store_number
        self.department_list = []

    def __str__(self):
        output = f"My Store Number is {self.store_number}\n"
        output += f"Number of Departments = {len(self.department_list)}"
        return output

    def add_department(self, department):
        self.department_list.append(department)

    def add_store_number(self, store_number):
        self.store_number = store_number

    #populates the "labor_hours_this_week" for every employee object
    def calculate_hours(self):
        for department in self.department_list:
            for employee in department.employees:
                for shift in employee.shifts:
                    employee.add_hours(shift.paid_hours)


class Department:
    def __init__(self, dept_index, dept_name, time_blocks):
        self.dept_name = dept_name
        self.dept_index = dept_index
        self.employees = []
        self.time_blocks = time_blocks
        self.role_labor_coverage = {}

    def add_employee(self, employee):
        self.employees.append(employee)
    
    def __str__(self):
        output = f"{self.dept_name}\n"
        output += f"dept_index = {self.dept_index}\n"
        output += f"Number of Employees = {len(self.employees)}\n"
        return output


class Employee:
    #Create the employee object
    def __init__(self, emp_index, name, middle_initial, role):
        self.name = name
        self.middle_initial = middle_initial
        self.dept = ''
        self.role = role
        self.display_role = str() #this will be used in output
        self.labor_hours_this_week = 0.0
        self.emp_index = emp_index
        self.shifts = []

    def __str__(self):
       output = f"Name: {self.name}\n"
       output += f"Raw Role: {self.role}\n"
       output += f"Role: {self.display_role}\n"
       output += f"Hours This Week: {self.labor_hours_this_week}\n"
       output += f"Employee Index: {self.emp_index}\n"
       output += "Shifts:\n"
       for shift in self.shifts:
           output += f"  - {shift}\n"
       return output

    def add_shift(self, daily_shift_parsed):
        self.shifts.append(daily_shift_parsed)

    def add_dept(self, dept):
        self.dept = str(dept)

    def add_hours(self, shift_paid_hours):
        current_hours = self.labor_hours_this_week
        new_hours = current_hours + shift_paid_hours
        self.labor_hours_this_week = float(new_hours)

    def set_display_role(self, dept_name, config_object_settings_role_map):
        role_map = config_object_settings_role_map.get(dept_name, {})
        valid_roles = role_map.get("roles", [])
        clean_roles = role_map.get("clean_roles", [])

        if self.role in valid_roles:
            clean_index = valid_roles.index(self.role)
            self.display_role = clean_roles[clean_index]
        else:
            self.display_role = role_map.get("default", self.role)


class Shift:
    def __init__(self, day_index, start_time, end_time, paid_hours):
        self.day_index = int(day_index)
        self.start_time = start_time
        self.end_time = end_time
        self.paid_hours = float(paid_hours)

    def __str__(self):
        return f"Day {self.day_index}: {self.start_time} - {self.end_time} ({self.paid_hours} hrs)"
