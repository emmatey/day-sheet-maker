# daysheet-backend.spec  (place in backend/src)

from pathlib import Path
from PyInstaller.building.datastruct import Tree
from PyInstaller.utils.hooks import collect_data_files

# ---- Paths relative to this spec file ----
HERE = Path(__file__).parent.resolve()          # .../backend/src
REPO_ROOT = HERE.parents[2]                     # .../day-sheet-maker
ASSETS_DIR = REPO_ROOT / "assets"               # repo assets folder (xlsx, icons, etc.)
ICON_PATH = ASSETS_DIR / "lilWorkerBuddy.ico"   # change if your icon has a different name

# Bundle the entire repo assets/ folder under "assets/" at runtime
assets_tree = Tree(str(ASSETS_DIR), prefix="assets") if ASSETS_DIR.exists() else []

# 3rd-party packages sometimes need their package "data" added explicitly
third_party_datas = []
# If you use openpyxl, these two lines help on some setups:
third_party_datas += collect_data_files("openpyxl", include_py_files=False)
third_party_datas += collect_data_files("et_xmlfile", include_py_files=False)

# Hidden imports (usually not needed, but safe):
hiddenimports = ["openpyxl", "et_xmlfile"]

a = Analysis(
    ["output.py"],
    pathex=[str(HERE)],
    binaries=[],
    datas=[
        ("DefaultSettings.py", "."),  # for ConfigHandler import
    ] + third_party_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],        # You already force UTF-8 in output.py
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    assets_tree,                 # packs repo assets/ as "assets/"
    name="daysheet-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                    # ok if UPX isn't installed; PyInstaller will ignore
    console=False,               # set True temporarily if you want a console for logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_PATH) if ICON_PATH.exists() else None,
    uac_admin=False,
    uac_uiaccess=False,
    splash=None,
    onefile=True,                # single-file exe
)
