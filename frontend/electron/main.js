import { app, BrowserWindow, ipcMain, dialog } from "electron";
import os from "os";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
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
   * Run Python in --preview mode
   */
  ipcMain.handle("run-python-preview", async (_event, inputFilePath) => {
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
});

/**
 * Utility: Run Python and return stdout or throw on error
 */
function runPython(args) {
  return new Promise((resolve, reject) => {
    const py = spawn("python", args);

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

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
