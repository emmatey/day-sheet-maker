import { app, BrowserWindow, ipcMain, dialog } from "electron";
import os from "os";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import { shell } from "electron";
import fs from "fs"; 

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }
}

app.whenReady().then(() => {
  createWindow();

  /**
   * Open File Picker
   */
  ipcMain.handle("select-file", async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
      properties: ["openFile"],
      defaultPath: path.join(os.homedir(), "Desktop"),
      filters: [{ name: "Spreadsheets",
        extensions: ["csv", "xlsx", "xls"]
      },]
    });
    if (canceled) return null;
    return filePaths[0];
  });

  /**
   * Open Dir Picker
   */
  ipcMain.handle("select-directory", async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
      properties: ["openDirectory"],
      defaultPath: path.join(os.homedir(), "Desktop"),
    });
    if (canceled) return null;
    return filePaths[0];
  });

  /**
   * Run Python in --preview mode
   */
  ipcMain.handle("run-python-preview", 
    async (_event, inputFilePath) => {
      const scriptPath = path.join(__dirname, "../../backend/src/output.py");
      
      return runPython([scriptPath, inputFilePath, "--preview"]);
});

  /**
   * Run Python with --output
   */
  ipcMain.handle(
    "run-python-output",
    async (_event, { inputFile, saveDir, outputMap }) => {
      const scriptPath = path.join(__dirname, "../../backend/src/output.py");
      const outputArgs = Object.entries(outputMap).map(
        ([dept, mode]) => `${dept}:${mode}`
      );

      return runPython([
        scriptPath,
        inputFile,
        saveDir,
        "--output",
        ...outputArgs,
      ]);
    }
  );

  ipcMain.handle("open-folder", async (_event, folderPath) => {
  await shell.openPath(folderPath);
  });


  ipcMain.handle("confirm-reset-config", async () => {
  const { response } = await dialog.showMessageBox({
    type: "warning",
    buttons: ["Cancel", "Reset"],
    defaultId: 0,
    cancelId: 0,
    title: "Reset to Defaults",
    message: "Are you sure you want to reset all settings to default?",
    detail: "This will overwrite your current configuration and cannot be undone.",
  });

  return response === 1;
});

ipcMain.handle("reset-config", async () => {
  const scriptPath = path.join(__dirname, "../../backend/src/output.py");
  console.log("handle reset config clicked")
  /*return runPython([scriptPath, "--generate-default-config"]);*/
});

ipcMain.handle("read-settings", async () => {
  const p = settingsPath();
  const raw = fs.readFileSync(p, "utf-8");
  return JSON.parse(raw);
});

ipcMain.handle("apply-config", async (_e, updateString) => {
  const { cmd, args } = backendCmd();
  const child = spawn(cmd, [...args, "--update_config", updateString], { windowsHide: true });

  return await new Promise((resolve, reject) => {
    let out = "", err = "";
    child.stdout.on("data", d => out += d.toString());
    child.stderr.on("data", d => err += d.toString());
    child.on("close", code => {
      if (code === 0) resolve(out.trim());
      else reject(new Error(err || `backend exited ${code}`));
    });
  });
});

});

/**
 * Utility: Run Python and return stdout or throw on error
 */
function runPython(args) {
  return new Promise((resolve, reject) => {
    const pyCmd = process.platform === "win32" ? "python.exe" : "python";
    const py = spawn(pyCmd, args);

    let output = "";
    let errorOutput = "";

    py.stdout.on("data", (data) => (output += data.toString()));
    py.stderr.on("data", (data) => (errorOutput += data.toString()));

    py.on("close", (code) => {
      if (code === 0) {
        resolve(output.trim());
      } else {
        reject(new Error(`Python exited with code ${code}:\n${errorOutput}`));
      }
    });
  });
}

function isDev() {
  return !app.isPackaged;
}

// Where settings.json lives (adjust if you copy it somewhere else later)
function settingsPath() {
  return path.join(__dirname, "../../backend/src/settings.json");
}

// How to launch the backend for --update_config
function backendCmd() {
  if (isDev()) {
    // dev: run python + your script
    const py = process.platform === "win32" ? "python.exe" : "python";
    const script = path.join(__dirname, "../../backend/src/output.py");
    return { cmd: py, args: [script] };
  }
  // packaged: point to your bundled exe in extraResources (change name/path as needed)
  const exe =
    process.platform === "win32"
      ? path.join(process.resourcesPath, "daysheet-backend.exe")
      : path.join(process.resourcesPath, "daysheet-backend");
  return { cmd: exe, args: [] };
}

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
