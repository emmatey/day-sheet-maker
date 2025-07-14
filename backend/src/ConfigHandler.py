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
        self.settings_save_loc = ""

        if self.detect_config() is True:
            print(self.set_default_archive())
            self.settings = self.read_config()
            self.parse_config(self.settings)
        else:
            self.generate_default_config()
            self.settings = self.read_config()
            self.parse_config(self.settings)
            print(self.set_default_archive())
        
    @staticmethod
    def get_project_root():
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS)
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def get_working_dir():
        """
        Returns the base working directory.

        If the script is frozen (e.g., packaged as an .exe with PyInstaller),
        it returns the temporary directory used by the bundled app.
        Otherwise, it returns the directory of the current script file.
        """
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS)
        return Path(__file__).parent

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
            return None

    def parse_config(self, settings):
        """
        Parses relevant keys from the configuration dictionary and assigns them to internal attributes.
        Args:
            settings (dict): The loaded configuration dictionary.
        """
        self.settings_time_blocks = settings.get("TIME_BLOCKS", {})
        self.settings_role_map = settings.get("ROLE_MAP", {})
        save_location_dict = settings.get("SAVE_LOCATION", {})
        try:
            save_location_string = save_location_dict["save_location_string"]
            self.settings_save_loc = save_location_string
        except KeyError as e:
            print(e)
            print("Save Location Setting Inaccessable, Config File Could Be Broken, Return to default settings, or delete config file")
            sys.exit(1)
            
        #Converts the 'key' from EXPEDITOR_REQUIREMENTS from a string, as required by JSON to an INT, as assumed by this program.
        raw_esh = settings.get("EXPEDITOR_REQUIREMENTS", {})
        self.settings_esh = {}
        for k, v in raw_esh.items():
            self.settings_esh[int(k)] = v

    def set_default_archive(self):
        """
        At runtime, finds the location of the program and derives default save location from this.

        """
        if self.settings_save_loc == "DEFAULT_PLACEHOLDER":
            project_root = self.get_project_root()
            project_root_resolved = project_root.resolve()
            archive_path = project_root_resolved / "Daysheet Archive"

            with open(self.config_path, 'r', encoding = 'utf-8') as config_file:
                settings = json.load(config_file)
                try:
                    settings["SAVE_LOCATION"]["save_location_string"] = str(archive_path.resolve())
                except KeyError as e:
                    print(e)
                    print("Save Location Setting Inaccessable, Config File Could Be Broken, Return to default settings, or delete config file")
                    sys.exit(1)
                    
                    
            with open(self.config_path, 'w', encoding = 'utf-8') as config_file:
                json.dump(settings, config_file, indent = 4)

        else:
            return f"Save Location Path Setting Exists!{self.settings_save_loc}\n"