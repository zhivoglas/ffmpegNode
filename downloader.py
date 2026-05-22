# downloader.py
import os
import zipfile
import urllib.request
import logging
import shutil
from typing import Optional

logger = logging.getLogger("ffmpegNode")

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")

def show_progress(block_num: int, block_size: int, total_size: int) -> None:
    if total_size <= 0:
        return
    
    downloaded = block_num * block_size
    percent = min(downloaded * 100 / total_size, 100.0)
    
    if int(percent) % 25 == 0 and downloaded > 0:
        logger.info(f"FFmpeg Download Progress: {int(percent)}%")

def ensure_ffmpeg() -> Optional[str]:
    ffmpeg_exe = os.path.join(BIN_DIR, "ffmpeg.exe")
    ffprobe_exe = os.path.join(BIN_DIR, "ffprobe.exe")

    if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
        return ffmpeg_exe

    logger.info(f"FFmpeg binaries missing. Preparing download to: {BIN_DIR}")
    os.makedirs(BIN_DIR, exist_ok=True)
    
    zip_path = os.path.join(BIN_DIR, "ffmpeg.zip")

    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
        urllib.request.install_opener(opener)

        logger.info(f"Downloading from {FFMPEG_URL}...")
        urllib.request.urlretrieve(FFMPEG_URL, zip_path, reporthook=show_progress)
        
        logger.info("Download finished. Extracting...")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extracted_count = 0
            for file_info in zip_ref.infolist():
                filename = os.path.basename(file_info.filename).lower()
                
                if filename in ["ffmpeg.exe", "ffprobe.exe"]:
                    target_path = os.path.join(BIN_DIR, filename)
                    with zip_ref.open(file_info) as source, open(target_path, "wb") as target:
                        shutil.copyfileobj(source, target)
                    extracted_count += 1
                    logger.info(f"Successfully extracted: {filename}")

        if os.path.exists(zip_path):
            os.remove(zip_path)

        if extracted_count < 2:
            logger.error("Failed to find both ffmpeg.exe and ffprobe.exe in the archive.")
            return None

        logger.info(f"FFmpeg setup complete. Path: {ffmpeg_exe}")
        return ffmpeg_exe

    except Exception as e:
        logger.error(f"FFmpeg installation failed: {e}", exc_info=True)
        if os.path.exists(zip_path):
            try: os.remove(zip_path)
            except: pass
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    ensure_ffmpeg()
