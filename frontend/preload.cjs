// frontend\preload.cjs
const { contextBridge, ipcRenderer, shell } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openFile: (options) => ipcRenderer.invoke('dialog:openFile', options),
  openDir: () => ipcRenderer.invoke('dialog:openDir'),
  saveFile: (options) => ipcRenderer.invoke('dialog:saveFile', options),
  scanDir: (path) => ipcRenderer.invoke('dialog:scanDir', path),
  getBackendPort: () => ipcRenderer.invoke('get-backend-port'),
  openExternal: (url) => shell.openExternal(url)
});