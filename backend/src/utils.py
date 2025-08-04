import re
import csv
import models as m
import datetime
from copy import copy
from collections import defaultdict
from openpyxl.styles import Border, Side, Font, Alignment
from openpyxl.cell.rich_text import TextBlock, CellRichText
from openpyxl.cell.text import InlineFont


# Helper Functions
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


def employee_group(dept, day_index, config_object_role_map):
    """
    Groups employees into their output headers for a given department and day.

    Args:
        dept (Department): The department object containing employees and shifts.
        day_index (int): The day of the week (0 = Sunday, 1 = Monday, etc.)
        config_object_role_map: The settings for "raw" roles and their associated "clean names"

    Returns:
        defaultdict(list): A dictionary where keys are display_role names
                           and values are lists of employee names under that role.
    """

    # Start with a defaultdict so every role key auto-creates a list
    employee_group = {}

    # Get the role mapping for this department (which defines header order)
    role_map = config_object_role_map.get(dept.dept_name, {})
    clean_roles = role_map.get('clean_roles', [])
    role_labor_tracker_enabled_bool_list = role_map.get('labor_tracker_enabled', [])
    role_index = 0

    # This will track employees who were placed correctly in a role
    all_sorted = []

    # First, sort employees according to the preferred role order
    for i in range(len(clean_roles)):
        for emp in dept.employees:
            for shift in emp.shifts:
                if shift.day_index == day_index and emp.display_role == clean_roles[role_index] and emp not in all_sorted:
                    if emp.display_role not in employee_group:
                        employee_group[emp.display_role] = ([emp], role_labor_tracker_enabled_bool_list[role_index])
                    else:
                        employee_group[emp.display_role][0].append(emp)

                    all_sorted.append(emp)

        role_index += 1

    # After the preferred roles, assign any remaining employees
    for emp in dept.employees:
        if emp not in all_sorted:
            for shift in emp.shifts:
                if shift.day_index == day_index:
                    if emp.display_role not in employee_group:
                        employee_group[emp.display_role] = ([emp], 1)
                    else:
                        employee_group[emp.display_role][0].append(emp)

    return employee_group


def detect_new_roles_and_departments(store_object, config_object):
    """
    Detects any roles or departments in the store_object that are not present in ROLE_MAP.

    Args:
        store_object (Store): The store object containing all departments and employees.
        config_handler_object (ConfigHandler): The ConfigHandler instance with role maps.

    Returns:
        dict: {
            "new_departments": [list of dept names],
            "new_roles": [list of roles]
        }
    """
    role_map = config_object.settings_role_map
    extant_roles_set = set()
    departments_aleady_in_settings = set(role_map.keys())
    blacklist_dept = config_object.settings_new_dept_or_role_blacklist.get("departments", [])
    blacklist_role = config_object.settings_new_dept_or_role_blacklist.get("roles", [])

    # 1. Build extant roles set across all departments
    for dept_name, dept_map in role_map.items():
        extant_roles_set.update(dept_map.get("roles", []))

    # 2. Check for new departments and roles
    emp_objects_with_unseen_roles = []
    unseen_departments = []

    for dept in store_object.department_list:
        if dept.dept_name not in blacklist_dept:
            if dept.dept_name not in departments_aleady_in_settings:
                unseen_departments.append(dept.dept_name)

            for emp in dept.employees:
                if emp.role not in blacklist_role:
                    if emp.role not in extant_roles_set:
                        emp_objects_with_unseen_roles.append(emp)

    return {
        "new_departments": sorted(list(unseen_departments)),
        "emp_objects_with_unseen_roles": list(emp_objects_with_unseen_roles)
    }


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
        for row in inputCSV:
            for cell in row:
                match = re.search(r'Store:(\d+)', cell)
                if match:
                    return match.group(1)

    return None


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


def parse_shift_cell(shift_cell, index):
    """
    Parses a cell containing shift information and returns a list of Shift objects.

    Handles both single and split shifts. For split shifts, paid hours are now
    proportionally allocated to each segment.

    Args:
        shift_cell (str): The cell string from the name_row that may contain shift data.
        index (int): The column index where the shift is located.

    Returns:
        list of Shift objects.
    """
    regex_double = r'(\d+:\d+\w+)-(\d+:\d+\w+)\n(\d+:\d+\w+)-(\d+:\d+\w+)'
    regex_single = r'(\d+:\d+\w+)-(\d+:\d+\w+)'
    regex_duration = r'Hrs:(.+)'

    double = re.search(regex_double, shift_cell)
    single = re.search(regex_single, shift_cell)
    duration = re.search(regex_duration, shift_cell)

    if double and duration:
        total_paid_hours_across_both_shifts_in_seconds = (
            float((duration.group(1))) * 60 * 60
        )

        first_shift_start = datetime.datetime.strptime(double.group(1), '%I:%M%p')
        first_shift_end = datetime.datetime.strptime(double.group(2), '%I:%M%p')
        if first_shift_end <= first_shift_start:
            first_shift_end += datetime.timedelta(days = 1)
        first_shift_duration = (first_shift_end - first_shift_start)
        first_shift_duration_in_seconds = first_shift_duration.total_seconds()

        second_shift_start = datetime.datetime.strptime(double.group(3), '%I:%M%p')
        second_shift_end = datetime.datetime.strptime(double.group(4), '%I:%M%p')
        if second_shift_end <= second_shift_start:
            second_shift_end += datetime.timedelta(days=1)
        second_shift_duration = (second_shift_end - second_shift_start)
        second_shift_duration_in_seconds = second_shift_duration.total_seconds()

        if first_shift_duration_in_seconds >= (6 * 60 * 60):
            # Subtract Half Hour for Lunch if Shift Duration is Greater Than or Equal to Six Hours
            first_shift_duration_in_seconds = (
                first_shift_duration_in_seconds - (0.5 * 60 * 60)
            )
            first_shift_duration_in_seconds = int(first_shift_duration_in_seconds)

        if second_shift_duration_in_seconds >= (6 * 60 * 60):
            # Subtract Half Hour for Lunch if Shift Duration is Greater Than or Equal to Six Hours
            second_shift_duration_in_seconds = (
                second_shift_duration_in_seconds - (0.5 * 60 * 60)
            )
            second_shift_duration_in_seconds = int(second_shift_duration_in_seconds)

        if total_paid_hours_across_both_shifts_in_seconds != (
            first_shift_duration_in_seconds + second_shift_duration_in_seconds
        ):
            if first_shift_duration_in_seconds > second_shift_duration_in_seconds:
                first_shift_duration_in_seconds = (
                    total_paid_hours_across_both_shifts_in_seconds
                    - second_shift_duration_in_seconds
                )
            if second_shift_duration_in_seconds > first_shift_duration_in_seconds:
                second_shift_duration_in_seconds = (
                    total_paid_hours_across_both_shifts_in_seconds
                    - first_shift_duration_in_seconds
                )

        final_paid_time_first_shift = round(
            (first_shift_duration_in_seconds / 60 / 60)
        )
        final_paid_time_second_shift = round(
            (second_shift_duration_in_seconds / 60 / 60)
        )

        return [
            m.Shift(
                index,
                first_shift_start.time(),
                first_shift_end.time(),
                final_paid_time_first_shift,
            ),
            m.Shift(
                index,
                second_shift_start.time(),
                second_shift_end.time(),
                final_paid_time_second_shift,
            ),
        ]

    if single and duration:
        return [
            m.Shift(
                index,
                datetime.datetime.strptime(single.group(1), '%I:%M%p').time(),
                datetime.datetime.strptime(single.group(2), '%I:%M%p').time(),
                float(duration.group(1)),
            )
        ]

    return []


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
                                print(f"Log: Updated: {name} -> {emp.name}")


# Rendering Funcitons
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


def insert_footer(ws, store_number):
    """
    Adds a footer with the store number and generation date to the bottom-right corner of the printed page.
    """
    date_generated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    ws.oddFooter.right.text = f"Store {store_number} | Generated {date_generated}"
    ws.oddFooter.right.size = 8
    ws.oddFooter.right.font = "Calibri"


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


def insert_labor_tracker(ws, labor_data, title, start_row, start_col = 10):
    """
    Inserts a small labor tracker table into the worksheet.
    """
    from openpyxl.styles import Font, Alignment, Border, Side

    # Borders
    thick_border = Border(
        left=Side(style = "thick"),
        right=Side(style = "thick"),
        top=Side(style = "thick"),
        bottom=Side(style = "thick")
    )

    thin_border = Border(
        left=Side(style = "thin"),
        right=Side(style = "thin"),
        top=Side(style = "thin"),
        bottom=Side(style = "thin")
    )

    # 1. Title row
    ws.merge_cells(start_row = start_row, start_column=start_col, end_row = start_row, end_column = start_col + 4)

    for col in range(start_col, start_col + 5):
        cell = ws.cell(row = start_row, column = col)
        cell.border = thick_border
        cell.font = Font(bold = True, size = 12, name='Calibri')
        cell.alignment = Alignment(horizontal="center", vertical = "center")

    title_cell = ws.cell(row = start_row, column = start_col)
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


def insert_daily_notes(ws, start_row = 4, start_col = 10, height = 20, width = 5):
    """
    Inserts 'Daily Notes', a blank space to write, in place of labor trackers if chosen by user.

    Args:
        ws (Worksheet): The Excel worksheet.
        start_row (int): Row to place the header.
        start_col (int): Starting column for the rectangle.
        height (int): Number of rows the rectangle should extend down.
        width (int): Number of columns the rectangle should span.
    """
    from openpyxl.styles import Font, Alignment, Border, Side

    # Borders
    thick_border = Border(
        left = Side(style = "thick"),
        right = Side(style = "thick"),
        top = Side(style = "thick"),
        bottom = Side(style = "thick")
    )
    thin_border = Border(
        left = Side(style = "thin"),
        right = Side(style = "thin"),
        top = Side(style = "thin"),
        bottom = Side(style = "thin")
    )

    # 1. Insert "Daily Notes" header
    ws.merge_cells(
        start_row = start_row,
        start_column = start_col,
        end_row = start_row,
        end_column = start_col + width - 1
    )
    for c in range(start_col, start_col + width):
        cell = ws.cell(row = start_row, column = c)
        cell.border = thick_border

    header_cell = ws.cell(row = start_row, column = start_col)
    header_cell.value = "Daily Notes"
    header_cell.font = Font(bold = True, size = 14, name = 'Calibri')
    header_cell.alignment = Alignment(horizontal = "center", vertical = "center")

    # 2. Create rectangle area below header
    for r in range(start_row + 1, start_row + 1 + height):
        for c in range(start_col, start_col + width):
            cell = ws.cell(row = r, column = c)
            cell.value = ""  # leave blank for notes
            cell.border = thin_border
            cell.alignment = Alignment(horizontal = "left", vertical = "top")

    # Merge cells for a large writing area
    ws.merge_cells(
        start_row = start_row + 1,
        start_column = start_col,
        end_row = start_row + height,
        end_column = start_col + width - 1
    )


def insert_headers_and_employees(ws, employee_group_dict, day_index, start_row = 4):
    role_names = list(employee_group_dict.keys())
    current_row = start_row

    for i, (employee_list, is_enabled) in enumerate(employee_group_dict.values()):
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
    ws.merge_cells(start_row=current_row, start_column=3, end_row=current_row, end_column=6)

    #6 Insert Label
    label_cell = ws.cell(row=current_row, column=3)
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
        employee_group_dict (dict): display_role -> (list of Employee objects, tracker_enabled).
        time_blocks (list): The list of time blocks to calculate coverage.
        day_index (int): Which day to calculate (0=Sunday, 6=Saturday).
        start_row (int): The row to start inserting trackers.
        start_col (int): The column to insert trackers (default 10).

    Returns:
        int: The next empty row after all trackers.
    """
    role_display_names = list(employee_group_dict.keys())
    grouped_employees_by_role = list(employee_group_dict.values())
    current_row = start_row

    for i, role_name in enumerate(role_display_names):
        employees_with_shifts_today, tracker_enabled = grouped_employees_by_role[i]

        if tracker_enabled == 0:
            continue #return to start of loop without rendering labor tracker.

        if tracker_enabled == 1 and len(employees_with_shifts_today) > 1:
            block_hours_total = defaultdict(int)

            for emp in employees_with_shifts_today:
                for shift in emp.shifts:
                    if shift.day_index == day_index:
                        overlaps = calculate_block_overlaps(shift.start_time, shift.end_time, time_blocks)
                        for block, hours in overlaps.items():
                            block_hours_total[block] += hours

            insert_labor_tracker(
                ws,
                block_hours_total,
                f"Labor Coverage: {role_name}",
                start_row = current_row,
                start_col = start_col
            )

            current_row += 5  # move down after each tracker

    return current_row


def insert_effective_shopper_table(ws, employee_group, expeditor_requirements, time_blocks, day_index, start_row=4, start_col=11):
    """
    Insert a table showing effective shopper hours into a worksheet.
    """

    # Borders
    thick_border = Border(
        left = Side(style = "thick"),
        right = Side(style = "thick"),
        top = Side(style = "thick"),
        bottom = Side(style = "thick")
    )

    thin_border = Border(
        left = Side(style = "thin"),
        right = Side(style = "thin"),
        top = Side(style = "thin"),
        bottom = Side(style = "thin")
    )

    # --- 1. Write Header ---
    ws.merge_cells(start_row = start_row, start_column = start_col, end_row = start_row + 1, end_column = start_col + 3)

    # Set up header
    header_cell = ws.cell(row = start_row, column = start_col)
    header_cell.alignment = Alignment(horizontal = "center", vertical = "center", wrap_text = True)

    # Define rich text font styles
    title_font = InlineFont(sz = 12, b = True, rFont = "Calibri")
    subtitle_font = InlineFont(sz = 8, b = False, rFont = "Calibri")
    rich_text = CellRichText([
        TextBlock(text="Effective Shopper Hours (ESH)\n", font = title_font),
        TextBlock(text="Total Hours - [Estimated 'Non-Shopping' & Break Hours] = ESH", font = subtitle_font)
    ])
    header_cell.value = rich_text

    # Apply border to all merged cells manually
    for row in ws.iter_rows(min_row = start_row, max_row = start_row+1, min_col = start_col, max_col = start_col + 3):
        for cell in row:
            cell.border = thick_border

    # Move to next row for column labels
    current_row = start_row + 2

    # --- 2. Write Table Column Headers ---
    headers = ["Time Range", "Non-Shopping Hrs", "ESH", ""]
    header_font = Font(name="Calibri", bold=True)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for col_offset, header_text in enumerate(headers):
        cell = ws.cell(row=current_row, column=start_col + col_offset)
        cell.value = header_text
        cell.alignment = header_alignment
        cell.border = thin_border
        if col_offset == 1:  # "Expo Hrs Req" column smaller font
            cell.font = Font(name="Calibri", bold=True, size=8)
        else:
            cell.font = header_font

    current_row += 1  # move to first data row

    # --- 3. Calculate All Employee Overlaps ---
    total_overlaps = defaultdict(float)
    for employees, _ in employee_group.values():
        for emp in employees:
            for shift in emp.shifts:
                if shift.day_index == day_index:
                    overlaps = calculate_block_overlaps(shift.start_time, shift.end_time, time_blocks)
                    for block_key, hours in overlaps.items():
                        total_overlaps[block_key] += hours

    # --- 4. Write Data Rows ---
    for i, block in enumerate(time_blocks):
        block_start, block_end, _ = block
        block_name = f"{block[2]} = {block_start}-{block_end}"

        actual_total_hours = total_overlaps.get(block_name, 0)
        required_expo_hours = expeditor_requirements.get(i, 0)
        effective_hours = actual_total_hours - required_expo_hours

        # Write time range
        time_range_cell = ws.cell(row = current_row, column = start_col)
        time_range_cell.value = f"{block_start} - {block_end}"
        time_range_cell.alignment = header_alignment
        time_range_cell.border = thin_border

        # Write required expo hours
        required_expo_cell = ws.cell(row=current_row, column = start_col + 1)
        required_expo_cell.value = required_expo_hours
        required_expo_cell.alignment = header_alignment
        required_expo_cell.border = thin_border

        # Write effective shopper hours
        esh_cell = ws.cell(row = current_row, column = start_col + 2)
        esh_cell.value = round(effective_hours, 2)
        esh_cell.alignment = header_alignment
        esh_cell.border = thin_border

        current_row += 1

    # --- 5. Merge and sum every 3-hour chunk ---
    for group_start_row in range(start_row + 3, current_row, 3):
        sum_value = sum(
            ws.cell(row = r, column = start_col + 2).value
            for r in range(group_start_row, min(group_start_row + 3, current_row))
        )
        ws.merge_cells(
            start_row=group_start_row,
            start_column = start_col + 3,
            end_row=min(group_start_row + 2, current_row - 1),
            end_column=start_col + 3
        )
        merged_cell = ws.cell(row = group_start_row, column = start_col + 3)
        merged_cell.value = round(sum_value, 2)
        merged_cell.alignment = header_alignment
        merged_cell.border = thin_border

        # Fill borders for empty cells too
        for r in range(group_start_row + 1, min(group_start_row + 3, current_row)):
            empty_cell = ws.cell(row = r, column = start_col + 3)
            empty_cell.border = thin_border
