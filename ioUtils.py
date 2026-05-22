# ioUtils.py
import os
from pathlib import Path

def get_files_from_dir(dir_path, extensions):
    """
    Recursively searches for files in dir_path that match the given extensions.
    extensions: tuple of strings, e.g. ('.mp4', '.mov')
    """
    if not os.path.isdir(dir_path):
        raise ValueError(f"Directory not found: {dir_path}")
        
    files = [str(f) for f in Path(dir_path).rglob("*") if f.suffix.lower() in extensions]
    return files

def prepare_output_dir(output_path):
    """
    Ensures the directory for the output_path exists.
    """
    if output_path.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.jpg', '.png', '.wav', '.mp3')):
        out_dir = os.path.dirname(output_path)
    else:
        out_dir = output_path
        
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    return out_dir
