# plugin_manager.py
import os
import json
import logging
import importlib.util
from threading import Timer
from typing import Any, Dict
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger("ffmpegNode")

PLUGINS_CACHE: Dict[str, Any] = {
    "nodes": [],
    "engines": {},
    "active_engine": None,
    "loaded_modules": {}
}

def load_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        return

    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        manifest_p = os.path.join(path, 'manifest.json')
        worker_p = os.path.join(path, 'worker.py')
        
        if not os.path.exists(manifest_p):
            continue
        
        try:
            with open(manifest_p, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            plugin_id = manifest.get("id", name)
            module = None

            if os.path.exists(worker_p):
                spec = importlib.util.spec_from_file_location(f"mod_{plugin_id}", worker_p)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
            
            if module:
                PLUGINS_CACHE["loaded_modules"][plugin_id] = module

            if str(manifest.get("type")).lower() == "engine":
                PLUGINS_CACHE["active_engine"] = plugin_id
                PLUGINS_CACHE["engines"][plugin_id] = manifest
            else:
                PLUGINS_CACHE["nodes"].append(manifest)
                
        except Exception as e:
            logger.error(f"Failed to load {name}: {e}")

def load_all_plugins(base_dir: str):
    global PLUGINS_CACHE
    PLUGINS_CACHE["nodes"] = []
    PLUGINS_CACHE["engines"] = {}
    PLUGINS_CACHE["loaded_modules"] = {}
    
    load_directory(os.path.join(base_dir, 'plugincore'))
    load_directory(os.path.join(base_dir, 'plugins'))

class PluginsWatchdog(FileSystemEventHandler):
    def __init__(self, base_dir: str):
        self._timer = None
        self.base_dir = base_dir

    def on_modified(self, event):
        if event.is_directory:
            return
        filename = str(event.src_path).lower()
        if filename.endswith(('.py', '.json')):
            if self._timer:
                self._timer.cancel()
            self._timer = Timer(1.5, load_all_plugins, args=[self.base_dir])
            self._timer.start()

def start_plugin_watchdog(base_dir: str) -> Any:
    obs = Observer()
    for folder in ['plugins', 'plugincore']:
        path = os.path.join(base_dir, folder)
        if os.path.exists(path):
            obs.schedule(PluginsWatchdog(base_dir), path, recursive=True)
    obs.start()
    return obs