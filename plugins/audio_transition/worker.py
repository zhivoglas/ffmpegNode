import ffmpeg
import logging
from typing import Any, Optional, Tuple, Dict

logger = logging.getLogger("ffmpegNode.Nodes.AudioTransition")

StreamPair = Tuple[Any, Any]

def get_video_metadata(stream: Any) -> Dict[str, Any]:
    try:
        if not hasattr(stream, 'node'):
            return {}
        node = stream.node
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
    sample_rate = params.get("sample_rate", 48000)

    target_w = target_w - (target_w % 2)
    target_h = target_h - (target_h % 2)

    nv = None
    if v is not None:
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
        # Если аудио нет, генерируем тишину, чтобы acrossfade не завис
        na = ffmpeg.input('anullsrc', f='lavfi').audio
        na = (
            na.filter("aresample", sample_rate)
              .filter("aformat", sample_rates=sample_rate, channel_layouts="stereo")
        )
    
    return nv, na

def process(node_inputs: Dict[str, StreamPair], params: Dict[str, Any]) -> Optional[StreamPair]:
    if not node_inputs:
        logger.warning(" [!] AudioTransitionNode: No inputs provided.")
        return None

    input_a = node_inputs.get("video_a") or node_inputs.get("audio_a")
    input_b = node_inputs.get("video_b") or node_inputs.get("audio_b")

    if input_a is None and input_b is None:
        return None
    if input_a is not None and input_b is None:
        return input_a
    if input_b is not None and input_a is None:
        return input_b

    assert input_a is not None
    assert input_b is not None

    # Извлекаем видео и аудио
    v_a_raw = input_a[0] if isinstance(input_a, tuple) else None
    a_a_raw = input_a[1] if isinstance(input_a, tuple) else input_a
    
    v_b_raw = input_b[0] if isinstance(input_b, tuple) else None
    a_b_raw = input_b[1] if isinstance(input_b, tuple) else input_b

    transition_type = params.get("transition_type", "crossfade")
    video_transition_type = params.get("video_transition_type", "fade")
    duration = float(params.get("duration", 1.0))
    offset = float(params.get("offset", 5.0))
    c1 = params.get("curve_c1", "tri")
    c2 = params.get("curve_c2", "tri")
    smart_normalize = params.get("smart_normalize", True)

    # Гарантируем наличие базовых параметров
    output_params = params.copy()
    output_params.setdefault("width", 1920)
    output_params.setdefault("height", 1080)
    output_params.setdefault("fps", 30)
    output_params.setdefault("sample_rate", 48000)

    # 1. ОБРАБОТКА ВИДЕО (чтобы не было зависаний)
    v_out = None
    if v_a_raw is not None and v_b_raw is not None:
        if smart_normalize:
            detected_params = get_video_metadata(v_a_raw)
            output_params["width"] = params.get("width") or detected_params.get("width") or 1920
            output_params["height"] = params.get("height") or detected_params.get("height") or 1080
            output_params["fps"] = params.get("fps") or detected_params.get("fps") or 30

        try:
            v_a, a_a = normalize_stream(v_a_raw, a_a_raw, output_params) if smart_normalize else (v_a_raw, a_a_raw)
            v_b, a_b = normalize_stream(v_b_raw, a_b_raw, output_params) if smart_normalize else (v_b_raw, a_b_raw)
            
            # Применяем xfade к видео, чтобы его длина совпала с длиной аудио
            v_out = ffmpeg.filter([v_a, v_b], 'xfade', transition=video_transition_type, duration=duration, offset=offset)
        except Exception as e:
            logger.error(f" [!] Video Normalization/Xfade error: {e}", exc_info=True)
            v_out = v_a_raw
            a_a = a_a_raw
            a_b = a_b_raw
    else:
        # Если видео нет, все равно нормализуем аудио
        try:
            _, a_a = normalize_stream(None, a_a_raw, output_params) if smart_normalize else (None, a_a_raw)
            _, a_b = normalize_stream(None, a_b_raw, output_params) if smart_normalize else (None, a_b_raw)
        except Exception as e:
            logger.error(f" [!] Audio Normalization error: {e}", exc_info=True)
            a_a = a_a_raw
            a_b = a_b_raw
            
        if v_a_raw is not None:
            v_out = v_a_raw
        elif v_b_raw is not None:
            v_out = v_b_raw

    # 2. ОБРАБОТКА АУДИО
    try:
        # ВАЖНО: Чтобы аудиопереход идеально совпадал с видеопереходом (xfade), 
        # нам нужно обрезать первый трек ровно до (offset + duration).
        # Иначе acrossfade сработает в самом конце первого трека, что вызовет рассинхрон.
        a_a_trimmed = a_a.filter("atrim", start=0, end=offset + duration).filter("asetpts", "PTS-STARTPTS")

        # Используем параметр enable, чтобы применять глитч ТОЛЬКО в момент перехода.
        # Это полностью избавляет от необходимости использовать asplit и concat,
        # что на 100% исключает зависания (deadlocks) графа FFmpeg.
        enable_a = f"between(t,{offset},{offset+duration})"
        enable_b = f"between(t,0,{duration})"

        if transition_type == "crossfade":
            a_out = ffmpeg.filter([a_a_trimmed, a_b], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "glitch_bitcrush":
            bits = int(params.get("glitch_bits", 3))
            # Вариант 1 (Текущий в коде): Жесткий биткрашер + высокочастотное дрожание 
            # (Убрали aeval, который вызывал зависание)
            a_a_g = (a_a_trimmed.filter("acrusher", level_in=1.5, level_out=1, bits=bits, mode="log", aa=0, enable=enable_a)
                                .filter("tremolo", f=40, d=0.8, enable=enable_a))
            
            a_b_g = (a_b.filter("acrusher", level_in=1.5, level_out=1, bits=bits, mode="log", aa=0, enable=enable_b)
                        .filter("tremolo", f=40, d=0.8, enable=enable_b))
            
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "glitch_stutter":
            hz = int(params.get("stutter_hz", 15))
            # ВАЖНО: apulsator вызывает зависание FFmpeg при использовании с параметром enable.
            # Заменяем его на tremolo (d=1 дает 100% прерывание, что звучит идентично stutter), 
            # который абсолютно стабилен.
            a_a_g = a_a_trimmed.filter("tremolo", f=hz, d=1, enable=enable_a)
            a_b_g = a_b.filter("tremolo", f=hz, d=1, enable=enable_b)
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "complex_glitch":
            # Убираем flanger/vibrato, так как любые фильтры с линией задержки (delay line)
            # намертво вешают FFmpeg при работе с параметром enable.
            # Комбинируем acrusher (искажение) и tremolo (заикание) - они работают покадрово и абсолютно стабильны.
            a_a_g = (a_a_trimmed.filter("acrusher", bits=2, enable=enable_a)
                                .filter("tremolo", f=30, d=1, enable=enable_a))
            a_b_g = (a_b.filter("acrusher", bits=2, enable=enable_b)
                        .filter("tremolo", f=30, d=1, enable=enable_b))
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "radio_effect":
            # Эффект старой рации/радио: узкая полоса частот (highpass + lowpass) + легкий дисторшн
            a_a_g = (a_a_trimmed.filter("highpass", f=1000, enable=enable_a)
                                .filter("lowpass", f=3000, enable=enable_a)
                                .filter("acrusher", level_in=2, level_out=1, bits=8, mode="log", aa=0, enable=enable_a))
            a_b_g = (a_b.filter("highpass", f=1000, enable=enable_b)
                        .filter("lowpass", f=3000, enable=enable_b)
                        .filter("acrusher", level_in=2, level_out=1, bits=8, mode="log", aa=0, enable=enable_b))
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "underwater":
            # Эффект погружения под воду: срез высоких частот (глухой звук)
            a_a_g = a_a_trimmed.filter("lowpass", f=300, enable=enable_a)
            a_b_g = a_b.filter("lowpass", f=300, enable=enable_b)
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "wobble":
            # Эффект головокружения/волн: медленное глубокое изменение громкости
            hz = float(params.get("wobble_hz", 4.0))
            a_a_g = a_a_trimmed.filter("tremolo", f=hz, d=0.8, enable=enable_a)
            a_b_g = a_b.filter("tremolo", f=hz, d=0.8, enable=enable_b)
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "overdrive":
            # Жесткий перегруз: завышение громкости в 10 раз перед биткрашером
            a_a_g = (a_a_trimmed.filter("volume", volume=10.0, enable=enable_a)
                                .filter("acrusher", level_in=1, level_out=1, bits=4, mode="log", aa=0, enable=enable_a)
                                .filter("volume", volume=0.5, enable=enable_a))
            a_b_g = (a_b.filter("volume", volume=10.0, enable=enable_b)
                        .filter("acrusher", level_in=1, level_out=1, bits=4, mode="log", aa=0, enable=enable_b)
                        .filter("volume", volume=0.5, enable=enable_b))
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "hard_cut":
            # Жесткий стык: используем acrossfade с d=duration, но с кривой nofade (без изменения громкости)
            # При этом глушим первый клип во второй половине перехода, а второй - в первой половине.
            a_a_g = a_a_trimmed.filter("volume", enable=f"between(t,{offset + duration/2},{offset + duration})", volume=0)
            a_b_g = a_b.filter("volume", enable=f"between(t,0,{duration/2})", volume=0)
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1='nofade', c2='nofade')

        elif transition_type == "tape_rewind":
            # ИМИТАЦИЯ перемотки (aphaser вызывает зависание)
            # Используем highpass + быстрое тремоло + volume
            a_a_g = (a_a_trimmed.filter("highpass", f=1500, enable=enable_a)
                                .filter("tremolo", f=30, d=1, enable=enable_a)
                                .filter("volume", volume=2.0, enable=enable_a))
            a_b_g = (a_b.filter("highpass", f=1500, enable=enable_b)
                        .filter("tremolo", f=30, d=1, enable=enable_b)
                        .filter("volume", volume=2.0, enable=enable_b))
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "tape_chewed":
            # ИМИТАЦИЯ зажеванной пленки
            # Добавляем aa=0 в acrusher, чтобы избежать зависания
            a_a_g = (a_a_trimmed.filter("lowpass", f=500, enable=enable_a)
                                .filter("acrusher", level_in=2, level_out=1, bits=5, mode="log", aa=0, enable=enable_a)
                                .filter("tremolo", f=3, d=0.9, enable=enable_a))
            a_b_g = (a_b.filter("lowpass", f=500, enable=enable_b)
                        .filter("acrusher", level_in=2, level_out=1, bits=5, mode="log", aa=0, enable=enable_b)
                        .filter("tremolo", f=3, d=0.9, enable=enable_b))
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "digital_noise":
            # Цифровой шум: экстремальный биткрашер (1 бит) + прерывания
            a_a_g = (a_a_trimmed.filter("acrusher", level_in=3, level_out=1, bits=1, mode="log", aa=0, enable=enable_a)
                                .filter("tremolo", f=20, d=1, enable=enable_a))
            a_b_g = (a_b.filter("acrusher", level_in=3, level_out=1, bits=1, mode="log", aa=0, enable=enable_b)
                        .filter("tremolo", f=20, d=1, enable=enable_b))
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        elif transition_type == "white_noise":
            # ИМИТАЦИЯ белого шума
            # Убираем aphaser, оставляем acrusher (с aa=0) и tremolo
            a_a_g = (a_a_trimmed.filter("volume", volume=50.0, enable=enable_a)
                                .filter("acrusher", level_in=1, level_out=1, bits=1, mode="log", aa=0, enable=enable_a)
                                .filter("tremolo", f=50, d=1, enable=enable_a)
                                .filter("volume", volume=0.1, enable=enable_a))
            a_b_g = (a_b.filter("volume", volume=50.0, enable=enable_b)
                        .filter("acrusher", level_in=1, level_out=1, bits=1, mode="log", aa=0, enable=enable_b)
                        .filter("tremolo", f=50, d=1, enable=enable_b)
                        .filter("volume", volume=0.1, enable=enable_b))
            a_out = ffmpeg.filter([a_a_g, a_b_g], 'acrossfade', d=duration, c1=c1, c2=c2)

        else:
            a_out = ffmpeg.filter([a_a_trimmed, a_b], 'acrossfade', d=duration)

        logger.info(f" [AUDIO TRANSITION] Applied: {transition_type} (duration: {duration}s)")
        
        return (v_out, a_out) if v_out is not None else a_out

    except Exception as e:
        logger.error(f" [!] FFmpeg Audio Transition Error: {e}", exc_info=True)
        return input_a
