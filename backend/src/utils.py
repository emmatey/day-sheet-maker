import re
import csv
import models as m
import datetime
from copy import copy
from collections import defaultdict
from openpyxl.styles import Border, Side, Font, Alignment


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
    WEEKDAYS = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    with open(csv_path, "r") as f:
        schedule = csv.reader(f)
        header_row = []
        for row in schedule:
            if row and row[0].strip() == "Name":
                header_row = row
                break

    m = {}
    dates = [None]*7
    pat = re.compile(r'^(Sun|Mon|Tue|Wed|Thu|Fri|Sat)\s+(\d+/\d+)\b')
    for col_idx, cell in enumerate(header_row):
        mo = pat.match(cell.strip())
        if mo:
            wk_abbr, date_str = mo.groups()
            day_index = WEEKDAYS.index(wk_abbr)
            m[col_idx] = day_index
            dates[day_index] = date_str
    return m, dates


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

    employee_group = {}

    # Get the role mapping for this department (which defines header order)
    role_map = config_object_role_map.get(dept.dept_name, {})
    raw_roles = role_map.get('roles', [])
    clean_roles = role_map.get('clean_roles', [])
    role_labor_tracker_enabled_bool_list = role_map.get('labor_tracker_enabled', [])

    # This will track employees who were placed correctly in a role
    all_sorted = []

    # First, sort employees according to the preferred role order
    for role_index, clean_role in enumerate(clean_roles):
        for emp in dept.employees:
            if emp in all_sorted:
                continue
            for shift in emp.shifts:
                if shift.day_index == day_index and emp.display_role == clean_role:
                    if emp.display_role not in employee_group:
                        employee_group[emp.display_role] = ([emp], role_labor_tracker_enabled_bool_list[role_index])
                    else:
                        employee_group[emp.display_role][0].append(emp)
                    
                    all_sorted.append(emp)
                    break

    # After the preferred roles, assign any remaining employees to largest role
    if employee_group:
        most_populous_role = "Default"
        role_len = 0
        for role_name, values in employee_group.items():
            if len(values[0]) > role_len:
                role_len = len(values[0])
                most_populous_role = role_name
    
    for emp in dept.employees:
        if emp in all_sorted:
            continue
        if any(shift.day_index == day_index for shift in emp.shifts):
            employee_group[most_populous_role][0].append(emp)
            all_sorted.append(emp)

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
    departments_already_in_settings = set(role_map.keys())
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
            if dept.dept_name not in departments_already_in_settings:
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

        final_paid_time_first_shift = first_shift_duration_in_seconds / 60 / 60
        final_paid_time_second_shift = second_shift_duration_in_seconds / 60 / 60

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


def disambiguate_duplicate_names(store, debug=False):
    """
    Adds middle initials to employees who share the same name within the same department.
    Only employees that 1) collide on name and 2) have a middle_initial are modified.

    Returns:
        int: count of updated employee names
    """
    updated = 0

    for department in store.department_list:
        by_name = defaultdict(list)

        # Group employees by their current (cleaned) name string
        for emp in department.employees:
            base = (emp.name or "").strip()
            if base:
                by_name[base].append(emp)

        # For any name that appears more than once, try to disambiguate
        for base_name, emps in by_name.items():
            if len(emps) <= 1:
                continue

            for emp in emps:
                mi = (getattr(emp, "middle_initial", "") or "").strip()
                if not mi:
                    # No middle initial available → leave as-is
                    continue

                parts = emp.name.split()
                # If it already has the same middle initial after the first name, skip (idempotent)
                if len(parts) >= 3:
                    mid_token = parts[1].rstrip(".").upper()
                    if mid_token == mi.upper():
                        continue

                # Build the new name safely
                if len(parts) >= 2:
                    first = parts[0]
                    last = " ".join(parts[1:])  # preserve multi-part last names
                else:
                    # Single token name; treat everything as "first"
                    first = parts[0]
                    last = ""

                new_name = f"{first} {mi.upper()} {last}".strip()

                if new_name != emp.name:
                    if debug:
                        print(f"Log: Updated: {emp.name} -> {new_name}")
                    emp.name = new_name
                    updated += 1

    return updated


def dept_scope_time_blocks(dept_name, employee_group, config_object, day_index):
  time_blocks_master = config_object.settings_time_blocks
  time_blocks = time_blocks_master[dept_name]
  
  totals = defaultdict(float)

  for employee_list, _bool in employee_group.values():
    for employee in employee_list:
      for shift in employee.shifts:
        if shift.day_index == day_index:
          overlaps = calculate_block_overlaps(shift.start_time, shift.end_time, time_blocks)
          for name, hours in overlaps.items():
            totals[name] += hours

  return(totals)


# Rendering Funcitons
def insert_title_cell(ws, day, column_day_map, dept_name=None):
    _, dates = column_day_map
    days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    cell = ws.cell(row=1, column=1)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    try:
        from openpyxl.cell.rich_text import TextBlock, CellRichText
        from openpyxl.cell.text import InlineFont

        top_sz = 16
        sub_sz = 10

        blocks = [
            TextBlock(text=f"{days[day]} - {dates[day]}\n",
                      font=InlineFont(sz=top_sz, b=True, rFont="Calibri")),
        ]
        if dept_name:
            blocks.append(TextBlock(text=f"{dept_name}",
                                    font=InlineFont(sz=sub_sz, b=False, rFont="Calibri")))

        cell.value = CellRichText(blocks)

    except Exception as e:
        # Fallback to simple string if rich text fails
        if dept_name:
            cell.value = f"{days[day]} - {dates[day]} — {dept_name}"
        else:
            cell.value = f"{days[day]} - {dates[day]}"


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
            target_cell.value = f"{role_name.title()}:"
            target_cell.border = thin_border

        elif col == 2:
            target_cell.value = 'In'
            target_cell.border = thin_border

        elif col == 3:
            target_cell.value = 'Out'
            target_cell.border = thin_border

        elif col == 4:
            target_cell.value = 'Break 1'
            target_cell.border = thin_border

        elif col == 5:
            target_cell.value = 'Lunch'
            target_cell.border = thin_border

        elif col == 6:
            target_cell.value = 'Break 2'
            target_cell.border = thin_border

        elif col == 7:
            target_cell.value = 'Hours'
            target_cell.border = copy(template_cell.border)

        elif col == 8:
            target_cell.value = "Out"
            target_cell.alignment = Alignment(horizontal="center", vertical="center")
            target_cell.border = copy(template_cell.border)

        else:
            target_cell.value = ""
            target_cell.border = copy(template_cell.border)


def insert_labor_tracker(ws, calculate_overlaps_output, title, start_row, start_col = 10):
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
    ws.merge_cells(start_row = start_row, start_column = start_col, end_row = start_row, end_column = start_col + 4)

    for col in range(start_col, start_col + 5):
        cell = ws.cell(row = start_row, column = col)
        cell.border = thick_border
        cell.font = Font(bold = True, size = 12, name='Calibri')
        cell.alignment = Alignment(horizontal="center", vertical = "center", wrap_text = True) 

    title_cell = ws.cell(row = start_row, column = start_col)
    title_cell.value = title

    # 2. Data rows
    current_row = start_row + 1

    for block_name, hours in calculate_overlaps_output.items():
        ws.merge_cells(
            start_row = current_row,
            start_column = start_col,
            end_row = current_row,
            end_column = start_col + 3
        )

        # Format merged block name cells
        for col in range(start_col, start_col + 4):
            block_cell = ws.cell(row = current_row, column = col)
            block_cell.border = thin_border
            block_cell.font = Font(bold = False, size = 12, name = 'Calibri')
            block_cell.alignment = Alignment(horizontal = "left", vertical = "center")

        block_cell = ws.cell(row = current_row, column = start_col)
        block_cell.value = block_name

        # Format the hours cell
        hours_cell = ws.cell(row = current_row, column = start_col+4)
        hours_cell.value = round(hours, 2)
        hours_cell.border = thin_border
        hours_cell.font = Font(bold = True, size = 12, name = 'Calibri')
        hours_cell.alignment = Alignment(horizontal = "center", vertical = "center")

        current_row += 1


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
                f"{role_name} - Scheduled Hours",
                start_row = current_row,
                start_col = start_col
            )
            current_row += 5  # move down after each tracker

    return current_row


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
                    if type(target_cell.value) == float:
                        target_cell.number_format = '0.##'  

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


def insert_effective_shopper_table(
    ws,
    employee_group,
    time_blocks,
    expeditor_requirements,
    day_index,
    start_row = 4,
    start_col = 11
):
    """
    Render the ESH table.
    """
    from collections import defaultdict
    from openpyxl.styles import Alignment, Font, Border, Side
    from openpyxl.cell.rich_text import TextBlock, CellRichText
    from openpyxl.cell.text import InlineFont

    # Styles
    thick_border_all = Border(
        left=Side(style="thick"), right=Side(style="thick"),
        top=Side(style="thick"),   bottom=Side(style="thick")
    )
    thin_border_all = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"),  bottom=Side(style="thin")
    )
    centered_wrapped = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _block_key(start_str, end_str, label):
        return f"{label} = {start_str}-{end_str}"

    def build_hourly_headcount(employee_group, time_blocks, day_index):
        totals = defaultdict(float)
        for employees_in_role, _enabled in employee_group.values():
            for employee in employees_in_role:
                for shift in getattr(employee, "shifts", []):
                    if shift.day_index == day_index:
                        overlaps = calculate_block_overlaps(shift.start_time, shift.end_time, time_blocks)
                        for k, hours in overlaps.items():
                            totals[k] += hours
        return totals

    def compute_effective_shoppers(total_overlap_by_key, time_blocks, expeditor_requirements):
        req_list, esh_list = [], []
        for i, (start_str, end_str, label) in enumerate(time_blocks):
            key = _block_key(start_str, end_str, label)
            actual_total = total_overlap_by_key.get(key, 0.0)
            if isinstance(expeditor_requirements, (list, tuple)):
                req = expeditor_requirements[i] if i < len(expeditor_requirements) else 0
            else:
                req = expeditor_requirements.get(i, 0)
            esh = actual_total - req
            req_list.append(req)
            esh_list.append(esh)
        return req_list, esh_list

    # ---------------------------
    # 1) Header block
    # ---------------------------
    header_first_row = start_row
    header_first_col = start_col
    header_last_row  = start_row + 1
    header_last_col  = start_col + 3

    ws.merge_cells(start_row = header_first_row, start_column = header_first_col,
                   end_row=  header_last_row,  end_column = header_last_col)

    header_cell = ws.cell(row=header_first_row, column=header_first_col)
    try:
        header_cell.value = CellRichText([
            TextBlock(text="Effective Shopper Hours (ESH)\n",
                      font=InlineFont(sz=12, b=True, rFont="Calibri")),
            TextBlock(text="Total Hours - [Estimated 'Non-Shopping' & Break Hours] = ESH",
                      font=InlineFont(sz=8, b=False, rFont="Calibri")),
        ])
    except Exception:
        header_cell.value = (
            "Effective Shopper Hours (ESH)\n"
            "Total Hours - [Estimated 'Non-Shopping' & Break Hours] = ESH"
        )

    for row in ws.iter_rows(min_row = header_first_row, max_row = header_last_row,
                            min_col = header_first_col, max_col = header_last_col):
        for cell in row:
            cell.border = thick_border_all
            cell.alignment = centered_wrapped

    # ----------------------
    # 2) Column label row
    # ----------------------
    current_row = start_row + 2
    column_headers = ["Time Range", "Non-Shopping Hrs", "ESH", ""]
    for offset, header_text in enumerate(column_headers):
        hc = ws.cell(row=current_row, column=start_col + offset)
        hc.value = header_text
        hc.alignment = centered_wrapped
        hc.border = thin_border_all
        if header_text == "Non-Shopping Hrs":
            hc.font = Font(name="Calibri", bold=True, size=8)
        else:
            hc.font = Font(name="Calibri", bold=True)

    current_row += 1
    first_data_row_index = current_row

    # --------------------------
    # 3) Build totals & ESH
    # --------------------------
    total_overlap_by_key = build_hourly_headcount(employee_group, time_blocks, day_index)
    req_per_hour, esh_per_hour = compute_effective_shoppers(total_overlap_by_key, time_blocks, expeditor_requirements)

    # --------------------------
    # 4) Render rows
    # --------------------------
    for hour_index, (start_str, end_str, _label) in enumerate(time_blocks):
        req = req_per_hour[hour_index]
        esh = esh_per_hour[hour_index]

        # Time Range
        c = ws.cell(row=current_row, column=start_col)
        c.value = f"{start_str} - {end_str}"
        c.alignment = centered_wrapped
        c.border = thin_border_all

        # Requirement
        c = ws.cell(row=current_row, column=start_col + 1)
        c.value = req
        c.number_format = '0.##'
        c.alignment = centered_wrapped
        c.border = thin_border_all
        c.font = Font(name="Calibri", bold=True)

        # ESH value
        esh_cell = ws.cell(row=current_row, column=start_col + 2)
        esh_cell.value = esh
        esh_cell.number_format = '0.##'
        esh_cell.alignment = centered_wrapped
        esh_cell.border = thin_border_all

        current_row += 1

    # --------------------------
    # 5) 3-hour merged totals
    # --------------------------
    total_rows = len(esh_per_hour)
    merge_col = start_col + 3
    row_ptr = first_data_row_index

    while row_ptr < first_data_row_index + total_rows:
        merge_end_row = min(row_ptr + 2, first_data_row_index + total_rows - 1)
        ws.merge_cells(start_row=row_ptr, start_column=merge_col,
                       end_row=merge_end_row, end_column=merge_col)

        idx0 = row_ptr - first_data_row_index
        idx_end = min(idx0 + 3, total_rows)
        three_hr_sum_esh = round(sum(esh_per_hour[idx0:idx_end]), 2)

        merged_total_cell = ws.cell(row=row_ptr, column=merge_col)
        merged_total_cell.value = three_hr_sum_esh
        merged_total_cell.number_format = '0.##'
        merged_total_cell.alignment = centered_wrapped
        merged_total_cell.border = thin_border_all
        merged_total_cell.font = Font(name="Calibri", bold=False)

        for inner in range(row_ptr + 1, merge_end_row + 1):
            ws.cell(row=inner, column=merge_col).border = thin_border_all

        row_ptr += 3