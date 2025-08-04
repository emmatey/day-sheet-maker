import argparse
import openpyxl
import shutil
import os
import pandas as pd
import builder
import utils as u
import ConfigHandler as c


def ProcessInput(input_file):
    """
    Validates and processes the input file.

    If the file is an .xlsx, converts it to .csv.
    If the file is already a .csv, uses it as-is.
    Raises an error if the file type is unsupported.

    Parameters:
        input_file (str): Path to the input file (.csv or .xlsx)

    Returns:
        Tuple[str, str]: Path to the resulting .csv file and original input path
    """
    _, ext = os.path.splitext(input_file)
    ext = ext.lower()

    if ext == '.xlsx':
        try:
            dataframe = pd.read_excel(input_file)
            csv_file = input_file.replace('.xlsx', '_converted.csv')
            dataframe.to_csv(csv_file, index=False)
        except:
            raise ValueError('Invalid Input, Could not Convert to CSV')
    elif ext == '.csv':
        csv_file = input_file
    else:
        raise ValueError(f'Invalid Input - input is: {input_file}')

    return csv_file, input_file


def FindValidDepts(hrd):
    """
    Filters the department list to only those with at least one employee.

    Parameters:
        hrd: Store object from builder.build_store()

    Returns:
        List[str]: List of department names with at least one employee
    """
    valid_depts = []
    for dept in hrd.department_list:
        if len(dept.employees) > 0:
            valid_depts.append(dept.dept_name)
    return valid_depts


def CreateWorkbook(wall_mode_list, output_depts, column_day_map, outPath):
    """
    Creates and saves Excel workbooks for each department in specified wall/table format(s).

    Parameters:
        wall_mode_list (List[bool]): List of wall mode values to use (e.g., [True], [False], [True, False])
        output_depts (List[Department]): Departments to process
        column_day_map: Column-to-day mapping
        outPath (str): Directory to save generated Excel files
    """
    for dept in output_depts:
        for wall_mode in wall_mode_list:
            templatePath = c.ConfigHandler.get_project_root() / "assets" / "Day Sheet Master.xlsx"
            wb = openpyxl.load_workbook(templatePath)

            is_wall = populate_workbook(
                wb,
                dept,
                column_day_map,
                is_wall = wall_mode
            )

            save_name = dept.dept_name.replace(" ", "_")
            if is_wall:
                save_name += "_WALL"

            file_path = os.path.join(outPath, f"{save_name}.xlsx")
            print(f"Log: Saving: {file_path}")
            wb.save(file_path)
            print(f"Log: Saved: {file_path}")


def ProcessOutput(save_location_path, WEEK_ENDING_DATE, STORE_NUMBER, settings_object, input_file_path, output_dict, column_day_map, hrd):
    """
    Generates staffing sheet outputs for selected departments in Table and/or Wall formats.

    Parameters:
        save_location_path (str): Base directory where output folder should be created
        WEEK_ENDING_DATE (str): The last date in the schedule (e.g., '3/22')
        settings_object: ConfigHandler object with user settings
        input_file_path (str): Path to the original input file

    Returns:
        str: Full path to the created output folder
    """
    outPath = os.path.join(save_location_path, f'DaySheets_{STORE_NUMBER}_WeekEnding_{WEEK_ENDING_DATE}')
    os.makedirs(outPath, exist_ok=True)

    if settings_object.settings_copy_input_to_archive:
        shutil.copy(input_file_path, outPath)
    else:
        print("Log: settings_copy_input_to_archive = False")

    wall_mode_options = [
        [False],       # 0 = TABLE_ONLY
        [True],        # 1 = WALL_ONLY
        [True, False]  # 2 = BOTH
    ]

    for dept_name, orientation_index in output_dict.items():
        wall_mode_list = wall_mode_options[orientation_index]
        dept_obj = next((d for d in hrd.department_list if d.dept_name == dept_name), None)
        if not dept_obj:
            print(f"Log: Warning: Department '{dept_name}' not found in data")
            continue

        CreateWorkbook(
            wall_mode_list,
            [dept_obj],
            column_day_map,
            outPath,
        )

    return outPath


def populate_workbook(wb, dept, column_day_map, is_wall: bool = False):
    """
    Populates a workbook with scheduling data for a department.

    Parameters:
        wb (Workbook): openpyxl workbook to populate
        dept (Department): Department object
        column_day_map (Tuple): Day-column mapping and list of schedule dates
        is_wall (bool): Apply wall formatting if True

    Returns:
        bool: The is_wall flag, unchanged
    """
    def print_region_width_adjust(col_num_int):
            last_row = ws.max_row
            last_col_letter = openpyxl.utils.get_column_letter(col_num_int)
            ws.print_area = f"A1:{last_col_letter}{last_row}"

    for day, sheetname in enumerate(wb.sheetnames):
        ws = wb[sheetname]

        employee_group = u.employee_group(dept, day, config_handler_object.settings_role_map)
        time_blocks = config_handler_object.settings_time_blocks.get(dept.dept_name, [])

        u.insert_title_cell(ws, day, column_day_map)
        u.insert_headers_and_employees(ws, employee_group, day)
        u.insert_footer(ws, hrd.store_number)

        # If at least one 'labor tracker table' is enabled, don't draw the 'daily notes'
        # Employee group = ({dict}, bool)
        role_enabled = employee_group.values()
        role_enabled_list = []
        role_enabled_notes_override_token = True
        for i in role_enabled:
            role_enabled_list.append(i[-1])
        for i in role_enabled_list:
            if i != 0:
                role_enabled_notes_override_token = False


        if "to go" in dept.dept_name.lower() and config_handler_object.settings_enable_esh == True:
            time_blocks = config_handler_object.settings_time_blocks.get("Hannaford to Go ESH", [])

            u.insert_effective_shopper_table(ws, employee_group, config_handler_object.settings_esh, time_blocks, day)

            ws.column_dimensions['K'].width = 20
            ws.column_dimensions['L'].width = 10
            ws.column_dimensions['M'].width = 5
            ws.column_dimensions['N'].width = 5

        elif role_enabled_notes_override_token == True:
            u.insert_daily_notes(ws)
        else:
            u.insert_labor_trackers(ws, employee_group, time_blocks, day)

        # Formatting based on layout
        if is_wall:
            ws.column_dimensions['D'].hidden = True
            ws.column_dimensions['E'].hidden = True
            ws.column_dimensions['F'].hidden = True
            ws.column_dimensions['H'].hidden = True
            ws.page_margins.top = 1.25
            ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT
        else:
            ws.column_dimensions['D'].hidden = False
            ws.column_dimensions['E'].hidden = False
            ws.column_dimensions['F'].hidden = False
            ws.column_dimensions['H'].hidden = False
            ws.page_margins.top = 0.5
            ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE

        # Column widths
        column_widths = {
            'A': 30.0, 'B': 12.0, 'C': 12.0, 'D': 5.0, 'E': 5.0,
            'F': 5.0, 'G': 8.0, 'H': 5.0, 'I': 3.0, 'J': 3.0,
        }
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        # Page margins
        ws.page_margins.left = 0.1
        ws.page_margins.right = 0.1
        ws.page_margins.bottom = 0.25
        ws.page_margins.header = 0.1
        ws.page_margins.footer = 0.1

        # Fit to page
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        ws.page_setup.scale = None

        # Centering
        ws.print_options.horizontalCentered = True
        ws.print_options.verticalCentered = False

        print_region_width_adjust(14)

    return is_wall


if __name__ == "__main__":
    desc = """
        Command-line entry point.

        Usage:
            python output.py <input_file> <save_directory> --output <DEPT>:<MODE> [<DEPT>:<MODE> ...]
            python output.py <input_file> --preview

        Positional Arguments:
            input_file          Path to the input CSV file.
            save_directory      Directory where output will be saved. Required for --output.

        Optional Arguments:
            --preview           Preview all available departments in the input file. Does not save output.
            --output            One or more department output settings.
                                Format: <DEPT>:<MODE>
                                  <DEPT>  = Department name (case-sensitive, must match schedule data)
                                  <MODE>  = 0 = Table, 1 = Wall, 2 = Both
                                Example:
                                  python output.py schedule.csv ./out --output Bakery:2 Deli:0 Produce:1
        """

    config_handler_object = c.ConfigHandler()

    parser = argparse.ArgumentParser(
        description = desc,
        formatter_class = argparse.RawDescriptionHelpFormatter,
        usage=argparse.SUPPRESS
    )

    parser.add_argument("input_file", type=str)
    parser.add_argument("save_directory", type=str, default=config_handler_object.settings_save_loc, nargs="?")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument(
        "--output",
        nargs='+',
        help="Departments and orientation index in the form DeptName:Index (Index = 0=Table, 1=Wall, 2=Both)"
    )
    args = parser.parse_args()

    csv_path, input_file = ProcessInput(args.input_file)
    hrd = builder.build_store(csv_path, config_handler_object.settings_time_blocks, config_handler_object.settings_role_map)
    column_day_map = u.column_day_map(csv_path)

    new_roles_and_depts = u.detect_new_roles_and_departments(hrd, config_handler_object)
    new_depts = new_roles_and_depts["new_departments"]
    emp_objects_with_new_role = new_roles_and_depts["emp_objects_with_unseen_roles"]
    if new_depts or emp_objects_with_new_role:
        new_roles_set = set()
        for emp_object_with_new_role in emp_objects_with_new_role:
            new_roles_set.add(emp_object_with_new_role.role)
        print(f"Log: New Departments found!: {new_depts}")
        print(f"Log: New Roles found!: {new_roles_set}")

        config_handler_object.add_newly_detected_department_to_role_map(new_depts)
        config_handler_object.add_newly_detected_roles_to_relevant_depts(emp_objects_with_new_role)
        config_handler_object.add_time_blocks_for_new_depts(new_depts)
        hrd = builder.build_store(csv_path, config_handler_object.settings_time_blocks, config_handler_object.settings_role_map)

    if args.preview:
        preview_depts = FindValidDepts(hrd)
        for dept in preview_depts:
            print(dept)

    elif args.output:
        _, date_list = column_day_map
        weekEndingDate = date_list[-1]
        WEEK_ENDING_DATE = weekEndingDate.replace('/', '-')

        output_dict = {}
        for entry in args.output:
            try:
                dept_name, index_str = entry.split(":")
                output_dict[dept_name] = int(index_str)
            except ValueError:
                raise ValueError(f"Invalid format for --output entry: '{entry}'. Expected DeptName:Index")

        print("Log: Output selection received:")
        for dept_name, idx in output_dict.items():
            print(f"Log: {dept_name} → Orientation index {idx}")

        output_path = ProcessOutput(
            args.save_directory,
            WEEK_ENDING_DATE,
            hrd.store_number,
            config_handler_object,
            input_file,
            output_dict,
            column_day_map,
            hrd
        )
        print(f"\nLog: Done! Files saved in:\n{output_path}")

    if "_converted.csv" in csv_path and os.path.exists(csv_path):
        try:
            os.remove(csv_path)
        except Exception as e:
            print(f"Log: Error {e}. \n {csv_path} was unable to be removed\n")
