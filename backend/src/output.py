import argparse
import openpyxl
import sys
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
        str: Path to the resulting .csv file
    """
    _, ext = os.path.splitext(input_file)
    ext = ext.lower()

    if ext == '.xlsx':
        try:
            df = pd.read_excel(input_file)
            csv_file = input_file.replace('.xlsx', '_converted.csv')
            df.to_csv(csv_file, index=False)
        except:
            raise ValueError('Invalid Input')
    elif ext == '.csv':
        csv_file = input_file
    else:
        raise ValueError('Invalid Input')

    return csv_file


def FindValidDepts(hrd):
    """
    Filters the department list to only those with at least one employee.

    Parameters:
        hrd: Store object, generated build_store method in builder.py

    Returns:
        List[Department]: List of departments with employees
    """
    valid_depts = []
    for dept in hrd.department_list:
        if len(dept.employees) > 0:
            valid_depts.append(dept.dept_name)
    return valid_depts


def ProcessOutput(save_location_path, output_depts, column_day_map, WEEK_ENDING_DATE):
    """
    Generates staffing sheet outputs for each department in both Table and Wall format.

    Files are saved into a folder named 'daysheets-weekEnding-{WEEK_ENDING_DATE}' inside the given save path.

    Parameters:
        save_location_path (str): Base directory where output folder should be created
        output_depts (List[Department]): Departments to generate sheets for
        column_day_map (Tuple[Dict[int, int], List[str]]): Tuple returned by u.column_day_map
        WEEK_ENDING_DATE (str): The last date in the schedule (e.g. '3/22')

    Returns:
        str: Full path to the created output folder
    """
    outPath = os.path.join(save_location_path, f'DaySheets_WeekEnding_{WEEK_ENDING_DATE}')
    os.makedirs(outPath, exist_ok = True)

    for dept in output_depts:
        for wall_mode in [False, True]:
            templatePath = c.ConfigHandler.get_project_root() / "assets" / "Day Sheet Master.xlsx"
            wb = openpyxl.load_workbook(templatePath)

            is_wall = populate_workbook(wb, dept, column_day_map, is_wall=wall_mode)

            save_name = dept.dept_name.replace(" ", "_")
            if is_wall:
                save_name += "_WALL"

            file_path = os.path.join(outPath, f"{save_name}.xlsx")
            print(f"Saving: {file_path}")
            wb.save(file_path)
            print(f"Saved: {file_path}")

    return outPath


def populate_workbook(wb, dept, column_day_map, is_wall: bool = False):
    """
    Populates each sheet in the given workbook with employee scheduling data
    for the specified department.

    Supports both 'table' and 'wall' layouts, and applies formatting accordingly.

    Parameters:
        wb (Workbook): An openpyxl Workbook object to populate
        dept (Department): The department object to generate a schedule for
        column_day_map (Tuple[Dict[int, int], List[str]]): Mapping of Excel columns to weekdays and a list of dates
        is_wall (bool): If True, apply 'wall mode' formatting and layout

    Returns:
        bool: The is_wall flag, unchanged — used for naming output files
    """
    for day, sheetname in enumerate(wb.sheetnames):
        ws = wb[sheetname]

        # --- Fill Content ---
        employee_group = u.employee_group(dept, day, config_handler_object.settings_role_map)
        time_blocks = config_handler_object.settings_time_blocks.get(dept.dept_name, [])

        u.insert_title_cell(ws, day, column_day_map)
        u.insert_headers_and_employees(ws, employee_group, day)

        # Special case for Hannaford to Go department
        if dept.dept_name == 'Hannaford to Go':
            u.insert_effective_shopper_table(ws, employee_group, config_handler_object.settings_esh, time_blocks, day)
        else:
            u.insert_labor_trackers(ws, employee_group, time_blocks, day)

        # --- Page Setup & Formatting ---
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

        # Margins
        ws.page_margins.left = 0.1
        ws.page_margins.right = 0.1
        ws.page_margins.bottom = 0.25
        ws.page_margins.header = 0.1
        ws.page_margins.footer = 0.1

        # Fit-to-Page
        ws.page_setup.use_fit_to_page = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        ws.page_setup.scale = 100

        # Centering
        ws.print_options.horizontalCentered = True
        ws.print_options.verticalCentered = False

        # Column Widths
        column_widths = {
            'A': 30.0, 'B': 12.0, 'C': 12.0, 'D': 5.0, 'E': 5.0,
            'F': 5.0, 'G': 8.0, 'H': 5.0, 'I': 3.0, 'J': 3.0,
        }
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        if dept.dept_name.lower() == 'hannaford to go':
            ws.column_dimensions['K'].width = 20
            ws.column_dimensions['L'].width = 10
            ws.column_dimensions['M'].width = 5
            ws.column_dimensions['N'].width = 5

        # Print Area
        last_row = ws.max_row
        last_col_letter = openpyxl.utils.get_column_letter(14)  # Column N = 14
        ws.print_area = f"A1:{last_col_letter}{last_row}"

    return is_wall


if __name__ == "__main__":
    desc = (
        """
    Command-line entry point.
    
    Usage:\n
        python output.py <input_file> <save_directory> --departments <DEPT> <DEPT> <DEPT>...]
        python output.py <input_file> --preview 
    
    Positional Arguments:\n
        input_file          Path to the input CSV file. 
        save_directory      Directory where output will be saved. Required for --departments.
    
    Optional Arguments:\n
        --preview           Preview all available departments in the input file. Does not save output.
        --departments       One or more department names to process and output. Requires save_directory.
        **CASE SENSITIVE**
        
        """
    )

    parser = argparse.ArgumentParser(
        description = desc, 
        formatter_class = argparse.RawDescriptionHelpFormatter,
        usage = argparse.SUPPRESS
    )
    parser.add_argument("input_file", type = str)
    parser.add_argument("save_directory", type = str, nargs = '?')
    parser.add_argument("--preview", action = "store_true")
    parser.add_argument("--departments", nargs = '+')
    args = parser.parse_args()

    #Ensure valid argument combinations
    if args.preview:
        if args.departments:
            parser.error("--preview cannot be combined with --departments")
    
    elif args.departments:
        if not args.save_directory:
            parser.error("--departments requires save_directory")
    
    else:
        parser.error("Either --preview or --departments must be provided.")

    #Begin actual logic
    config_handler_object = c.ConfigHandler()
    csv_path = ProcessInput(args.input_file)
    hrd = builder.build_store(csv_path, config_handler_object.settings_time_blocks, config_handler_object.settings_role_map)
    column_day_map = u.column_day_map(csv_path)

    if args.preview:
        preview_depts = FindValidDepts(hrd)
        for dept in preview_depts:
            print(dept)

    elif args.departments:
        #Get Week Ending Date
        _, date_list = column_day_map
        weekEndingDate = date_list[-1]
        WEEK_ENDING_DATE = weekEndingDate.replace('/', '-')

        output_depts = []
        for dept in hrd.department_list:
                if dept.dept_name in args.departments:
                    output_depts.append(dept)

        print(output_depts)
        output_path = ProcessOutput(args.save_directory, output_depts, column_day_map, WEEK_ENDING_DATE)
        print(f"\n Done! Files saved in:\n{output_path}")
