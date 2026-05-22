// frontend\main.cjs
const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const { setupFileHandlers } = require('./mainFileWork.cjs');
const { startBackend, killBackend, getBackendPort } = require('./mainBackendManager.cjs');

let mainWindow = null;
const isDev = !app.isPackaged;

function createWindow() {
  mainWindow = new BrowserWindow({
    autoHideMenuBar: true,
    width: 1400,
    height: 900,
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false
    },
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  setupFileHandlers(mainWindow);
}

app.whenReady().then(async () => {
  try {
    await startBackend();
    
    ipcMain.handle('get-backend-port', () => getBackendPort());
    
    createWindow();
  } catch (err) {
    dialog.showErrorBox('Critical Error', err.message);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  killBackend();
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  killBackend();
});
