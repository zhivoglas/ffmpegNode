# plugins\transition\worker.py
import ffmpeg
import logging
from typing import Any, Optional, Tuple, Dict

logger = logging.getLogger("ffmpegNode.Nodes.Transition")

StreamPair = Tuple[Any, Any]

def get_video_metadata(stream: Any) -> Dict[str, Any]:
    """
    Пытается извлечь метаданные (разрешение, fps) из исходного файла потока,
    проходя вверх по графу ffmpeg-python до узла 'input'.
    """
    try:
        if not hasattr(stream, 'node'):
            return {}
            
        node = stream.node
        # Идем вверх по графу, чтобы найти входной файл
        while node.name != 'input':
            if not node.incoming_edges:
                break
            node = node.incoming_edges[0].upstream_node
            
        if node.name == 'input':
            filename = node.kwargs.get('filename')
            if filename:
                probe = ffmpeg.probe(filename)
                video_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
                if video_info:
                    width = int(video_info.get('width', 1920))
                    height = int(video_info.get('height', 1080))
                    
                    # Извлечение FPS (обрабатываем как дроби '30000/1001', так и целые числа)
                    fps_str = video_info.get('r_frame_rate', '30/1')
                    if '/' in fps_str:
                        num, den = map(int, fps_str.split('/'))
                        fps = num / den if den != 0 else 30
                    else:
                        fps = float(fps_str)
                        
                    return {"width": width, "height": height, "fps": fps}
    except Exception as e:
        logger.warning(f" [!] Не удалось автоматически определить параметры видео: {e}")
        
    return {}

def normalize_stream(v: Any, a: Any, params: Dict[str, Any]) -> StreamPair:
    target_w = int(params.get("width", 1920))
    target_h = int(params.get("height", 1080))
    target_fps = params.get("fps", 30)

    # Убедимся, что ширина и высота четные (строгое требование формата yuv420p)
    target_w = target_w - (target_w % 2)
    target_h = target_h - (target_h % 2)

    nv = (
        v.filter("scale", target_w, target_h, force_original_aspect_ratio="decrease")
         .filter("pad", target_w, target_h, "(ow-iw)/2", "(oh-ih)/2", color="black")
         .filter("fps", fps=target_fps, round="up") 
         .filter("format", "yuv420p")
    )

    na = (
        a.filter("aresample", 48000)
         .filter("aformat", sample_rates=48000, channel_layouts="stereo")
    )
    
    return nv, na

def process(node_inputs: Dict[str, StreamPair], params: Dict[str, Any]) -> Optional[StreamPair]:
    if not node_inputs:
        logger.warning(" [!] TransitionNode: No inputs provided.")
        return None

    transition_type = params.get("transition_type", "fade")
    duration = float(params.get("duration", 1.0))
    offset = float(params.get("offset", 5.0))
    smart_normalize = params.get("smart_normalize", True)

    input_a = node_inputs.get("video_a")
    input_b = node_inputs.get("video_b")

    if input_a is None and input_b is None:
        return None
    if input_a is not None and input_b is None:
        return input_a
    if input_b is not None and input_a is None:
        return input_b

    assert input_a is not None
    assert input_b is not None

    v_a_raw, a_a_raw = input_a
    v_b_raw, a_b_raw = input_b

    # Если включена умная нормализация, пытаемся определить параметры первого видео
    if smart_normalize:
        detected_params = get_video_metadata(v_a_raw)
        
        # Приоритет: 1. Явно переданные параметры -> 2. Определенные из видео -> 3. Дефолтные значения
        target_w = params.get("width") or detected_params.get("width") or 1920
        target_h = params.get("height") or detected_params.get("height") or 1080
        target_fps = params.get("fps") or detected_params.get("fps") or 30

        # Создаем копию параметров для нормализации
        norm_params = params.copy()
        norm_params["width"] = target_w
        norm_params["height"] = target_h
        norm_params["fps"] = target_fps
    else:
        norm_params = params

    try:
        v_a, a_a = normalize_stream(v_a_raw, a_a_raw, norm_params) if smart_normalize else (v_a_raw, a_a_raw)
        v_b, a_b = normalize_stream(v_b_raw, a_b_raw, norm_params) if smart_normalize else (v_b_raw, a_b_raw)
    except Exception as e:
        logger.error(f" [!] Normalization error in TransitionNode: {e}")
        return input_a

    try:
        # Фильтр xfade требует строгого совпадения разрешения, fps, timebase и формата пикселей
        v_out = ffmpeg.filter([v_a, v_b], 'xfade', transition=transition_type, duration=duration, offset=offset)
        a_out = ffmpeg.filter([a_a, a_b], 'acrossfade', d=duration)
        logger.info(f" [TRANSITION] Result: {transition_type} (duration: {duration}s, offset: {offset}s)")
        return v_out, a_out

    except Exception as e:
        logger.error(f" [!] FFmpeg Transition Error: {e}")
        return input_a

    return input_a