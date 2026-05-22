// frontend\mainFileWork.cjs
const { dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

function setupFileHandlers(mainWindow) {
  ipcMain.handle('dialog:openFile', async (event, options) => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: options?.filters || [{ name: 'All Files', extensions: ['*'] }]
    });
    if (result.canceled) return null;
    return result.filePaths[0];
  });

  // 2. Открытие папки
  ipcMain.handle('dialog:openDir', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory']
    });
    if (result.canceled) return null;
    return result.filePaths[0];
  });

  // 3. Сохранение файла
  ipcMain.handle('dialog:saveFile', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, {
      title: 'Save Render As',
      defaultPath: options?.defaultPath || 'output.mp4',
      filters: options?.filters || [{ name: 'All Files', extensions: ['*'] }]
    });
    if (result.canceled) return null;
    return result.filePath;
  });

  ipcMain.handle('dialog:scanDir', async (event, options = {}) => {
    let dirPath = options.dropPath || null;
    
    if (!dirPath) {
      const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory']
      });
      if (result.canceled) return { path: null, files: [], count: 0 };
      dirPath = result.filePaths[0];
    }

    const exts = options.extensions ? options.extensions.map(ext => `.${ext.toLowerCase()}`) : null;
    
    function getAllFiles(dir, fileList = []) {
      const files = fs.readdirSync(dir);
      for (const file of files) {
        const filePath = path.join(dir, file);
        if (fs.statSync(filePath).isDirectory()) {
          getAllFiles(filePath, fileList);
        } else {
          fileList.push(filePath);
        }
      }
      return fileList;
    }

    try {
      const allFiles = getAllFiles(dirPath);
      const matchedFiles = exts 
        ? allFiles.filter(f => exts.some(ext => f.toLowerCase().endsWith(ext)))
        : allFiles;
      
      return { path: dirPath, files: matchedFiles, count: matchedFiles.length };
    } catch (err) {
      console.error("Error scanning directory:", err);
      return { path: dirPath, files: [], count: 0 };
    }
  });
}

module.exports = { setupFileHandlers };
