from pathlib import Path
import sys
import json
from DefaultSettings import default_settings


class ConfigHandler:
    """
    Handles configuration loading, generation, and parsing for the application.
    """

    DEFAULT_FILE_NAME = "settings.json"

    def __init__(self, cfg_file_name=DEFAULT_FILE_NAME):
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
        self.settings_output_orientation_index = 2
        self.settings_save_loc = "DEFAULT_PLACEHOLDER"

        if self.detect_config():
            self.settings = self.read_config()
            self.parse_config(self.settings)
            print(self.set_default_archive())
        else:
            self.generate_default_config()
            self.settings = self.read_config()
            self.parse_config(self.settings)
            print(self.set_default_archive())

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
        # Maps
        self.settings_time_blocks = settings.get("TIME_BLOCKS", {})
        self.settings_role_map = settings.get("ROLE_MAP", {})

        # Toggles
        settings_toggles_dict = settings.get("OUTPUT_SETTINGS", {})
        self.settings_copy_input_to_archive = settings_toggles_dict.get("copy_input_to_archive", True)
        self.settings_output_orientation_index = settings_toggles_dict.get("OUTPUT_ORIENTATION_INDEX", 2)

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

        # Convert EXPEDITOR_REQUIREMENTS keys from strings to ints
        raw_esh = settings.get("EXPEDITOR_REQUIREMENTS", {})
        self.settings_esh = {int(k): v for k, v in raw_esh.items()}

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
