#!/usr/bin/env python3
"""
Beat Cut Node
----------------------------------
* Анализирует аудио трек с помощью librosa для поиска битов (ударов).
* Нарезает входные видео на фрагменты, соответствующие интервалам между битами.
* Склеивает фрагменты в один видеоряд под музыку.
"""

import ffmpeg
import logging
import re
import os
import tempfile
import uuid
import subprocess
import json
from typing import Any, Dict, List, Tuple, Optional

try:
    import librosa
except ImportError:
    librosa = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import numpy as np
except ImportError:
    np = None

logger = logging.getLogger("ffmpegNode.Nodes.BeatCut")
StreamPair = Tuple[Any, Any]

def find_input_filename(stream: Any) -> Optional[str]:
    if stream is None:
        return None
    try:
        node = stream.node
        visited = set()
        while node.name != 'input':
            if id(node) in visited:
                return None
            visited.add(id(node))
            if not node.incoming_edges:
                return None
            node = node.incoming_edges[0].upstream_node
        return node.kwargs.get('filename')
    except Exception:
        return None

def get_stream_duration(stream: Any) -> float:
    if stream is None:
        return 0.0
    filename = find_input_filename(stream)
    if filename and os.path.exists(filename):
        try:
            cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", filename]
            proc = subprocess.run(cmd, capture_output=True, timeout=5)
            info = json.loads(proc.stdout.decode('utf-8'))
            fmt = info.get("format", {})
            if "duration" in fmt:
                return float(fmt["duration"])
            for s in info.get("streams", []):
                if "duration" in s:
                    return float(s["duration"])
        except:
            pass
    
    # Мы больше не пытаемся делать cmd.run() на потоке, так как это
    # может вызвать выполнение всего upstream-графа и привести к зависанию.
    return 10.0

def extract_audio_to_temp(filepath: str) -> str:
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"temp_audio_{uuid.uuid4().hex}.wav")
    try:
        logger.info(f"Extracting audio from {filepath} for beat detection...")
        # Используем путь к файлу напрямую, а не поток, чтобы не триггерить upstream-ноды
        cmd = (
            ffmpeg
            .input(filepath)
            .output(
                temp_path, 
                format='wav', 
                acodec='pcm_s16le', 
                ac=1, 
                ar='22050'
            )
            .global_args('-loglevel', 'error', '-nostdin', '-y')
            .compile()
        )
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45, check=True)
        if os.path.exists(temp_path):
            return temp_path
        return ""
    except Exception as e:
        logger.error(f"Failed to extract audio: {e}")
        return ""

def get_beat_times(audio_path: str) -> List[float]:
    if librosa is None:
        logger.error("librosa is not installed. Please run: pip install librosa")
        return []
        
    logger.info(f"Analyzing beats for {audio_path}...")
    try:
        # Загружаем аудио. Так как мы уже конвертировали его в WAV, 
        # librosa использует быстрый soundfile backend и не вызывает ffmpeg (который может зависнуть).
        try:
            y, sr = librosa.load(audio_path, sr=22050, duration=120)
        except Exception as e:
            logger.error(f"librosa.load failed: {e}")
            return []
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        return list(beat_times)
    except Exception as e:
        logger.error(f"Beat detection failed: {e}")
        return []

def generate_silent_audio(duration: float, params: Dict[str, Any]) -> Any:
    sr = params.get("sample_rate", 44100)
    return (
        ffmpeg
        .input("anullsrc", f="lavfi", duration=duration, sample_rate=sr)
        .audio
        .filter("aresample", sr)
        .filter("aformat", sample_rates=sr, channel_layouts="stereo")
    )

def placeholder_stream(params: Dict[str, Any]) -> StreamPair:
    w = params.get("output_width", 1920)
    h = params.get("output_height", 1080)
    fps = params.get("output_fps", 30)
    dur = 1.0
    v = (
        ffmpeg
        .input(f"color=c=black:s={w}x{h}:r={fps}", f="lavfi", t=dur)
        .filter("format", "yuv420p")
        .filter("setsar", "1")
    )
    a = generate_silent_audio(dur, params)
    return v, a

MOTION_CACHE = {}

def get_video_motion_scores(video_path: str) -> Tuple[float, List[float]]:
    if video_path in MOTION_CACHE:
        return MOTION_CACHE[video_path]

    fps = 10.0
    scores = []
    
    if np is None:
        logger.warning("numpy is not installed. Motion detection disabled.")
        return fps, [0.0] * 100

    try:
        logger.info(f"Analyzing motion for {video_path}...")
        # Используем ffmpeg для экстремально быстрого декодирования и ресайза.
        # Читаем только первые 30 секунд, 10 кадров в секунду, размер 64x64, в оттенках серого.
        # Это позволяет избежать зависаний при декодировании 4K видео через OpenCV.
        cmd = (
            ffmpeg
            .input(video_path, t=30)
            .filter('scale', 64, 64)
            .filter('fps', fps=fps)
            .output('pipe:', format='rawvideo', pix_fmt='gray')
            .global_args('-loglevel', 'error', '-nostdin')
            .compile()
        )
        
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=45)
        out = proc.stdout
        
        frame_size = 64 * 64
        prev_frame = None
        
        for i in range(0, len(out), frame_size):
            frame_bytes = out[i:i+frame_size]
            if len(frame_bytes) < frame_size:
                break
                
            # Конвертируем в int16, чтобы избежать переполнения при вычитании (uint8)
            frame = np.frombuffer(frame_bytes, np.uint8).astype(np.int16)
            
            if prev_frame is not None:
                delta = np.abs(frame - prev_frame)
                # Простой порог (threshold) для отсечения шума
                delta[delta < 20] = 0
                scores.append(float(np.sum(delta)))
            else:
                scores.append(0.0)
                
            prev_frame = frame
            
    except Exception as e:
        logger.error(f"Motion analysis failed for {video_path}: {e}")
        
    if not scores:
        scores = [0.0] * 100
        
    if len(MOTION_CACHE) > 50:
        MOTION_CACHE.clear()
        
    MOTION_CACHE[video_path] = (fps, scores)
    return fps, scores

def find_best_crop_start(video_path: str, target_duration: float, total_duration: float) -> float:
    if target_duration > total_duration:
        return 0.0
    if not video_path or not os.path.exists(video_path):
        return max(0.0, (total_duration / 2.0) - (target_duration / 2.0))

    fps, scores = get_video_motion_scores(video_path)
    
    target_frames = int(target_duration * fps)
    if target_frames <= 0 or len(scores) <= target_frames:
        return max(0.0, (total_duration / 2.0) - (target_duration / 2.0))

    # Скользящее окно для поиска отрезка с максимальным движением
    window_sum = sum(scores[:target_frames])
    max_sum = window_sum
    best_start_frame = 0

    for i in range(1, len(scores) - target_frames + 1):
        window_sum = window_sum - scores[i - 1] + scores[i + target_frames - 1]
        if window_sum > max_sum:
            max_sum = window_sum
            best_start_frame = i

    return best_start_frame / fps

def normalize_video(v: Any, params: Dict[str, Any]) -> Any:
    w = params.get("output_width", 1920)
    h = params.get("output_height", 1080)
    fps = params.get("output_fps", 30)
    return (
        v.filter("scale", w, h, force_original_aspect_ratio="decrease")
         .filter("pad", w, h, "(ow-iw)/2", "(oh-ih)/2", color="black")
         .filter("setsar", "1")
         .filter("fps", fps=fps, round="up")
         .filter("format", "yuv420p")
    )

def process(node_inputs: Dict[str, Any], params: Dict[str, Any]) -> Optional[StreamPair]:
    if not node_inputs:
        logger.warning("BeatCut: no inputs supplied.")
        return placeholder_stream(params)

    audio_input = node_inputs.get("audio")
    if not audio_input or not isinstance(audio_input, tuple):
        logger.warning("BeatCut: 'audio' input is missing or invalid.")
        return placeholder_stream(params)

    _, a_main = audio_input
    if a_main is None:
        logger.warning("BeatCut: 'audio' input has no audio stream.")
        return placeholder_stream(params)

    src_keys = ["video_a", "video_b", "video_c", "video_d", "video_e"]
    video_sources = []
    for k in src_keys:
        src = node_inputs.get(k)
        if src and isinstance(src, tuple) and src[0] is not None:
            video_sources.append(src[0])

    if not video_sources:
        logger.warning("BeatCut: no video inputs supplied.")
        return placeholder_stream(params)

    # Пытаемся найти оригинальный файл, чтобы не выполнять upstream-граф
    audio_filename = find_input_filename(a_main)
    
    if not audio_filename or not os.path.exists(audio_filename):
        logger.warning("BeatCut: Could not find original audio file. Using fallback dummy beats.")
        # Если файл не найден (например, звук сгенерирован нодой), 
        # делаем фейковые биты каждые 2 секунды, чтобы не крашить пайплайн
        audio_dur = get_stream_duration(a_main)
        if audio_dur <= 0:
            audio_dur = 30.0
        beats = [float(i * 2) for i in range(int(audio_dur / 2) + 1)]
    else:
        temp_audio_file = extract_audio_to_temp(audio_filename)

        if not temp_audio_file or not os.path.exists(temp_audio_file):
            logger.error("BeatCut: Could not extract audio file for analysis.")
            return placeholder_stream(params)

        beats = get_beat_times(temp_audio_file)
        
        try:
            os.remove(temp_audio_file)
        except:
            pass

    if len(beats) < 2:
        logger.warning("BeatCut: Not enough beats detected.")
        return placeholder_stream(params)

    offset_ms = params.get("offset_ms", 0)
    offset_sec = offset_ms / 1000.0

    if offset_sec != 0:
        beats = [max(0.0, b + offset_sec) for b in beats]

    # Ограничиваем количество битов, чтобы избежать ошибки "Слишком длинная командная строка" (Windows limit: 8191 chars)
    MAX_BEATS = 30
    if len(beats) > MAX_BEATS:
        logger.info(f"BeatCut: Limiting beats from {len(beats)} to {MAX_BEATS} to prevent command line overflow.")
        beats = beats[:MAX_BEATS]

    video_durations = []
    video_files = []
    for v in video_sources:
        dur = get_stream_duration(v)
        video_durations.append(dur if dur > 0 else 10.0)
        video_files.append(find_input_filename(v))

    current_video_idx = 0

    if beats and beats[0] > 0.1:
        beats.insert(0, 0.0)

    # Создаем временный файл для concat demuxer
    concat_list_path = os.path.join(tempfile.gettempdir(), f"concat_list_{uuid.uuid4().hex}.txt")
    valid_clips_count = 0

    try:
        with open(concat_list_path, 'w', encoding='utf-8') as f:
            for i in range(len(beats) - 1):
                start_t = beats[i]
                end_t = beats[i+1]
                duration = end_t - start_t

                if duration <= 0:
                    continue

                v_idx = current_video_idx % len(video_sources)
                v_dur = video_durations[v_idx]
                v_file = video_files[v_idx]

                smart_crop = params.get("smart_crop", True)

                if v_file and os.path.exists(v_file):
                    if smart_crop:
                        start_crop = find_best_crop_start(v_file, duration, v_dur)
                    else:
                        start_crop = max(0.0, (v_dur / 2.0) - (duration / 2.0))
                    
                    # FFmpeg concat demuxer требует абсолютных путей и прямых слешей
                    safe_path = os.path.abspath(v_file).replace('\\', '/')
                    f.write(f"file '{safe_path}'\n")
                    f.write(f"inpoint {start_crop:.3f}\n")
                    f.write(f"outpoint {start_crop + duration:.3f}\n")
                    valid_clips_count += 1
                else:
                    logger.warning(f"BeatCut: Video file missing for index {v_idx}, skipping beat.")

                current_video_idx += 1

        if valid_clips_count == 0:
            logger.warning("BeatCut: No clips generated for concat demuxer.")
            return placeholder_stream(params)

        # Читаем склеенный поток через demuxer
        # safe=0 разрешает абсолютные пути
        concat_input = ffmpeg.input(concat_list_path, format='concat', safe=0)
        
        # Нормализуем уже склеенный поток ОДИН РАЗ
        v_out = normalize_video(concat_input.video, params)
        
        total_duration = beats[-1]
        a_out = (
            a_main
            .filter("atrim", start=0, end=total_duration)
            .filter("asetpts", "PTS-STARTPTS")
            .filter("aformat", sample_rates=44100, channel_layouts="stereo")
        )

        logger.info(f"BeatCut: concatenated {valid_clips_count} clips via demuxer → OK")
        return v_out, a_out
    except Exception as exc:
        logger.error(f"BeatCut concat failed: {exc}", exc_info=True)
        return placeholder_stream(params)
