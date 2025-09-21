import sys
import pathlib
import subprocess
import shutil


desc = """
        Command-line entry point.

        Usage:
            python output.py <input_file> <save_directory> --output <DEPT>:<MODE> [<DEPT>:<MODE> ...]
            python output.py <input_file> --preview
            python output.py --update_config "<path,comma-separated>^<json>^<update|delete>"
            python output.py --update_config RESET_TO_DEFAULT

        Optional Arguments:
            --preview           Preview all available departments in the input file. Does not save output.
            --output            One or more department output settings.
                                Format: <DEPT>:<MODE>
                                  <DEPT>  = Department name (case-sensitive, must match schedule data)
                                  <MODE>  = 0 = Table, 1 = Wall, 2 = Both
                                Example:
                                  python output.py schedule.csv ./out --output Bakery:2 Deli:0 Produce:1
            --update_config     Apply a single config change (no input file required). See usage above.
        """

path = pathlib.Path(r"C:\Users\Mcrib\Documents\testData\source data")

file_list = [file for file in path.iterdir() if file.is_file()]

for file in file_list:
  err_dir = pathlib.Path(r'C:\Users\Mcrib\documents\testdata\bad-schedules')
  args = f'python output.py "{file}" --preview'
  
  completed_process_instance = subprocess.run(args, capture_output = True)

  return_code = completed_process_instance.returncode
  stdout = completed_process_instance.stdout
  stderr = completed_process_instance.stderr

  if stderr:
    print(f'{file}\n')
    print(f'return code is: {return_code}')
    print(f'{stderr}\n')
    try:
      shutil.copy(file, err_dir)
    except Exception as e: 
      print(e)
      print("shutting down, nighty night :3")
      sys.exit(1)
    
  else:
    print(f'pass\n{file}\n')
    continue