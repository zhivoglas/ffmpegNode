import logging
import inspect
from typing import Any, Optional, Dict, List, Callable

logger = logging.getLogger("ffmpegnode")

class GraphExecutor:
    def __init__(
        self, 
        data_source: Any, 
        plugins: Optional[Dict[str, Any]] = None, 
        use_gpu: bool = False, 
        job_id: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ):
        self.use_gpu = use_gpu
        self.plugins = plugins if plugins is not None else {}
        self.active_engine: Any = None
        self.job_id = job_id
        self.progress_callback = progress_callback
        
        self.graph = data_source if isinstance(data_source, dict) else {}

        # Данные из App.jsx
        self.nodes = {str(n['id']): n for n in self.graph.get('nodes',[])}
        self.edges = self.graph.get('edges', [])
        
        self.incoming_edges: Dict[str, List[str]] = {n_id: [] for n_id in self.nodes}
        self.outgoing_edges: Dict[str, List[str]] = {n_id:[] for n_id in self.nodes}
        
        for edge in self.edges:
            src, tgt = str(edge.get('source')), str(edge.get('target'))
            if src in self.nodes and tgt in self.nodes:
                self.incoming_edges[tgt].append(src)
                self.outgoing_edges[src].append(tgt)

        self._initialize_engine()

    def _initialize_engine(self) -> None:
        # Ищем движок среди загруженных модулей (plugincore)
        for name, mod in self.plugins.items():
            if hasattr(mod, 'Engine'):
                try:
                    # Умная инициализация: проверяем, какие аргументы принимает Engine
                    sig = inspect.signature(mod.Engine)
                    kwargs = {}
                    if 'use_gpu' in sig.parameters:
                        kwargs['use_gpu'] = self.use_gpu
                    if 'job_id' in sig.parameters:
                        kwargs['job_id'] = self.job_id
                        
                    self.active_engine = mod.Engine(**kwargs)
                    logger.info(f"Engine '{name}' activated with args: {kwargs}")
                except Exception as e:
                    logger.error(f"Failed to initialize Engine '{name}': {e}")
                    # Fallback
                    try:
                        self.active_engine = mod.Engine()
                    except Exception as fallback_e:
                        logger.error(f"Fallback initialization failed: {fallback_e}")
                break
        
        if not self.active_engine:
            logger.error("No valid Engine plugin found!")

    def validate_graph(self) -> bool:
        return len(self.nodes) > 0

    def build_and_run(self) -> bool:
        if not self.active_engine:
            return False
        if not self.validate_graph():
            return False

        # Топологическая сортировка для правильного порядка выполнения (от входов к выходам)
        in_degree = {n_id: len(self.incoming_edges[n_id]) for n_id in self.nodes}
        out_degree = {n_id: len(self.outgoing_edges[n_id]) for n_id in self.nodes}
        
        queue =[n_id for n_id, degree in in_degree.items() if degree == 0]
        pipeline_steps: List[Dict[str, Any]] =[]

        while queue:
            curr_id = queue.pop(0)
            node = self.nodes[curr_id]
            
            # Формируем шаг для движка FFmpeg
            params = node.get('params', {}).copy()
            data = node.get('data', {})
            for k, v in data.items():
                if k not in params or not params[k]:
                    params[k] = v
                    
            pipeline_steps.append({
                'id': curr_id,
                'type': node.get('type'),
                'params': params,
                'inputs': node.get('inputs', []), 
                'outputs_count': out_degree[curr_id]
            })

            for neighbor in self.outgoing_edges[curr_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(pipeline_steps) != len(self.nodes):
            logger.error("Graph execution failed: Cycle or disconnected node detected.")
            return False

        try:
            run_method = getattr(self.active_engine, 'run', None)
            if callable(run_method):
                logger.info(f"Launching Engine Pipeline: {len(pipeline_steps)} steps.")
                
                # Проверяем, поддерживает ли run_method аргумент progress_callback
                sig = inspect.signature(run_method)
                kwargs = {}
                if 'progress_callback' in sig.parameters:
                    kwargs['progress_callback'] = self.progress_callback
                
                # Передаем шаги и модули плагинов в worker.py движка FFmpeg
                result = run_method(pipeline_steps, self.plugins, **kwargs)
                return bool(result)
            
            logger.error("Engine lacks a callable 'run' method.")
            return False
        except Exception as e:
            logger.error(f"Execution crash: {e}", exc_info=True)
            return False
