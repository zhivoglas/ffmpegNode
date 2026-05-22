import os
import sys
import logging
import uuid
import time
import queue
import threading
from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from plugin_manager import PLUGINS_CACHE, load_all_plugins, start_plugin_watchdog
from render_engine import check_gpu_support, RenderJobProcessor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR_ROOT = os.path.join(BASE_DIR, "bin")
BIN_DIR_PLUGIN = os.path.join(BASE_DIR, "plugincore", "ffmpeg", "bin")
os.environ["PATH"] = BIN_DIR_ROOT + os.pathsep + BIN_DIR_PLUGIN + os.pathsep + os.environ.get("PATH", "")

logger = logging.getLogger("ffmpegNode")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

RENDER_JOBS: Dict[str, Dict[str, Any]] = {}
RENDER_QUEUE: queue.Queue = queue.Queue()
GPU_AVAILABLE = False
MAX_JOBS_HISTORY = 100

def render_worker():
    """Воркер, который берет задачи из очереди и передает их в RenderJobProcessor."""
    while True:
        job = RENDER_QUEUE.get()
        job_id = job['job_id']
        try:
            RENDER_JOBS[job_id]["status"] = "processing"
            RENDER_JOBS[job_id]["started_at"] = time.time()
            
            # Коллбек для обновления состояния задачи из недр движка
            def update_progress(progress: int, current_file: str):
                RENDER_JOBS[job_id]["progress"] = progress
                if current_file:
                    RENDER_JOBS[job_id]["current_file"] = current_file

            processor = RenderJobProcessor(
                job_id=job_id,
                graph=job['graph'],
                modules=job['modules'],
                use_gpu=job['use_gpu'],
                progress_callback=update_progress
            )
            
            success = processor.process()
            
            if success:
                RENDER_JOBS[job_id]["status"] = "completed"
                RENDER_JOBS[job_id]["progress"] = 100
            else:
                logger.warning(f"Job {job_id} completed with some errors. Check engine logs.")
                RENDER_JOBS[job_id]["status"] = "completed_with_errors"
                RENDER_JOBS[job_id]["progress"] = 100
                RENDER_JOBS[job_id]["error"] = "Some files failed to process. Check engine logs."
                
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            RENDER_JOBS[job_id]["status"] = "failed"
            RENDER_JOBS[job_id]["error"] = str(e)
        finally:
            RENDER_JOBS[job_id]["finished_at"] = time.time()
            RENDER_QUEUE.task_done()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global GPU_AVAILABLE
    GPU_AVAILABLE = check_gpu_support()
    
    load_all_plugins(BASE_DIR)
    obs = start_plugin_watchdog(BASE_DIR)
    
    threading.Thread(target=render_worker, daemon=True).start()
    
    yield
    
    if obs.is_alive():
        obs.stop()
        obs.join()

app = FastAPI(title="ffmpegNode Engine API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/plugins")
async def get_plugins():
    return {
        "nodes": PLUGINS_CACHE["nodes"],
        "engine": PLUGINS_CACHE["active_engine"]
    }

@app.get("/health")
async def health():
    return {
        "gpu": GPU_AVAILABLE, 
        "queue": RENDER_QUEUE.qsize(), 
        "engine": PLUGINS_CACHE["active_engine"]
    }

@app.post("/render")
async def create_render(graph: dict = Body(...)):
    if len(graph.get("nodes",[])) > 500:
        raise HTTPException(400, "Graph is too complex (max 500 nodes)")

    if len(RENDER_JOBS) >= MAX_JOBS_HISTORY:
        oldest = min(RENDER_JOBS.keys(), key=lambda k: RENDER_JOBS[k].get("created_at", 0))
        RENDER_JOBS.pop(oldest, None)

    job_id = str(uuid.uuid4())
    use_gpu = graph.get("settings", {}).get("use_gpu", False) and GPU_AVAILABLE

    RENDER_JOBS[job_id] = {
        "status": "queued",
        "progress": 0,
        "gpu": use_gpu,
        "created_at": time.time(),
        "error": None,
        "current_file": ""
    }

    RENDER_QUEUE.put({
        "job_id": job_id,
        "graph": graph,
        "modules": PLUGINS_CACHE["loaded_modules"],
        "use_gpu": use_gpu
    })

    return {"job_id": job_id, "status": "queued"}

@app.get("/render/{job_id}")
async def get_job_status(job_id: str):
    job = RENDER_JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    logger.info(f"Starting ffmpegNode Engine on port {args.port}")
    uvicorn.run("main:app", host="127.0.0.1", port=args.port, reload=False)
