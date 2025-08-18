import utils as u
from builder import build_store
import ConfigHandler as c
from collections import defaultdict

CSV_Path = "/home/emmatey/code/day_sheet_maker/testData/source data/doubleShiftTest.csv"
config_object = c.ConfigHandler()
hrd = build_store(CSV_Path, config_object.settings_time_blocks, config_object.settings_role_map)
time_blocks_master = config_object.settings_time_blocks

def get_employee_group(department_str, day_index, hrd = hrd, config_object = config_object):
  for dept in hrd.department_list:  
    if dept.dept_name == department_str:  
      employee_group = u.employee_group(dept, day_index, config_object.settings_role_map)
      return(employee_group)

employee_group = get_employee_group('Customer Service', 1)

def dept_scope_time_blocks(dept_name, employee_group, config_object, day_index):
  time_blocks_master = config_object.settings_time_blocks
  time_blocks = time_blocks_master[dept_name]
  
  totals = defaultdict(float)

  for employee_list, _bool in employee_group.values():
    for employee in employee_list:
      for shift in employee.shifts:
        if shift.day_index == day_index:
          overlaps = u.calculate_block_overlaps(shift.start_time, shift.end_time, time_blocks)
          for name, hours in overlaps.items():
            totals[name] += hours

  return(totals)

def add_

totals = dept_scope_time_blocks("Customer Service", employee_group, config_object, 1)

print(totals)