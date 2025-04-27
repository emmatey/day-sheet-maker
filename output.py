import openpyxl
import openpyxl.utils
import builder
import utils as u

#Global Vairables
csv_path = r"/home/emmatey/dev/Day Sheet Maker/Source Data/output.csv"
hrd = builder.build_store(csv_path)
valid_depts = []
column_day_map = u.column_day_map(csv_path)

#Eliminate Empty Departments Like 'Default'
for dept in hrd.department_list:
    if len(dept.employees) > 0:
        valid_depts.append(dept)

def populate_workbook(wb, dept, column_day_map, is_wall: bool = False):
    for day, sheetname in enumerate(wb.sheetnames):
        ws = wb[sheetname]

        # --- Fill content ---
        employee_group = u.employee_group(dept, day)
        time_blocks = u.TIME_BLOCKS.get(dept.dept_name, [])

        u.insert_title_cell(ws, day, column_day_map)
        u.insert_headers_and_employees(ws, employee_group, day)
        u.insert_labor_trackers(ws, employee_group, time_blocks, day)

        # --- AFTER filling content, set print settings ---
        # --- Config ---
        if is_wall == True: #True meaning wall, therefore hidden columns are true
            ws.column_dimensions['D'].hidden = True
            ws.column_dimensions['E'].hidden = True
            ws.column_dimensions['F'].hidden = True
            ws.column_dimensions['H'].hidden = True
            ws.page_margins.top = 1.25
        if is_wall == False: #False meaning table, hidden columns is false
            ws.column_dimensions['D'].hidden = False
            ws.column_dimensions['E'].hidden = False
            ws.column_dimensions['F'].hidden = False
            ws.column_dimensions['H'].hidden = False
            ws.page_margins.top = 0.5

        if is_wall== True: #True meaning wall, therefore portrait
            ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT
        if is_wall == False: #False meaning table, therefore landsape
            ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE

        #Constants
        ws.print_options.horizontalCentered = True
        ws.print_options.verticalCentered = False

        ws.page_margins.left = 0.1
        ws.page_margins.right = 0.1
        ws.page_margins.bottom = 0.25
        ws.page_margins.header = 0.1
        ws.page_margins.footer = 0.1

        ws.page_setup.use_fit_to_page = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        ws.page_setup.scale = 100

        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 5
        ws.column_dimensions['E'].width = 5
        ws.column_dimensions['F'].width = 5
        ws.column_dimensions['G'].width = 8
        ws.column_dimensions['H'].width = 5
        ws.column_dimensions['I'].width = 3

        # --- Finally, set dynamic print area ---
        last_row = ws.max_row
        last_col_letter = openpyxl.utils.get_column_letter(14)  # Column N
        ws.print_area = f"A1:{last_col_letter}{last_row}"


for dept in valid_depts:
    # Load a fresh master sheet for every department
    wb = openpyxl.load_workbook('Day Sheet Master.xlsx')

    # Fill it
    populate_workbook(wb, dept, column_day_map, True)

    # Save it
    save_name = dept.dept_name.replace(" ", "_")
    wb.save(f"output/{save_name}.xlsx")
