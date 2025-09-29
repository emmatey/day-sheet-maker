// ==============================
// Imports
// ==============================
import { app, BrowserWindow, ipcMain, dialog, shell } from "electron";
import path from "path";
import { fileURLToPath } from "url";
import { spawn, execFileSync } from "child_process";
import fs from "fs";

// ==============================
// Globals & Constants
// ==============================
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow = null;
const isDev = () => !app.isPackaged;

// Optional: keep single instance
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) app.quit();
else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}
if (process.platform === "win32") app.setAppUserModelId("DaySheet Maker");

// ==============================
// Settings helpers
// ==============================
const userSettingsPath = () => path.join(app.getPath("userData"), "settings.json");

const bundledDefaultSettingsPath = () => {
  if (isDev()) {
    // repo/defaults/settings.json  (electron/ → ../.. → repo/)
    return path.join(__dirname, "..", "..", "defaults", "settings.json");
  }
  // packaged app → resources/defaults/settings.json
  return path.join(process.resourcesPath, "defaults", "settings.json");
};

function ensureSettingsFile() {
  const dest = userSettingsPath();
  if (fs.existsSync(dest)) return dest;

  const src = bundledDefaultSettingsPath();
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  try {
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dest);
      console.log("Seeded settings from defaults:", src);
    } else {
      console.error("Defaults file NOT found at:", src, "— writing empty settings");
      fs.writeFileSync(dest, "{}");
    }
  } catch (err) {
    console.error("Failed to seed settings.json:", err);
    try { fs.writeFileSync(dest, "{}"); } catch {}
  }
  return dest;
}

// ==============================
// Backend launcher
// ==============================
function resolvePythonForDev() {
  // prefer project venv first
  const venvPy = process.platform === "win32"
    ? path.join(__dirname, "..", "..", "backend", "src", ".venv", "Scripts", "python.exe")
    : path.join(__dirname, "..", "..", "backend", "src", ".venv", "bin", "python");

  try { execFileSync(venvPy, ["--version"], { stdio: "ignore" }); return venvPy; } catch {}

  // fallbacks
  const candidates = process.platform === "win32" ? ["python", "py", "python3"] : ["python3", "python"];
  for (const c of candidates) {
    try { execFileSync(c, ["--version"], { stdio: "ignore" }); return c; } catch {}
  }
  return null;
}

function getBackendInvoker() {
  if (isDev()) {
    const py = resolvePythonForDev();
    const script = path.join(__dirname, "..", "..", "backend", "src", "output.py");
    return { cmd: py, argsPrefix: [script] };
  }
  // onedir layout we copy into resources/backend/daysheet-backend/
  const exePath = path.join(process.resourcesPath, "backend", "daysheet-backend", "daysheet-backend.exe");
  return { cmd: exePath, argsPrefix: [] };
}


function runBackend(args) {
  const { cmd, argsPrefix } = getBackendInvoker();
  const fullArgs = [...argsPrefix, ...args];
  const env = {
    ...process.env,
    DAYSHEET_CONFIG_DIR: app.getPath("userData"),
    PYTHONIOENCODING: "utf-8", 
    PYTHONUTF8: "1",           
  };

  return new Promise((resolve, reject) => {
    const child = spawn(cmd, fullArgs, { windowsHide: true, env });
    let out = "", err = "";
    child.stdout.on("data", d => (out += d.toString()));
    child.stderr.on("data", d => (err += d.toString()));
    child.on("close", code => (code === 0 ? resolve(out.trim()) : reject(new Error(err || `backend exited ${code}`))));
  });
}

// ==============================
// Window creation
// ==============================
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: "#00000000",
    icon: path.join(process.resourcesPath, "assets", "lilWorkerBuddy.ico"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
    },
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
    if (isDev()) mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }
}

// ==============================
// IPC registration
// ==============================
function registerIpcHandlers() {
  if (!mainWindow) throw new Error("Main window not ready");

  ipcMain.handle("select-file", async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
      properties: ["openFile"],
      defaultPath: app.getPath("documents"),
      filters: [{ name: "Spreadsheets", extensions: ["csv", "xlsx", "xls"] }],
    });
    return canceled ? null : filePaths[0];
  });

  ipcMain.handle("select-directory", async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
      properties: ["openDirectory"],
      defaultPath: app.getPath("documents"),
    });
    return canceled ? null : filePaths[0];
  });

  // Preview: output.py <input> --preview
  ipcMain.handle("run-python-preview", async (_e, inputFilePath) => {
    return runBackend([inputFilePath, "--preview"]);
  });

  // Generate output: output.py <input> <saveDir> --output <dept:mode>...
  ipcMain.handle("run-python-output", async (_e, { inputFile, saveDir, outputMap }) => {
    const outputArgs = Object.entries(outputMap).map(([dept, mode]) => `${dept}:${mode}`);
    return runBackend([inputFile, saveDir, "--output", ...outputArgs]);
  });

  ipcMain.handle("open-folder", async (_e, folderPath) => {
    const errorMessage = await shell.openPath(folderPath);
      if (errorMessage){
        console.error(`shell.openPath failed: ${errorMessage}`);
      } else {
        console.log("File opened sucessfully!");
      }
    return errorMessage;
  });

  ipcMain.handle("confirm-reset-config", async () => {
    const { response } = await dialog.showMessageBox({
      type: "warning",
      buttons: ["Cancel", "Reset"],
      defaultId: 0,
      cancelId: 0,
      title: "Reset to Defaults",
      message: "Reset all settings to default?",
      detail: "This will overwrite your current configuration.",
    });
    return response === 1;
  });

  ipcMain.handle("start-button-info-dialog", async () => {
    const { response } = await dialog.showMessageBox({
      message: "To begin, select the input file\nThis must be the weekly schedule exported from Kronos in either .xlsx or .csv format\n(PDF Files are not supported!)",
      type: "info"
    });
    return response;
  })

  // Let Python regenerate canonical defaults
  ipcMain.handle("reset-config", async () => {
    return runBackend(["--update_config", "RESET_TO_DEFAULT"]);
  });

  // Read settings.json (from userData)
  ipcMain.handle("read-settings", async () => {
    const p = ensureSettingsFile();
    try {
      const raw = fs.readFileSync(p, "utf-8");
      return JSON.parse(raw);
    } catch (e) {
      console.error("read-settings failed:", e);
      return {};
    }
  });

  // Apply a patch via backend (validation/merging lives in Python)
  ipcMain.handle("apply-config", async (_e, updateString) => {
    return runBackend(["--update_config", updateString]);
  });
}

// ==============================
// App lifecycle
// ==============================
app.whenReady().then(() => {
  // Use a real app name + stable userData path in dev (mirrors production)
  app.setName("DaySheet Maker");
  const desiredUserData = path.join(app.getPath("appData"), "DaySheet Maker");
  app.setPath("userData", desiredUserData);

  console.log("[dev] defaults path =", bundledDefaultSettingsPath(), fs.existsSync(bundledDefaultSettingsPath()));
  console.log("[dev] userData =", app.getPath("userData"));

  ensureSettingsFile();
  createWindow();
  registerIpcHandlers();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
