#Functions Base
import re
import csv
import models as m
import datetime
from copy import copy
from collections import defaultdict
from openpyxl.styles import Border, Side, Font, Alignment


def department_row_map(csv_path):

    # This function parses the .csv and builds a dictionary that maps
    # row numbers (line indices) to department labels (e.g., "Dept:003 Center Store").
    # This dictionary helps determine where each department begins in the file,
    # enabling future grouping of employees by department range.

    # Open the CSV file in read mode
    with open(csv_path, "r") as f:
        # Create a CSV reader object
        inputCSV = csv.reader(f)

        # Dictionary to store {row_index: department_name}
        department_row_map = {}

        # Iterate over each row and its index
        for i, row in enumerate(inputCSV):
            # Check if any cell in the row contains "Dept:"
            if any("Dept:" in cell for cell in row):
                # Join all cells into a single string so regex can scan across the whole row
                line_text = ",".join(row)

                # Use regex to extract the full "Dept:xxx Department Name" string
                regex = r"Dept:.+"
                result = re.search(regex, line_text)

                # If a match is found, save it to the dictionary
                if result:
                    clean_result = result.group().strip(',')
                    department_row_map[i] = clean_result


    # Return the complete mapping of departments to their row positions
    return department_row_map


def column_day_map(csv_path):
    """
    Scans the schedule CSV file to find which columns correspond to which days of the week.
    Returns a mapping from column index → weekday index (0 = Sunday, 6 = Saturday).
    """

    with open(csv_path, "r") as f:
        schedule = csv.reader(f)
        header_row = []

        # Find the header row (should contain 'Name' in the first cell)
        for row in schedule:
            if row and row[0].strip() == "Name":
                header_row = row
                break

        # Regex pattern to detect cells like "Sun 3/09", "Mon 3/10", etc.
        regex = r'\w+\s+(\d+/\d+)'
        matched_columns = []
        dates = []

        # Find all columns that match the day format
        for col_index, cell in enumerate(header_row):
            if re.match(regex, cell):
                match = re.match(regex, cell)
                if match:
                    matched_columns.append(col_index)
                    dates.append(match.group(1))

        # Map column index → weekday index (0–6)
        return {col: i for i, col in enumerate(sorted(matched_columns))}, dates


def extract_store_number(csv_path):
    """
    Extracts the store number from a .csv file.

    The function scans through each row and cell in the CSV file until it finds
    a cell that contains the string 'Store:####'. It returns the numeric portion
    of that string as a string (e.g., '8384').

    Parameters:
        filepath (str): The path to the .csv file.

    Returns:
        str: The extracted store number, or None if no match is found.
    """
    with open(csv_path, "r") as f:
        inputCSV = csv.reader(f)
        # Go through each row in the CSV
        for row in inputCSV:
            # Check each cell in the row
            for cell in row:
                # Look for a pattern like 'Store:1234'
                match = re.search(r'Store:(\d+)', cell)
                if match:
                    # Return only the digits part (e.g., '1234')
                    return match.group(1)

    # If we get here, no store number was found
    return None


def parse_shift_cell(shift_cell, index):
    """
    Parses a cell containing shift information and returns a list of Shift objects.

    Handles both single and split shifts. For split shifts, durations are not currently separated.

    Args:
        shift_cell (str): The cell string from the name_row that may contain shift data.
        index (int): The column index where the shift is located.

    Returns:
        list of Shift objects.
    """
    regex_double = r'(\d+:\d+\w+)-(\d+:\d+\w+)\n(\d+:\d+\w+)-(\d+:\d+\w+)'
    regex_single = r'(\d+:\d+\w+)-(\d+:\d+\w+)'
    regex_duration = r'Hrs:(.+)'

    duration = re.search(regex_duration, shift_cell)
    double = re.search(regex_double, shift_cell)
    if double and duration:
        return [
            m.Shift(index,
                    datetime.datetime.strptime(double.group(1), '%I:%M%p').time(),
                    datetime.datetime.strptime(double.group(2), '%I:%M%p').time(),
                    float(duration.group(1))),
            m.Shift(index,
                    datetime.datetime.strptime(double.group(3), '%I:%M%p').time(),
                    datetime.datetime.strptime(double.group(4), '%I:%M%p').time(),
                    0.0) #all paid hours for the day are already contained in the first shift object of the split/double shift.
        ]

    single = re.search(regex_single, shift_cell)
    if single and duration:
        return [m.Shift(index,
                        datetime.datetime.strptime(single.group(1), '%I:%M%p').time(),
                        datetime.datetime.strptime(single.group(2), '%I:%M%p').time(),
                        float(duration.group(1)))]

    return []


def calculate_block_overlaps(shift_start, shift_end, time_blocks):
    """
    Given a shift's start and end time, and a list of time blocks (each a tuple of (start, end, name)),
    returns a dictionary mapping time block names to the number of overlapping hours.
    """
    overlaps = {}

    for block in time_blocks:
        block_start = datetime.datetime.strptime(block[0], "%H:%M").time()
        block_end = datetime.datetime.strptime(block[1], "%H:%M").time()
        block_name = f"{block[2]} = {block[0]}-{block[1]}"

        # convert to datetime objects on the same base day for math
        start_shift = datetime.datetime.combine(datetime.date.min, shift_start)
        end_shift = datetime.datetime.combine(datetime.date.min, shift_end)
        start_block = datetime.datetime.combine(datetime.date.min, block_start)
        end_block = datetime.datetime.combine(datetime.date.min, block_end)

        # handle overnight blocks or shifts
        if end_block <= start_block:
            end_block += datetime.timedelta(days=1)
        if end_shift <= start_shift:
            end_shift += datetime.timedelta(days=1)

        # Calculate the overlapping hours between the shift and each time block
        # remember that this is code is reapplied to every individual time block iterateively
        latest_start = max(start_shift, start_block)
        # We want the later of the two start times because overlap only begins
        # when both the shift and the block are active.
        # If a shift starts at 7AM and the block starts at 8AM, the overlap begins at 8AM.

        earliest_end = min(end_shift, end_block)
        # We want the earlier of the two end times because overlap ends
        # when either the shift or the block ends.
        # If a shift ends at 2PM but the block ends at 12PM, overlap ends at 12PM.

        delta = (earliest_end - latest_start).total_seconds() / 3600
        # This gives us the overlap duration in seconds.
        # We convert it to hours by dividing by 3600.

        overlap_hours = max(0, delta)
        # In case there’s no overlap (delta is negative), we use max(0, delta)
        # to avoid assigning negative hours.

        overlaps[block_name] = overlap_hours
        # Store the calculated overlap hours for this block in a dictionary,
        # using the block's name (which includes time and label) as the key.

    return overlaps


def insert_title_cell(ws, day, column_day_map):
    _, dates = column_day_map
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    template_cell = ws.cell(row=1, column=1)

    # Copy the style from original cell (assuming row=1, col=1 is pre-styled)
    template_cell.font = copy(template_cell.font)
    template_cell.fill = copy(template_cell.fill)
    template_cell.border = copy(template_cell.border)
    template_cell.alignment = Alignment(horizontal="center", vertical="center")

    # Insert the value
    template_cell.value = f"{days[day]} - {dates[day]}"


def insert_role_header(ws, row_number, role_name):
    """
    Inserts a styled role header at the specified row using the template from A4:H4.
    Replaces the role name into column A (like "SHOPPERS:").
    """
    thick_border = Border(
            left=Side(style="thick"),
            right=Side(style="thick"),
            top=Side(style="thick"),
    )


    thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin")
        )

    for col in range(1, 9):  # A to H
        template_cell = ws.cell(row=4, column=col)
        target_cell = ws.cell(row=row_number, column=col)

        # Safely copy styles
        target_cell.font = copy(template_cell.font)
        target_cell.fill = copy(template_cell.fill)
        target_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Write role name or leave blank
        if col == 1:
            target_cell.value = f"{role_name.upper()}:"
            target_cell.border = thin_border

        elif col == 2:
            target_cell.value = 'In'
            target_cell.border = thin_border

        elif col == 3:
            target_cell.value = 'Out'
            target_cell.border = thin_border

        elif col == 4:
            target_cell.value = 'B'
            target_cell.border = thin_border

        elif col == 5:
            target_cell.value = 'L'
            target_cell.border = thin_border

        elif col == 6:
            target_cell.value = 'B'
            target_cell.border = thin_border

        elif col == 7:
            target_cell.value = 'Length'
            target_cell.border = copy(template_cell.border)

        elif col == 8:
            target_cell.value = 'Out'
            target_cell.border = copy(template_cell.border)

        else:
            target_cell.value = ""
            target_cell.border = copy(template_cell.border)


def employee_group(dept, day_index):
    """
    Groups employees into their output headers for a given department and day.

    Args:
        dept (Department): The department object containing employees and shifts.
        day_index (int): The day of the week (0 = Sunday, 1 = Monday, etc.)

    Returns:
        defaultdict(list): A dictionary where keys are display_role names
                           and values are lists of employee names under that role.
    """

    # Start with a defaultdict so every role key auto-creates a list
    employee_group = defaultdict(list)

    # Get the role mapping for this department (which defines header order)
    role_map = ROLE_MAP.get(dept.dept_name, {})
    clean_roles = role_map.get('clean_roles', [])
    role_index = 0

    # This will track employees who were placed correctly in a role
    all_sorted = []

    # First, sort employees according to the preferred role order
    for i in range(len(clean_roles)):
        for emp in dept.employees:
            for shift in emp.shifts:
                if shift.day_index == day_index and emp.display_role == clean_roles[role_index] and emp not in all_sorted:
                    employee_group[emp.display_role].append(emp)
                    all_sorted.append(emp)

        role_index += 1

    # After the preferred roles, assign any remaining employees
    for emp in dept.employees:
        if emp not in all_sorted:
            for shift in emp.shifts:
                if shift.day_index == day_index:
                    employee_group[emp.display_role].append(emp)

    return employee_group


def insert_labor_tracker(ws, labor_data, title, start_row, start_col=10):
    """
    Inserts a small labor tracker table into the worksheet.
    """
    from openpyxl.styles import Font, Alignment, Border, Side

    # Borders
    thick_border = Border(
        left=Side(style="thick"),
        right=Side(style="thick"),
        top=Side(style="thick"),
        bottom=Side(style="thick")
    )

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    # 1. Title row
    ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row, end_column=start_col+4)

    for col in range(start_col, start_col+5):
        cell = ws.cell(row=start_row, column=col)
        cell.border = thick_border
        cell.font = Font(bold=True, size=12, name='Calibri')
        cell.alignment = Alignment(horizontal="center", vertical="center")

    title_cell = ws.cell(row=start_row, column=start_col)
    title_cell.value = title

    # 2. Data rows
    current_row = start_row + 1

    for block_name, hours in labor_data.items():
        ws.merge_cells(
            start_row=current_row,
            start_column=start_col,
            end_row=current_row,
            end_column=start_col+3
        )

        # Format merged block name cells
        for col in range(start_col, start_col+4):
            block_cell = ws.cell(row=current_row, column=col)
            block_cell.border = thin_border
            block_cell.font = Font(bold=False, size=12, name='Calibri')
            block_cell.alignment = Alignment(horizontal="left", vertical="center")

        block_cell = ws.cell(row=current_row, column=start_col)
        block_cell.value = block_name

        # Format the hours cell
        hours_cell = ws.cell(row=current_row, column=start_col+4)
        hours_cell.value = round(hours, 2)
        hours_cell.border = thin_border
        hours_cell.font = Font(bold=True, size=12, name='Calibri')
        hours_cell.alignment = Alignment(horizontal="center", vertical="center")

        current_row += 1


def insert_headers_and_employees(ws, employee_group_dict, day_index, start_row=4):
    role_names = list(employee_group_dict.keys())
    current_row = start_row

    for i, employee_list in enumerate(employee_group_dict.values()):
        # 1. Insert role header
        insert_role_header(ws, current_row, role_names[i])
        current_row += 1

        # 2. Collect today's employees (with shifts on this day)
        todays_employees = []

        for emp in employee_list:
            for shift in emp.shifts:
                if shift.day_index == day_index:
                    todays_employees.append((shift.start_time, shift, emp))

        # 3. Sort by start_time
        todays_employees.sort(key = lambda x: x[0])

        # 4. Insert employees
        for start_time, shift, emp in todays_employees:
            for col in range(1, 9):  # A to H
                source_cell = ws.cell(row=5, column=col)
                target_cell = ws.cell(row=current_row, column=col)

                target_cell.font = copy(source_cell.font)
                target_cell.fill = copy(source_cell.fill)
                target_cell.border = copy(source_cell.border)
                target_cell.alignment = Alignment(horizontal="center", vertical="center")

                if col == 1:
                    target_cell.value = emp.name

                elif col == 2:
                    target_cell.value = shift.start_time.strftime("%I:%M %p")

                elif col == 3:
                    target_cell.value = shift.end_time.strftime("%I:%M %p")

                elif col == 7:
                    target_cell.value = shift.paid_hours

                else:
                    target_cell.value = ""

            current_row += 1
    #Employees and Headers All Written, Now add Hours Tally.
    #5 Merge Hours Tally Write Area
    ws.merge_cells(start_row=current_row, start_column=4, end_row=current_row, end_column=6)

    #6 Insert Label
    label_cell = ws.cell(row=current_row, column=4)
    label_cell.value = "Total Hours:"
    label_cell.alignment = Alignment(horizontal="right", vertical="center")
    label_cell.font = Font(name='Calibri', bold=True)

    #7 Insert Hours Tally
    hours_cell = ws.cell(row=current_row, column=7)
    hours_cell.value = f"=SUM(G5:G{current_row-1})"  # Sum from G5 to the row above
    hours_cell.alignment = Alignment(horizontal="center", vertical="center")
    hours_cell.font = Font(name='Calibri', bold=True)

    return current_row


def insert_labor_trackers(ws, employee_group_dict, time_blocks, day_index, start_row = 4, start_col = 10):
    """
    Inserts a labor tracker for each role in the employee group dict.

    Args:
        ws (Worksheet): The Excel worksheet.
        employee_group_dict (dict): display_role -> list of Employee objects.
        time_blocks (list): The list of time blocks to calculate coverage.
        day_index (int): Which day to calculate (0=Sunday, 6=Saturday).
        start_row (int): The row to start inserting trackers.
        start_col (int): The column to insert trackers (default 10).

    Returns:
        int: The next empty row after all trackers.
    """
    role_names = list(employee_group_dict.keys())
    role_values = list(employee_group_dict.values())
    current_row = start_row

    for i, role in enumerate(role_names):
        display_subject = role_values[i]
        if len(display_subject) > 1:
            labor_coverage = defaultdict(int)
            for emp in employee_group_dict[role_names[i]]:
                for shift in emp.shifts:
                    if shift.day_index == day_index:
                        overlap = calculate_block_overlaps(shift.start_time, shift.end_time, time_blocks)
                        for block, hours in overlap.items():
                            labor_coverage[block] += hours

                # Insert a labor tracker for this role
            insert_labor_tracker(ws, labor_coverage, f"Labor Coverage: {role_names[i]}", start_row=current_row, start_col=start_col)

                # Move down after each labor tracker
            current_row += 5  # adjust depending on your tracker size

    return current_row


TIME_BLOCKS = {
    "Hannaford to Go": [("05:00", "10:00", "Opening Crew"), ("10:00", "15:00", "Midday"), ("15:00", "20:00", "Evening")],
    "Center Store": [("04:00", "12:00", "Load & Stock"), ("12:00", "18:00", "Repack"), ("18:00", "07:00", "Overnight")],
    "Produce": [("04:00", "08:00", "Morning"), ("08:00", "15:00", "Midday"), ("15:00", "19:00", "Close")],
    "Meat": [("04:00", "11:00", "Production"), ("11:00", "16:00", "Maintenance"), ("16:00", "20:00", "Close")],
    "Seafood": [("04:00", "11:00", "Prep"), ("11:00", "16:00", "Service"), ("16:00", "20:00", "Close")],
    "Deli": [("04:00", "11:00", "Prep"), ("11:00", "17:00", "Service"), ("17:00", "20:00", "Close")],
    "Bakery": [("04:00", "11:00", "Production"), ("11:00", "16:00", "Service"), ("16:00", "20:00", "Clean")],
    "Customer Service": [("7:00", "12:00", "Morning"), ("12:00", "17:00", "Midday"), ("17:00", "23:00", "Evening")],
    "Pharmacy": [("04:00", "12:00", "popopopo"), ("12:00", "16:00", "eeeeee"), ("16:00", "19:00", "the void comes")]
}


ROLE_MAP = {
    "Hannaford to Go": {
        "roles": ["Expeditor", "Shopper"],
        "clean_roles": ["Expeditor", "Shopper"],
        "default": "Shopper",
    },
    "Center Store": {
        "roles": ["Ctr Str Mgmt", "Ctr Str Lead", "Ctr Str Clerk", "Stock Crew Assoc", "Maintenance"],
        "clean_roles": ["Management", "Management", "Clerk", "Overnight", "Maintenance"],
        "default": "Clerk",
    },
    "Produce": {
        "roles": ["Associate"],
        "clean_roles": ["Produce Associate"],
        "default": "Produce Associate",
    },
    "Meat": {
        "roles": ["Meat Associate"],
        "clean_roles": ["Meat Associate"],
        "default": "Meat Associate",
    },
    "Seafood": {
        "roles": ["Seafood Associate", "Meat Associate"],
        "clean_roles": ["Seafood Associate", "Meat Associate"],
        "default": "Seafood Associate",
    },
    "Deli": {
        "roles": ["Deli Associate"],
        "clean_roles": ["Deli Associate"],
        "default": "Deli Associate",
    },
    "Bakery": {
        "roles": ["Associate"],
        "clean_roles": ["Bakery Associate"],
        "default": "Bakery Associate",
    },
    "Customer Service": {
        "roles": ["ServiceLeadr", "Service Desk Assoc", "Cashier Exp", "ServiceClerk", "SL SelfScan"],
        "clean_roles": ["Lead", "Service Desk", "Register Team", "Register Team", "Service Desk"],
        "default": "Cashier",
    },
    "Pharmacy": {
        "roles": ["Pharmacist", "Pharmacy Tech", "Tech"],
        "clean_roles": ["Pharmacist", "Pharmacy Tech", "Tech"],
        "default": "Pharmacy Tech",
    },
}
