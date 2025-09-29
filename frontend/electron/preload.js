const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  selectFile: () => ipcRenderer.invoke("select-file"),
  selectDirectory: () => ipcRenderer.invoke("select-directory"),
  runPythonPreview: (filePath) => ipcRenderer.invoke("run-python-preview", filePath),
  runPythonOutput: (params) => ipcRenderer.invoke("run-python-output", params),
  openFolder: (path) => ipcRenderer.invoke("open-folder", path),
  confirmResetConfig: () => ipcRenderer.invoke("confirm-reset-config"),
  startButtonInfoDialog: () => ipcRenderer.invoke("start-button-info-dialog"),
  resetConfig: () => ipcRenderer.invoke("reset-config"), 
  readSettings: () => ipcRenderer.invoke("read-settings"),
  applyConfig: (updateString) => ipcRenderer.invoke("apply-config", updateString),
});
