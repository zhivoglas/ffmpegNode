import ffmpeg
import logging
from typing import Any, Optional, Tuple, Dict

logger = logging.getLogger("ffmpegNode.Nodes.Merge")

StreamPair = Tuple[Any, Any]

def normalize_stream(v: Any, a: Any, params: Dict[str, Any]) -> StreamPair:
    # Безопасное извлечение с фоллбеками на случай прямого вызова функции
    target_w = params.get("width", 1920)
    target_h = params.get("height", 1080)
    target_fps = params.get("fps", 30)
    sample_rate = params.get("sample_rate", 48000)

    nv = (
        v.filter("scale", target_w, target_h, force_original_aspect_ratio="decrease")
         .filter("pad", target_w, target_h, "(ow-iw)/2", "(oh-ih)/2", color="black")
         .filter("setsar", "1")
         .filter("fps", fps=target_fps, round="up") 
         .filter("format", "yuv420p")
    )

    if a is not None:
        na = (
            a.filter("aresample", sample_rate)
             .filter("aformat", sample_rates=sample_rate, channel_layouts="stereo")
        )
    else:
        # 2026 Practice: Убираем t=0.1. Бесконечная тишина (anullsrc) корректно 
        # обрезается фильтрами amix (duration=longest) и concat по длине видеопотока.
        na = ffmpeg.input('anullsrc', f='lavfi').audio
        na = (
            na.filter("aresample", sample_rate)
              .filter("aformat", sample_rates=sample_rate, channel_layouts="stereo")
        )
    
    return nv, na

def process(node_inputs: Dict[str, StreamPair], params: Dict[str, Any]) -> Optional[StreamPair]:
    if not node_inputs:
        logger.warning(" [!] MergeNode: No inputs provided.")
        return None

    mode = params.get("mode", "overlay")
    smart_normalize = params.get("smart_normalize", True)

    input_a = node_inputs.get("video_a")
    input_b = node_inputs.get("video_b")

    # Быстрый возврат, если одного из входов нет
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

    # Гарантируем наличие базовых параметров для всего графа
    output_params = params.copy()
    output_params.setdefault("width", 1920)
    output_params.setdefault("height", 1080)
    output_params.setdefault("fps", 30)
    output_params.setdefault("sample_rate", 48000)

    try:
        v_a, a_a = normalize_stream(v_a_raw, a_a_raw, output_params) if smart_normalize else (v_a_raw, a_a_raw)
        
        if mode == "overlay" and smart_normalize:
            pip_params = output_params.copy()
            # Защита от деления на 0 или слишком мелких размеров (min 2px для YUV)
            pip_params["width"] = max(2, output_params["width"] // 3)
            pip_params["height"] = max(2, output_params["height"] // 3)
            v_b, a_b = normalize_stream(v_b_raw, a_b_raw, pip_params)
        else:
            v_b, a_b = normalize_stream(v_b_raw, a_b_raw, output_params) if smart_normalize else (v_b_raw, a_b_raw)
            
    except Exception as e:
        # exc_info=True даст полный стек вызовов в логах для быстрого дебага
        logger.error(f" [!] Normalization error in MergeNode: {e}", exc_info=True)
        return input_a

    try:
        if mode == "overlay":
            # 2026 Practice: Относительные отступы (5% от ширины/высоты) вместо хардкода 20px
            margin_x = params.get("margin_x", "W*0.05")
            margin_y = params.get("margin_y", "H*0.05")
            pos_x = params.get("pos_x", f"W-w-{margin_x}")
            pos_y = params.get("pos_y", f"H-h-{margin_y}")
            
            # eof_action='pass' - если видео B короче видео A, оно просто исчезнет, а не "застрянет" на последнем кадре
            v_out = ffmpeg.overlay(v_a, v_b, x=pos_x, y=pos_y, eof_action='pass')
            
            # 2026 Practice: normalize=0 отключает автоматическое понижение громкости (когда amix делает оба трека тише в 2 раза)
            a_out = ffmpeg.filter([a_a, a_b], 'amix', inputs=2, duration='longest', dropout_transition=0, normalize=0)
            
            logger.info(" [MERGE] Result: Overlay mode (B over A)")
            return v_out, a_out

        elif mode == "sequential":
            joined = ffmpeg.concat(v_a, a_a, v_b, a_b, v=1, a=1, unsafe=1).node
            logger.info(" [MERGE] Result: Sequential mode (A then B)")
            return joined[0], joined[1]
            
        else:
            logger.warning(f" [!] MergeNode: Unknown mode '{mode}', falling back to video_a")
            return input_a

    except Exception as e:
        logger.error(f" [!] FFmpeg Merge Error: {e}", exc_info=True)
        return input_a