const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  selectFile: () => ipcRenderer.invoke("select-file"),
  runPythonPreview: (filePath) => ipcRenderer.invoke("run-python-preview", filePath),
  runPythonOutput: (params) => ipcRenderer.invoke("run-python-output", params)
});
