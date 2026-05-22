// frontend\mainBackendManager.cjs
const { app } = require('electron');
const path = require('path');
const { spawn, execSync } = require('child_process');
const fs = require('fs');
const http = require('http');
const net = require('net');

let backendProcess = null;
let backendPort = 8000;
const isDev = !app.isPackaged;

function getFreePort() {
  return new Promise((resolve) => {
    const srv = net.createServer();
    srv.listen(0, () => {
      const port = srv.address().port;
      srv.close(() => resolve(port));
    });
  });
}

function killBackend() {
  if (backendProcess) {
    console.log(`[Electron] Killing backend process tree (PID: ${backendProcess.pid})...`);
    if (process.platform === 'win32') {
      try {
        execSync(`taskkill /pid ${backendProcess.pid} /T /F`);
      } catch (err) {
        console.error("[Electron] Error closing backend:", err.message);
      }
    } else {
      backendProcess.kill('SIGTERM');
    }
    backendProcess = null;
  }
}

function getPythonPath() {
  if (process.platform !== 'win32') return 'python3';
  try {
    const stdout = execSync('where python', { encoding: 'utf8' });
    const paths = stdout.split('\r\n').map(p => p.trim()).filter(p => p && fs.existsSync(p));
    const realPath = paths.find(p => !p.includes('WindowsApps'));
    if (realPath) return realPath;
    if (paths.length > 0) return paths[0];
  } catch {
    console.error("[Electron] Path discovery failed, falling back to 'python'");
  }
  return 'python';
}

async function startBackend() {
  backendPort = await getFreePort();
  const BACKEND_URL = `http://127.0.0.1:${backendPort}`;
  console.log(`[Electron] Found free port for backend: ${backendPort}`);

  return new Promise((resolve, reject) => {
    let attempts = 0;
    const maxAttempts = 30;
    const projectRoot = isDev 
      ? path.resolve(__dirname, '..') 
      : path.join(process.resourcesPath, 'backend');
    
    const pythonScript = path.join(projectRoot, 'main.py');
    const pythonCmd = getPythonPath();

    console.log(`[Electron] Starting Backend: ${pythonCmd} ${pythonScript} --port ${backendPort}`);

    backendProcess = spawn(pythonCmd, [pythonScript, '--port', backendPort.toString()], {
      cwd: projectRoot,
      env: { ...process.env, PYTHONUTF8: "1" },
      stdio: ['ignore', 'pipe', 'pipe'],
      shell: false
    });

    backendProcess.stdout.on('data', (data) => console.log(`[Py]: ${data.toString().trim()}`));
    backendProcess.stderr.on('data', (data) => console.error(`[Py Error]: ${data.toString().trim()}`));
    backendProcess.on('error', (err) => {
      reject(new Error(`Failed to start Python: ${err.message}`));
    });

    backendProcess.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.error(`[Electron] Backend exited with code ${code}`);
        reject(new Error(`Backend exited with code ${code}. Check dependencies (FastAPI, Uvicorn).`));
      }
    });

    const checkReady = () => {
      if (attempts++ > maxAttempts) {
        reject(new Error(`Backend startup timeout. Check if port ${backendPort} is occupied.`));
        return;
      }

      const req = http.get(`${BACKEND_URL}/health`, (res) => {
        if (res.statusCode === 200) {
          console.log('[Electron] Backend is ready!');
          resolve(backendPort);
        } else {
          setTimeout(checkReady, 1000);
        }
      });

      req.on('error', () => setTimeout(checkReady, 1000));
      req.setTimeout(500, () => req.destroy());
    };

    setTimeout(checkReady, 2000);
  });
}

function getBackendPort() {
  return backendPort;
}

module.exports = { startBackend, killBackend, getBackendPort };
