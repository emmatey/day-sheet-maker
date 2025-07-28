from pathlib import Path
import sys
import json
from DefaultSettings import default_settings


class ConfigHandler:
    """
    Handles configuration loading, generation, and parsing for the application.
    """

    DEFAULT_FILE_NAME = "settings.json"

    def __init__(self, cfg_file_name = DEFAULT_FILE_NAME):
        """
        Initializes the config handler.
        Loads or creates a settings file and parses its content into internal attributes.
        """
        self.cfg_file_name = cfg_file_name
        self.working_dir = self.get_working_dir()
        self.config_path = self.working_dir / self.cfg_file_name

        self.settings = {}
        self.settings_time_blocks = {}
        self.settings_role_map = {}
        self.settings_esh = {}
        self.settings_copy_input_to_archive = True
        self.settings_enable_esh = True
        self.settings_save_loc = "DEFAULT_PLACEHOLDER"
        self.settings_blacklists = self.settings.get("Blacklists", {})
        self.settings_new_dept_or_role_blacklist = {
            "departments": self.settings_blacklists.get("departments", []),
            "roles": self.settings_blacklists.get("roles", [])
        }

        if self.detect_config():
            self.settings = self.read_config()
            self.parse_config(self.settings)
        else:
            self.generate_default_config()
            self.settings = self.read_config()
            self.parse_config(self.settings)

    @staticmethod
    def get_project_root():
        """
        Returns the root directory of the project.
        Adjusts if the script is frozen into an executable.
        """
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS)
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def get_working_dir():
        """
        Returns the base working directory.
        If the script is frozen (e.g., packaged as an .exe),
        it returns the temp directory used by the bundled app.
        Otherwise, it returns the directory of the current script file.
        """
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS)
        return Path(__file__).parent

    def generate_default_config(self):
        """
        Writes the default settings to a JSON file in the working directory.
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as config_file:
                json.dump(default_settings, config_file, indent=4)
            print(f"Default config written to: {self.config_path}")
        except Exception as e:
            print(f"Failed to write default config: {e}")
    
    def set_default_archive(self):
        """
        Sets the default save location to a folder named 'Daysheet Archive'
        inside the project root if it hasn't been customized yet.

        Returns:
            str: The resolved save path for confirmation/logging.
        """
        if self.settings_save_loc == "DEFAULT_PLACEHOLDER":
            project_root = self.get_project_root().resolve()
            archive_path = project_root / "Daysheet Archive"

            try:
                with open(self.config_path, 'r', encoding='utf-8') as config_file:
                    settings = json.load(config_file)

                settings["SAVE_LOCATION"]["save_location_string"] = str(archive_path.resolve())
                self.settings_save_loc = str(archive_path)

                with open(self.config_path, 'w', encoding='utf-8') as config_file:
                    json.dump(settings, config_file, indent=4)

            except KeyError as e:
                print(e)
                print("Save Location Setting Inaccessible. Config file may be broken. "
                      "Restore default settings or delete config file.")
                sys.exit(1)

            return f"Save Location Path Is: {self.settings_save_loc}\n"

        else:
            return f"Save Location Path Is: {self.settings_save_loc}\n"

    def detect_config(self):
        """
        Checks if the configuration file exists in the working directory.
        Returns:
            bool: True if found, False otherwise.
        """
        for item in self.working_dir.iterdir():
            if item.name == self.cfg_file_name:
                print(f"Config found: {item.name}")
                return True
        print("Config not found in working directory.")
        return False
    
    def read_config(self):
        """
        Reads the JSON configuration file from disk.

        Returns:
            dict: The loaded configuration settings, or None if failed.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as config_file:
                settings = json.load(config_file)
            print("Config loaded successfully.\n")
            return settings
        except Exception as e:
            print(f"Failed to load config: {e}")
            sys.exit(1)

    def save_config(self):
        """
        Saves the current in-memory settings to the config file.
        """
        try:
            with open(self.config_path, "w") as file:
                json.dump(self.settings, file, indent = 4)
            print("Config updated successfully.\n")
        except Exception as e:
            print(f"Failed to save config: {e}")
            sys.exit(1)
            
    def parse_config(self, settings):
        """
        Parses relevant keys from the configuration dictionary and assigns them to internal attributes.

        Args:
            settings (dict): The loaded configuration dictionary.
        """
        # Maps
        self.settings_time_blocks = settings.get("TIME_BLOCKS", {})
        self.settings_role_map = settings.get("ROLE_MAP", {})
        self.settings_new_dept_or_role_blacklist = self.settings_role_map.get("Blacklists", {})

        # Toggles
        settings_toggles_dict = settings.get("OUTPUT_SETTINGS", {})
        self.settings_copy_input_to_archive = settings_toggles_dict.get("copy_input_to_archive", True)
        self.settings_enable_esh = settings_toggles_dict.get("enable_esh", True)

        # Save Location
        try:
            save_location_dict = settings.get("SAVE_LOCATION", {})
            save_location_string = save_location_dict["save_location_string"]
            self.settings_save_loc = save_location_string
        except KeyError as e:
            print(e)
            print("Save Location Setting Inaccessible. Config file may be broken. "
                  "Restore default settings or delete config file.")
            sys.exit(1)
        
        # Executes method, prints return value
        print(self.set_default_archive())
        
        # Convert EXPEDITOR_REQUIREMENTS keys from strings to ints
        raw_esh = settings.get("EXPEDITOR_REQUIREMENTS", {})
        self.settings_esh = {int(k): v for k, v in raw_esh.items()}
    
    def add_newly_detected_department_to_role_map(self, new_dept_list):
        """
        Add placeholder role map entries for newly detected departments.

        This function is called when departments are found in a schedule 
        that do not exist in the current ROLE_MAP. It creates the required 
        structure (roles, clean_roles, labor_tracker_enabled, default) for 
        each new department, allowing them to be fully configured later.

        Args:
            new_dept_list (list): A list of department names (strings) to add.

        Returns:
            None
        """
        dict_key_dept_value_dict_of_dept_attributes = self.settings_role_map

        for dept in new_dept_list:
            dict_key_dept_value_dict_of_dept_attributes[dept] = {
                "roles": [],
                "clean_roles": [],
                "labor_tracker_enabled": [],
                "default": "Associate"
            }

        self.save_config()
        self.settings_role_map = dict_key_dept_value_dict_of_dept_attributes

    def add_newly_detected_roles_to_relevant_depts(self, list_of_emp_obj_with_new_roles):
        """
        Add newly detected roles to the relevant departments in the ROLE_MAP.

        For each employee in the provided list, this function updates the 
        corresponding department's role configuration by adding the new 
        role to both 'roles' and 'clean_roles', and adjusts 
        'labor_tracker_enabled' to maintain alignment with the total number 
        of roles.

        Args:
            list_of_emp_obj_with_new_roles (list): A list of Employee objects 
                that contain roles not currently present in ROLE_MAP.

        Returns:
            None
        """
        dict_key_dept_value_dict_of_dept_attributes = self.settings_role_map

        for emp in list_of_emp_obj_with_new_roles:
            new_role = emp.role
            new_dept = emp.dept

            dict_key_dept_value_dict_of_dept_attributes[new_dept]["roles"].append(new_role)
            dict_key_dept_value_dict_of_dept_attributes[new_dept]["clean_roles"].append(new_role)
            dict_key_dept_value_dict_of_dept_attributes[new_dept]["labor_tracker_enabled"] = [1] * len(
                dict_key_dept_value_dict_of_dept_attributes[new_dept]["clean_roles"]
            )

        self.save_config()

    def add_time_blocks_for_new_depts(self, new_dept_list):
        """
        Adds placeholder time blocks for newly detected departments.

        This function updates the TIME_BLOCKS section of the settings with a
        default placeholder block for any department not already present. This
        ensures downstream code (like populate_workbook) can safely access
        time blocks for new departments.

        Args:
            new_dept_list (list): A list of department names (strings) to add
                                  placeholder time blocks for.

        Returns:
            None
        """
        dict_key_dept_value_dict_of_time_blocks = self.settings_time_blocks

        for dept in new_dept_list:
            # Add only if dept not already present
            if dept not in dict_key_dept_value_dict_of_time_blocks:
                dict_key_dept_value_dict_of_time_blocks[dept] = [
                    ["07:00", "12:00", "Morning"],
                    ["12:00", "17:00", "Mid-day"],
                    ["17:00", "22:00", "Evening"]
                ]

        self.save_config()

    def ensure_dept_output_settings(self, new_depts):
        """
        Ensure the OUTPUT_SETTINGS entry for a department exists with defaults.

        Args:
            dept_name (str): The name of the department.
        """
        departments = self.settings.setdefault("OUTPUT_SETTINGS", {}).setdefault("Departments", {})

        for dept in new_depts:
            if dept not in departments:
                departments[dept] = {
                    "orientation_index": 2,
                    "daily_notes_override": False
                }
        
        self.save_config()
    
    def get_dept_output_setting(self, dept_name, key, default = None):
        """
        Retrieve a department-specific output setting.

        Args:
            dept_name (str): The name of the department.
            key (str): The setting key (e.g., 'orientation_index', 'daily_notes_override').
            default (Any): The default value if not found.

        Returns:
            The department-specific setting or default.
        """
        return (
            self.settings.get("OUTPUT_SETTINGS", {})
            .get("Departments", {})
            .get(dept_name, {})
            .get(key, default)
        )