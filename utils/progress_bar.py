# utils\progress_bar.py
import sys
import logging
from typing import Optional

logger = logging.getLogger("ffmpegNodeProgress")

def show_progress(block_num: int, block_size: int, total_size: int) -> None:
    if total_size <= 0:
        return
    
    downloaded = block_num * block_size
    progress = min(downloaded / total_size, 1.0)
    percent = progress * 100
    last_p = getattr(show_progress, "_last_percent", -1)
    
    current_step = int(percent // 10) * 10 # Шаги по 10%
    
    if current_step > last_p or progress >= 1.0:
        if progress >= 1.0:
            logger.info("Download task: 100% [COMPLETED]")
        else:
            logger.info(f"Download task: {current_step}%...")
        show_progress._last_percent = current_step # type: ignore

def simple_progress_text(current: float, total: float, prefix: str = "Processing") -> None:
    if total <= 0:
        return
        
    percent = (current / total) * 100
    try:
        msg = f"\r{prefix}: {percent:>5.1f}%"
        sys.stdout.write(msg)
        sys.stdout.flush()
    except (ValueError, OSError):
        if int(percent) % 20 == 0:
            logger.info(f"{prefix}: {int(percent)}%")
