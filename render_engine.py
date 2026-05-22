# render_engine.py
import os
import copy
import subprocess
import logging
import re
import gc
from pathlib import Path
from typing import Callable, Dict, Any, Iterator

# Импортируем утилиты (предполагается, что они есть в вашем проекте)
from ioUtils import get_files_from_dir, prepare_output_dir

try:
    from executor import GraphExecutor
except ImportError:
    GraphExecutor = None

logger = logging.getLogger("ffmpegNode.RenderEngine")

def check_gpu_support() -> bool:
    """Проверяет наличие аппаратных энкодеров (NVENC и т.д.)."""
    try:
        result = subprocess.run(['ffmpeg', '-encoders'], capture_output=True, text=True, timeout=5)
        encoders = result.stdout.lower()
        return any(c in encoders for c in ["h264_nvenc", "hevc_nvenc", "av1_nvenc"])
    except Exception:
        return False

class RenderJobProcessor:
    """
    Класс инкапсулирует логику подготовки графа, пакетной обработки (batch)
    и взаимодействия с GraphExecutor.
    """
    def __init__(self, job_id: str, graph: dict, modules: dict, use_gpu: bool, progress_callback: Callable[[int, str], None]):
        self.job_id = job_id
        self.graph = graph
        self.modules = modules
        self.use_gpu = use_gpu
        self.progress_callback = progress_callback

    def process(self) -> bool:
        """Основной метод запуска обработки графа."""
        if GraphExecutor is None:
            raise ValueError("executor.py is missing or broken.")

        nodes = self.graph.get('nodes', [])
        batch_node = self._find_batch_node(nodes)

        if batch_node:
            return self._process_batch(batch_node)
        else:
            return self._process_single()

    def _find_batch_node(self, nodes: list) -> dict | None:
        """Ищет ноду, которая является источником директории (для batch-рендера)."""
        for n in nodes:
            n_type = str(n.get('type', '')).lower()
            p_id = str(n.get('data', {}).get('pluginId', '')).lower()
            category = str(n.get('data', {}).get('category', '')).lower()
            
            is_source = 'input' in n_type or 'source' in n_type or 'input' in p_id or 'source' in category
            
            if is_source:
                data = n.get('data', {})
                params = n.get('params', {})
                path = data.get('file_path') or params.get('file_path') or data.get('dir_path') or params.get('dir_path') or ''
                if path and os.path.isdir(path):
                    return n
        return None

    def _get_payload_stream(self, dir_path: Path, extensions: tuple) -> Iterator[Path]:
        """Стриминг путей через генератор (не ест память на списках в 10к+ файлов)."""
        if not dir_path.is_dir():
            return
        # Рекурсивный поиск с использованием rglob и быстрая фильтрация
        yield from (f for f in dir_path.rglob("*") if f.suffix.lower() in extensions)

    def _find_batch_nodes(self, nodes: list) -> list:
        """Ищет все ноды, которые являются источниками директорий (для batch-рендера)."""
        batch_nodes = []
        for n in nodes:
            n_type = str(n.get('type', '')).lower()
            p_id = str(n.get('data', {}).get('pluginId', '')).lower()
            category = str(n.get('data', {}).get('category', '')).lower()
            
            is_source = 'input' in n_type or 'source' in n_type or 'input' in p_id or 'source' in category
            
            if is_source:
                data = n.get('data', {})
                params = n.get('params', {})
                path = data.get('file_path') or params.get('file_path') or data.get('dir_path') or params.get('dir_path') or ''
                if path and os.path.isdir(path):
                    batch_nodes.append(n)
        return batch_nodes

    def _process_batch(self, batch_node: dict) -> bool:
        """Логика пакетной обработки файлов из директории."""
        nodes = self.graph.get('nodes', [])
        batch_nodes = self._find_batch_nodes(nodes)
        
        # Основная нода для итерации (первая найденная)
        main_batch_node = batch_nodes[0] if batch_nodes else batch_node
        
        data = main_batch_node.get('data', {})
        params = main_batch_node.get('params', {})
        
        dir_path_str = data.get('file_path') or params.get('file_path') or data.get('dir_path') or params.get('dir_path') or ''
        input_dir = Path(dir_path_str).resolve()
        
        exts_str = data.get('extensions') or params.get('extensions') or ''
        if not exts_str:
            outputs = data.get('outputs', [])
            if outputs and isinstance(outputs, list):
                out_type = outputs[0].get('type', '')
                if out_type == 'video':
                    exts_str = '.mp4,.mov,.mkv,.avi,.webm,.flv'
                elif out_type == 'image':
                    exts_str = '.jpg,.jpeg,.png,.webp,.bmp,.gif'
                elif out_type == 'audio':
                    exts_str = '.mp3,.wav,.ogg,.m4a,.flac'
        
        if not exts_str:
            exts_str = '.mp4,.mov,.mkv,.avi,.webm,.flv,.jpg,.jpeg,.png,.webp,.bmp,.gif,.mp3,.wav,.ogg,.m4a,.flac'
        exts = tuple(ext.strip().lower() if ext.startswith('.') else f".{ext.strip().lower()}" for ext in exts_str.split(','))
        files = list(self._get_payload_stream(input_dir, exts))

        if not files:
            raise ValueError(f"No files found in {input_dir} matching {exts_str}")
        def natural_key(p: Path):
            return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(p))]
        files.sort(key=natural_key)
        other_batch_files = {}
        for b_node in batch_nodes[1:]:
            b_data = b_node.get('data', {})
            b_params = b_node.get('params', {})
            b_dir_str = b_data.get('file_path') or b_params.get('file_path') or b_data.get('dir_path') or b_params.get('dir_path') or ''
            b_dir = Path(b_dir_str).resolve()
            b_files = list(self._get_payload_stream(b_dir, exts))
            b_files.sort(key=natural_key)
            other_batch_files[b_node.get('id')] = b_files
            
        # Определяем общую папку вывода (на уровень выше или рядом)
        output_base_dir = input_dir.parent / "ffmpegNode_Export"
            
        total = len(files)
        overall_success = True
        
        for index, current_file in enumerate(files):
            # Извлекаем относительный путь, чтобы сохранить структуру папок
            try:
                rel_path = current_file.relative_to(input_dir)
            except ValueError:
                rel_path = Path(current_file.name)
                
            file_name = current_file.name
            
            # Формируем путь сохранения: Export/Subfolder/render_Filename.ext
            out_file_path = output_base_dir / rel_path.parent / f"render_{file_name}"
            out_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            current_graph = copy.deepcopy(self.graph)
            
            for node in current_graph['nodes']:
                n_data = node.setdefault('data', {})
                n_params = node.setdefault('params', {})
                
                # Подменяем пути во всех batch-нодах
                node_id = node.get('id')
                if node_id == main_batch_node.get('id'):
                    node['type'] = 'input' # Совместимость с executor.py
                    n_data['file_path'] = str(current_file)
                    n_params['file_path'] = str(current_file)
                    n_data.pop('dir_path', None)
                    n_params.pop('dir_path', None)
                    continue
                elif node_id in other_batch_files:
                    node['type'] = 'input' # Совместимость с executor.py
                    b_files = other_batch_files[node_id]
                    # Берем файл с тем же индексом, или последний, если файлов меньше
                    if b_files:
                        b_file = b_files[index] if index < len(b_files) else b_files[-1]
                        n_data['file_path'] = str(b_file)
                        n_params['file_path'] = str(b_file)
                    n_data.pop('dir_path', None)
                    n_params.pop('dir_path', None)
                    continue
                    
                # Подменяем пути в ноде вывода
                role = str(n_data.get('role', '')).lower()
                plugin_id = str(n_data.get('pluginId', '')).lower()
                node_type = str(node.get('type', '')).lower()
                
                if 'output' in plugin_id or 'sink' in role or 'output' in node_type:
                    n_data['file_path'] = str(out_file_path)
                    n_params['file_path'] = str(out_file_path)
                    
            if GraphExecutor is None:
                raise RuntimeError("GraphExecutor is not available")
                
            executor = GraphExecutor(
                data_source=current_graph, 
                plugins=self.modules, 
                use_gpu=self.use_gpu,
                job_id=f"{self.job_id}_{index}",
                progress_callback=lambda p, idx=index, fn=file_name: 
                    self.progress_callback(int((idx/total)*100 + (p/total)), f"[{idx+1}/{total}] {fn}")
            )
            
            try:
                if not executor.build_and_run():
                    logger.error(f"Failed task: {file_name}")
                    overall_success = False
                
                # ВАЖНО: Очистка ресурсов после каждого файла
                del executor
                if self.use_gpu:
                    gc.collect() # Принудительно очищаем Python объекты, держащие ссылки на GPU
                    
            except Exception as e:
                logger.critical(f"Engine crash on {file_name}: {e}")
                overall_success = False
                
        self.progress_callback(100, "All files processed")
        return overall_success

    def _process_single(self) -> bool:
        """Логика одиночного рендера (один файл или генерация)."""
        def single_cb(p: float):
            self.progress_callback(int(p), "")
            
        if GraphExecutor is None:
            raise RuntimeError("GraphExecutor is not available")
            
        executor = GraphExecutor(
            data_source=self.graph, 
            plugins=self.modules, 
            use_gpu=self.use_gpu,
            job_id=self.job_id,
            progress_callback=single_cb
        )
        return executor.build_and_run()
