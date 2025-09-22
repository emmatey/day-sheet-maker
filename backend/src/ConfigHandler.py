from __future__ import annotations

from pathlib import Path
import os
import sys
import json
import re
import platform

# default_settings is a dict defined in backend/src/DefaultSettings.py
from DefaultSettings import default_settings

class ConfigHandler:
    """
    Handles configuration loading, generation, parsing, and live updates from the UI.
    """

    DEFAULT_FILE_NAME = "settings.json"

    # -------------------------
    # Init / boot
    # -------------------------
    def __init__(self, cfg_file_name: str = DEFAULT_FILE_NAME) -> None:
        self.cfg_file_name = cfg_file_name

        # Where the app code/assets live (read-only when frozen)
        self.app_root = self.get_app_root()

        # Where the user's config lives (Electron passes this via env)
        self.config_dir = self.get_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / self.cfg_file_name

        # Parsed settings (populated by parse_config)
        self.settings: dict = {}
        self.settings_time_blocks: dict = {}
        self.settings_role_map: dict = {}
        self.settings_esh: dict[int, int] = {}

        self.settings_copy_input_to_archive: bool = True
        self.settings_daily_notes: bool = False
        self.settings_enable_esh: bool = True
        self.settings_combined_labor_tracker: bool = False
        self.settings_save_loc: str = "DEFAULT_PLACEHOLDER"

        # Blacklists
        self.settings_blacklists: dict = {}
        self.settings_new_dept_or_role_blacklist: dict = {"departments": [], "roles": []}

        # load or create config
        if self.detect_config():
            try:
                self.settings = self.read_config()
                if not self._is_valid_config(self.settings):
                    self.generate_default_config(force=True)
                    self.settings = self.read_config()

            except:
                # invalid or unreadable → regenerate
                self.generate_default_config()
                self.settings = self.read_config()
        else:
            self.generate_default_config(force=True)
            self.settings = self.read_config()

        self.parse_config(self.settings)


    # -------------------------
    # Paths
    # -------------------------
    @staticmethod
    def get_app_root() -> Path:
        """
        Folder where code/assets live.
        If frozen by PyInstaller, this is the temp extraction dir (read-only).
        """
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS)  # pyright: ignore[reportAttributeAccessIssue]
        # .../backend/src -> project root is two parents up
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def _user_docs_dir() -> Path:
        home = Path.home()
        if platform.system() == "Windows":
            return home / "Documents"
        if platform.system() == "Darwin":
            return home / "Documents"
        # Linux
        xdg = os.environ.get("XDG_DOCUMENTS_DIR")
        return Path(xdg) if xdg else (home / "Documents")

    @staticmethod
    def _default_config_dir() -> Path:
        """
        Sensible per-user config dir if Electron doesn't pass DAYSHEET_CONFIG_DIR.
        """
        home = Path.home()
        if platform.system() == "Windows":
            base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
            return base / "DaySheet Maker"
        if platform.system() == "Darwin":
            return home / "Library" / "Application Support" / "DaySheet Maker"
        # Linux
        base = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
        return base / "day-sheet-maker"

    @classmethod
    def get_config_dir(cls) -> Path:
        """
        Prefer Electron-provided userData path via env.
        """
        env_dir = os.environ.get("DAYSHEET_CONFIG_DIR")
        if env_dir:
            return Path(env_dir)
        return cls._default_config_dir()

    # -------------------------
    # Config I/O
    # -------------------------
    def generate_default_config(self, *, force: bool = False) -> None:
        """
        Write default_settings to settings.json.
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with self.config_path.open("w", encoding="utf-8") as f:
                json.dump(default_settings, f, indent=4)
            print(f"Log: Default config written to: {self.config_path}")
        except Exception as e:
            print(f"Log: Failed to write default config: {e}")

    def detect_config(self) -> bool:
        exists = self.config_path.exists()
        print("Log:", "Config found." if exists else "Config not found; will create defaults.")
        return exists

    def read_config(self) -> dict:
        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                settings = json.load(f)
            print(f"Log: Config loaded successfully. Config path: {self.config_path}")
            return settings
        except Exception as e:
            print(f"Log: Failed to load config: {e}")

    def save_config(self, data: dict | None = None) -> None:
        try:
            if data is not None:
                self.settings = data
            with self.config_path.open("w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            print("Log: Config updated successfully.")
        except Exception as e:
            print(f"Log: Failed to save config: {e}")

    # -------------------------
    # Defaults / parsing
    # -------------------------
    def set_default_archive(self) -> str:
        """
        Ensure a friendly default archive location if still placeholder.
        Uses user's Documents/Daysheet Archive (cross-platform).
        """
        if self.settings_save_loc == "DEFAULT_PLACEHOLDER":
            archive_path = self._user_docs_dir() / "Daysheet Archive"
            try:
                settings = self.read_config()
                settings.setdefault("SAVE_LOCATION", {})["save_location_string"] = str(archive_path.resolve())
                self.settings_save_loc = str(archive_path.resolve())
                self.save_config(settings)
            except KeyError as e:
                print(e)
                print("Err: Save Location Setting inaccessible. Restore defaults or delete config file.")
                raise SystemExit(1)
            return f"Log: Save Location Path Is: {self.settings_save_loc}\n"
        else:
            return f"Log: Save Location Path Is: {self.settings_save_loc}\n"

    def parse_config(self, settings: dict) -> None:
        # Maps
        self.settings_time_blocks = settings.get("TIME_BLOCKS", {})
        self.settings_role_map = settings.get("ROLE_MAP", {})
        self.settings_blacklists = self.settings_role_map.get("Blacklists", {})
        self.settings_new_dept_or_role_blacklist = {
            "departments": self.settings_blacklists.get("departments", []),
            "roles": self.settings_blacklists.get("roles", []),
        }

        # Toggles
        toggles = settings.get("OUTPUT_SETTINGS", {})
        self.settings_copy_input_to_archive = toggles.get("copy_input_to_archive", True)
        self.settings_enable_esh = toggles.get("enable_esh", True)
        self.settings_daily_notes = toggles.get("daily_notes_override", False)
        self.settings_combined_labor_tracker = toggles.get("combined_labor_tracker", False)

        # Save Location
        try:
            self.settings_save_loc = settings.get("SAVE_LOCATION", {})["save_location_string"]
        except KeyError as e:
            print(e)
            print("Err: Save Location Setting inaccessible. Restore defaults or delete config file.")
            raise SystemExit(1)

        # Ensure archive path is set if placeholder
        print(self.set_default_archive())

        # ESH keys as ints
        raw_esh = settings.get("EXPEDITOR_REQUIREMENTS", {})
        self.settings_esh = {int(k): v for k, v in raw_esh.items()}

    # -------------------------
    # Helpers to extend config
    # -------------------------
    def add_newly_detected_department_to_role_map(self, new_dept_list: list[str]) -> None:
        rm = self.settings_role_map
        for dept in new_dept_list:
            rm[dept] = {
                "roles": [],
                "clean_roles": [],
                "labor_tracker_enabled": [],
                "default": "Associate",
            }
        self.settings["ROLE_MAP"] = rm
        self.save_config()
        self.parse_config(self.settings)

    def add_newly_detected_roles_to_relevant_depts(self, list_of_emp_obj_with_new_roles: list) -> None:
        rm = self.settings_role_map
        for emp in list_of_emp_obj_with_new_roles:
            new_role = emp.role
            new_dept = emp.dept
            dept_cfg = rm.setdefault(new_dept, {"roles": [], "clean_roles": [], "labor_tracker_enabled": [], "default": "Associate"})
            roles = dept_cfg.setdefault("roles", [])
            clean_roles = dept_cfg.setdefault("clean_roles", [])
            labor = dept_cfg.setdefault("labor_tracker_enabled", [1] * len(clean_roles))
            if new_role not in roles:
                roles.append(new_role)
                clean_roles.append(new_role)
                labor.append(1)
        self.settings["ROLE_MAP"] = rm
        self.save_config()
        self.parse_config(self.settings)

    def add_time_blocks_for_new_depts(self, new_dept_list: list[str]) -> None:
        tb = self.settings_time_blocks
        for dept in new_dept_list:
            if dept not in tb:
                tb[dept] = [
                    ["07:00", "12:00", "Morning"],
                    ["12:00", "17:00", "Mid-day"],
                    ["17:00", "22:00", "Evening"],
                ]
        self.settings["TIME_BLOCKS"] = tb
        self.save_config()
        self.parse_config(self.settings)

    def _is_valid_config(self, cfg: dict) -> bool:
        try:
            if not isinstance(cfg, dict):
                return False

            Schema = ["TIME_BLOCKS", "ROLE_MAP", "EXPEDITOR_REQUIREMENTS", "SAVE_LOCATION", "OUTPUT_SETTINGS"]
            for role in Schema:
                if role not in cfg:
                    return False
            sl = cfg.get("SAVE_LOCATION", {})
            if not isinstance(sl, dict) or "save_location_string" not in sl:
                return False
            return True
        except Exception:
            print(Exception)
            return False

    # -------------------------
    # React bridge
    # -------------------------
    def apply_react_setting(self, react_string: str) -> str:
        """
        Accepts updates from the Electron UI.

        Formats:
          - "RESET_TO_DEFAULT"
          - "key1,key2,...^<json_value>^update"
          - "key1,key2,...^<json_value>^delete"
        """
        payload = (react_string or "").strip()
        if not payload:
            return "NOOP"

        # Full reset
        if payload == "RESET_TO_DEFAULT":
            self.generate_default_config(force=True)
            self.settings = self.read_config()
            self.parse_config(self.settings)
            return "Log: Configuration reset to default."

        # Path^json^op
        parts = payload.split("^")
        if len(parts) != 3:
            return "Log: Malformed string. Use 'key1,key2^value^flag'"

        path_str, raw_value, op = parts
        # normalize path (allow a few syntaxes)
        norm = path_str.replace(".", ",")
        norm = re.sub(r"\]\[", ",", norm)
        norm = re.sub(r"[\[\]]", ",", norm)
        key_hierarchy = [k.strip().strip("\"'") for k in norm.split(",") if k.strip()]
        if not key_hierarchy:
            return "Log: Bad path."

        # parse value
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            return "Err: Malformed JSON value. Could not decode."

        # current config
        cfg = self.settings if isinstance(self.settings, dict) else {}
        cursor = cfg
        for k in key_hierarchy[:-1]:
            if k not in cursor or not isinstance(cursor[k], dict):
                cursor[k] = {}
            cursor = cursor[k]
        leaf = key_hierarchy[-1]

        if op == "delete":
            if isinstance(cursor, dict) and leaf in cursor:
                cursor.pop(leaf, None)
        elif op == "update":
            cursor[leaf] = value
        else:
            return f"Log: Unknown flag '{op}'"

        self.save_config(cfg)
        self.parse_config(cfg)
        return f"Log: Setting {'deleted' if op == 'delete' else 'updated'} at {' -> '.join(key_hierarchy)}"
