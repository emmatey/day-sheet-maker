import models as m
import utils as u
import re
import csv

def build_store(csv_path, config_object_settings_time_blocks, config_object_settings_role_map):
    with open(csv_path, "r") as f:
        inputCSV = csv.reader(f)
        inputCSVrows = list(inputCSV)

    column_day_map, dates = u.column_day_map(csv_path)
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
        if any(',' in cell for cell in row):
            employee_index = index
            name_row = row

            split_name = name_row[0].split(',')

            last_name = split_name[0].strip().replace('"', '').title()
            # Handle cases where there's no first name safely
            first_name = split_name[1].strip().replace('"', '').title() if len(split_name) > 1 else ""

            # --- Minor tag detection ---
            minor_tag = ""
            if "(M)" in first_name or "(m)" in first_name:
                minor_tag = "(M)"
                first_name = first_name.replace("(M)", "").replace("(m)", "").strip()

            # --- Remove middle initials ---
            split_first = first_name.split()
            clean_first_parts = [word for word in split_first if len(word) > 1]
            first_name = " ".join(clean_first_parts)

            # --- Remove duplicated last name if inside first name ---
            if last_name in first_name:
                first_name = first_name.replace(last_name, "").strip()

            # --- Assemble clean name ---
            if minor_tag:
                clean_name = f"{first_name} {last_name} {minor_tag}"
            else:
                clean_name = f"{first_name} {last_name}"

            role_row = inputCSVrows[index + 1]
            employee = m.Employee(employee_index, clean_name, role_row[0])

            for index, cell in enumerate(name_row):
                if ":" in cell:
                    day_of_the_week = column_day_map.get(index)
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

    hrd.calculate_hours()
    return hrd
