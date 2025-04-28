import openpyxl
import openpyxl.utils
import builder
import utils as u

# --- Global Variables ---
import os
csv_path = r"/home/emmatey/src/Day-Sheet-Maker/Source Data/output.csv"
hrd = builder.build_store(csv_path)
column_day_map = u.column_day_map(csv_path)

# Create output directories if they don't exist
for folder in ["output", "output/table", "output/wall"]:
    if not os.path.exists(folder):
        print(f"Creating directory: {folder}")
        os.makedirs(folder)

# Filter out empty departments
valid_depts = []
for dept in hrd.department_list:
    if len(dept.employees) > 0:
        valid_depts.append(dept)
        print(f"Added department: '{dept.dept_name}'")

# --- Functions ---
def populate_workbook(wb, dept, column_day_map, is_wall: bool = False):
    for day, sheetname in enumerate(wb.sheetnames):
        ws = wb[sheetname]

        # --- Fill Content ---
        employee_group = u.employee_group(dept, day)
        time_blocks = u.TIME_BLOCKS.get(dept.dept_name, [])

        u.insert_title_cell(ws, day, column_day_map)
        u.insert_headers_and_employees(ws, employee_group, day)

        # Special case for Hannaford to Go department
        if dept.dept_name == 'Hannaford to Go':
            u.insert_effective_shopper_table(ws, employee_group, u.EXPEDITOR_REQUIREMENTS["Hannaford to Go"], time_blocks, day)
        else:
            u.insert_labor_trackers(ws, employee_group, time_blocks, day)

        # --- Page Setup & Formatting ---
        # Hide columns if "wall" mode
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

        # Set base column widths (A–M)
        column_widths = {
            'A': 30.0, 'B': 12.0, 'C': 12.0, 'D': 5.0, 'E': 5.0,
            'F': 5.0, 'G': 8.0, 'H': 5.0, 'I': 3.0, 'J': 3.0,
            #'K': 10.0, #'L': 10.0, #'M': 10.0
        }
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        # Customize columns J–M for Hannaford to Go
        if dept.dept_name.lower() == 'hannaford to go':
            ws.column_dimensions['K'].width = 20
            ws.column_dimensions['L'].width = 10
            ws.column_dimensions['M'].width = 5
            ws.column_dimensions['N'].width = 5


        # --- Print Area ---
        last_row = ws.max_row
        last_col_letter = openpyxl.utils.get_column_letter(14)  # Column N = 14
        ws.print_area = f"A1:{last_col_letter}{last_row}"

    # Return the is_wall flag so we know whether to add "_wall" to the filename
    return is_wall

# --- Main Loop ---
print("\nGenerating Day Sheets for all departments...")
print("Files will be saved to:")
print("  - output/table/ - For table versions (landscape orientation)")
print("  - output/wall/ - For wall versions (portrait orientation with hidden columns)")
print()

for dept in valid_depts:
    # Generate both table and wall versions
    for wall_mode in [False, True]:  # First create table version, then wall version
        # Load fresh master template for each department and each version
        wb = openpyxl.load_workbook('Day Sheet Master.xlsx')

        # Populate and get is_wall flag back
        is_wall = populate_workbook(wb, dept, column_day_map, is_wall=wall_mode)

        # Prepare folder path and filename
        folder = "wall" if is_wall else "table"  # Choose folder based on is_wall flag
        save_name = dept.dept_name.replace(" ", "_")

        # Save to appropriate output folder
        output_path = f"output/{folder}/{save_name}.xlsx"
        print(f"Saving {output_path}")
        wb.save(output_path)
