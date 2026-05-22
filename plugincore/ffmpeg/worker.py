import ffmpeg
import os
import logging
import urllib.request
import zipfile
import shutil
import subprocess
import re
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger("ffmpegNode.Engine.FFmpeg")

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

class Engine:
    def __init__(
        self,
        ffmpeg_path: Optional[str] = None,
        use_gpu: bool = False,
        threads: int = 0,
        hwaccel: str = "auto",
        job_id: Optional[str] = None # <-- Добавлено на всякий случай, если передается из executor
    ):
        self.name = "FFmpeg Engine (Autonomous)"
        self.use_gpu = use_gpu
        self.threads = threads
        self.hwaccel = hwaccel
        self.job_id = job_id

        # 1. Определяем пути строго внутри папки плагина
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.bin_dir = os.path.join(self.plugin_dir, "bin")
        
        if ffmpeg_path:
            self.executable = ffmpeg_path
            self.ffprobe = "ffprobe"
        else:
            self.executable = os.path.join(self.bin_dir, "ffmpeg.exe")
            self.ffprobe = os.path.join(self.bin_dir, "ffprobe.exe")
            
            # 2. Автоматически скачиваем бинарники, если их нет
            self._ensure_installed()

        # 3. КРИТИЧЕСКИ ВАЖНО: Добавляем локальный bin в PATH среды выполнения!
        # Это позволит библиотеке ffmpeg-python и другим плагинам-нодам 
        # находить ffprobe.exe и ffmpeg.exe без указания абсолютных путей.
        if self.bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = self.bin_dir + os.pathsep + os.environ.get("PATH", "")

        # 4. Проверяем реальную поддержку GPU (NVENC)
        if self.use_gpu and not self._check_gpu():
            logger.warning("GPU NVENC is not supported by hardware/drivers. Falling back to CPU.")
            self.use_gpu = False

        # 5. Настраиваем параметры кодека
        if self.use_gpu:
            self.video_codec = "h264_nvenc"
            self.extra_args = {
                "preset": "p4",
                "tune": "hq"
            }
        else:
            self.video_codec = "libx264"
            self.extra_args = {
                "preset": "medium",
                "crf": "23"
            }

    def _ensure_installed(self) -> None:
        """Проверяет наличие FFmpeg и скачивает его при необходимости."""
        if os.path.exists(self.executable) and os.path.exists(self.ffprobe):
            return

        logger.info(f"FFmpeg binaries missing in {self.bin_dir}. Starting download...")
        os.makedirs(self.bin_dir, exist_ok=True)
        zip_path = os.path.join(self.bin_dir, "ffmpeg.zip")

        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
            urllib.request.install_opener(opener)

            urllib.request.urlretrieve(FFMPEG_URL, zip_path)
            logger.info("Download finished. Extracting...")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    filename = os.path.basename(file_info.filename).lower()
                    if filename in ["ffmpeg.exe", "ffprobe.exe"]:
                        target_path = os.path.join(self.bin_dir, filename)
                        with zip_ref.open(file_info) as source, open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                        logger.info(f"Extracted: {filename}")

            if os.path.exists(zip_path):
                os.remove(zip_path)

        except Exception as e:
            logger.error(f"FFmpeg installation failed: {e}")
            raise RuntimeError(f"Failed to install FFmpeg: {e}")

    def _check_gpu(self) -> bool:
        """Проверяет наличие NVENC кодировщиков в скачанном FFmpeg."""
        try:
            result = subprocess.run([self.executable, '-encoders'], capture_output=True, text=True, timeout=5)
            return any(c in result.stdout.lower() for c in ["h264_nvenc", "hevc_nvenc", "av1_nvenc"])
        except Exception:
            return False

    def _get_duration(self, file_path: str) -> float:
        """Получает длительность медиафайла в секундах."""
        try:
            probe = ffmpeg.probe(file_path, cmd=self.ffprobe)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.warning(f"Could not get duration for {file_path}: {e}")
            return 0.0

    def run(self, pipeline_steps: List[Dict[str, Any]], plugins: Optional[Dict[str, Any]] = None, progress_callback=None) -> bool:
        plugins = plugins or {}
        streams: Dict[str, Tuple[Any, Any]] = {}
        last_output = None
        
        # Переменная для хранения максимальной длительности входных файлов
        total_duration = 0.0

        for step in pipeline_steps:
            node_id = str(step["id"])
            node_type = step["type"]
            params = step.get("params", {}).copy()
            inputs_info = step.get("inputs", [])

            try:
                node_inputs = {}
                for inp in inputs_info:
                    src_id = str(inp["source_node"])
                    target_port = inp.get("target_handle", "input")
                    if src_id in streams:
                        node_inputs[target_port] = streams[src_id]

                if node_type == "input":
                    path = params.get("file_path")
                    if not path or not os.path.exists(path):
                        logger.error(f"Input file not found: {path}")
                        continue
                    
                    # Получаем длительность файла для расчета прогресса
                    duration = self._get_duration(path)
                    total_duration = max(total_duration, duration)

                    inp = ffmpeg.input(path)
                    streams[node_id] = (inp.video, inp.audio)
                    logger.info(f"Loaded input {path} (Duration: {duration}s)")

                elif node_type == "output":
                    if not node_inputs:
                        continue

                    v_stream, a_stream = node_inputs.get("input", list(node_inputs.values())[0])
                    out_path = params.get("file_path", "output.mp4")

                    output_params: Dict[str, Any] = {
                        "vcodec": self.video_codec,
                        "acodec": "aac",
                        "pix_fmt": "yuv420p",
                        **self.extra_args
                    }

                    if self.threads > 0:
                        output_params["threads"] = self.threads

                    if a_stream is not None:
                        last_output = ffmpeg.output(v_stream, a_stream, out_path, **output_params)
                    else:
                        last_output = ffmpeg.output(v_stream, out_path, **output_params)

                    logger.info(f"Prepared output: {out_path}")

                elif node_type in plugins:
                    plugin = plugins[node_type]
                    result = plugin.process(node_inputs, params)
                    if result:
                        streams[node_id] = result
                        logger.info(f"Plugin node processed: {node_type}")
                    else:
                        logger.warning(f"Plugin {node_type} returned None. Skipping.")

                else:
                    if not node_inputs:
                        continue
                    v_in, a_in = node_inputs.get("input", list(node_inputs.values())[0])
                    filter_name = params.pop("filter_name", node_type)
                    v_out = v_in.filter(filter_name, **params)
                    streams[node_id] = (v_out, a_in)
                    logger.info(f"Filter applied: {filter_name}")

            except Exception as e:
                logger.error(f"Node error {node_id} ({node_type}): {e}")

        if last_output is None:
            logger.warning("Pipeline finished without output node")
            return False

        try:
            logger.info("Starting FFmpeg render...")
            
            # Запускаем FFmpeg асинхронно, чтобы читать stderr в реальном времени
            process = ffmpeg.run_async(
                last_output,
                cmd=self.executable,
                overwrite_output=True,
                pipe_stderr=True
                # УБРАНО: pipe_stdout=True (чтобы избежать переполнения буфера ОС и зависания)
            )
            
            # Регулярное выражение для поиска времени в логах FFmpeg (time=00:01:23.45)
            time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
            
            # Читаем вывод FFmpeg построчно
            if process.stderr:
                for line in process.stderr:
                    line_str = line.decode("utf-8", errors="replace")
                    
                    # Ищем текущее время рендера
                    match = time_pattern.search(line_str)
                    if match and total_duration > 0 and progress_callback:
                        hours = int(match.group(1))
                        minutes = int(match.group(2))
                        seconds = float(match.group(3))
                        
                        current_time = (hours * 3600) + (minutes * 60) + seconds
                        
                        # Вычисляем процент
                        percent = (current_time / total_duration) * 100
                        percent = min(99.9, percent)
                        
                        progress_callback(percent)
            
            process.wait()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg process failed with return code {process.returncode}")
                return False

            # В самом конце принудительно ставим 100%
            if progress_callback:
                progress_callback(100.0)

            logger.info("Rendering completed successfully")
            return True

        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            return False