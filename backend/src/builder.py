import models as m
import utils as u
import re
import csv
import NameFormatter
from collections import defaultdict

def build_store(csv_path, config_object_settings_time_blocks, config_object_settings_role_map):
    with open(csv_path, "r") as f:
        inputCSV = csv.reader(f)
        inputCSVrows = list(inputCSV)

    column_day_map, _ = u.column_day_map(csv_path)
    store_number = u.extract_store_number(csv_path)

    hrd = m.Store(store_number)

    # Create the departments and add them to the store
    for index, row in enumerate(inputCSVrows):
        for cell in row:
            if "Dept:" in cell:
                match = re.search(r"Dept:\d+\s+(.+)", cell)
                if match:
                    dept_clean_name = match.group(1).strip()
                    dept_time_blocks = config_object_settings_time_blocks.get(dept_clean_name, [])
                    dpt = m.Department(index, dept_clean_name, dept_time_blocks)
                    hrd.add_department(dpt)

    # Create the employees, add their shifts, and then add them to the departments
    for index, row in enumerate(inputCSVrows):
        NAME_PATTERN = re.compile(r"^([A-Za-z' -]+),\s*(.+)$")

        for cell in row:
            match = re.search(NAME_PATTERN, cell)
            if match:
                employee_index = index
                name_row = row

                name_formatting_object = NameFormatter.NameFormatter(match)

                role_row = inputCSVrows[index + 1]
                employee = m.Employee(
                    employee_index,
                    name_formatting_object.clean_name,
                    name_formatting_object.middle_initial,
                    role_row[0]
                )

                for col_idx, cell in enumerate(name_row):
                    if ":" in cell:
                        day_of_the_week = column_day_map.get(col_idx)
                        shift_objects = u.parse_shift_cell(cell, day_of_the_week)
                        for shift in shift_objects:
                            employee.add_shift(shift)

                assigned_department = None
                for dept in hrd.department_list:
                    if employee_index > dept.dept_index:
                        assigned_department = dept

                if assigned_department:
                    employee.add_dept(assigned_department.dept_name)
                    employee.set_display_role(assigned_department.dept_name, config_object_settings_role_map)
                    assigned_department.add_employee(employee)
                
                break

    def disambiguate_duplicate_names(store, debug = False):
        """
        Adds middle initials to employees who share the same name within the same department.

        Args:
            store (Store): The store object containing departments and employees.
            debug (bool): If True, prints which names were disambiguated.
        """
        for department in store.department_list:
            employees_by_name = defaultdict(list)

            # Group employees by their clean base name
            for employee in department.employees:
                employees_by_name[employee.name].append(employee)

            # Add middle initials where duplicates exist
            for name, list_of_employee_objects_with_said_name in employees_by_name.items():
                if len(list_of_employee_objects_with_said_name) > 1:
                    for emp in list_of_employee_objects_with_said_name:
                        # Only add middle initial if one exists
                        if emp.middle_initial:
                            first, last = emp.name.split(maxsplit=1)
                            emp.name = f"{first} {emp.middle_initial.upper()} {last}"
                            if debug:
                                print(f"Updated: {name} -> {emp.name}")

    hrd.calculate_hours()
    disambiguate_duplicate_names(hrd)
    return hrd
