// frontend\src\AppPlugins.jsx
import { useState, useRef, useCallback } from 'react';

export let API_BASE_URL = 'http://127.0.0.1:8000';

export const setApiBaseUrl = (url) => {
  API_BASE_URL = url;
};

export const useAppPlugins = (nodes, edges, setNodes) => {
  const [isRendering, setIsRendering] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState('');
  const pollRef = useRef(null);

const stopPolling = useCallback((msg) => {
    if (pollRef.current) clearInterval(pollRef.current);
    setIsRendering(false);
    setCurrentFile('');
    setProgress(0); // Сбрасываем прогресс
    if (msg) alert(msg);
  }, []);

  const startPolling = useCallback((jobId) => {
    // Уменьшаем интервал до 200мс для плавности
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/render/${jobId}`);
        const data = await res.json();
        
        // Если рендер успешно завершен
        if (data.status === 'completed') {
          if (pollRef.current) clearInterval(pollRef.current);
          
          setProgress(100);
          setCurrentFile('Render Complete!');
          setTimeout(() => {
            stopPolling('Render Success!');
          }, 600);
          return;
        }

        if (data.status === 'failed') {
          stopPolling(`Error: ${data.error}`);
          return;
        }

        setProgress(data.progress || 0);
        if (data.current_file) setCurrentFile(data.current_file);
        
      } catch {
        stopPolling('Connection lost to Python backend');
      }
    }, 100);
  }, [stopPolling]);

  const sendToPython = useCallback(async () => {
    setIsRendering(true);
    setProgress(0);
    setCurrentFile('');

    const pipeline_steps = nodes.map(node => {
      const nodeInputs = edges
        .filter(e => e.target === node.id)
        .map(e => ({
          source_node: e.source,
          source_handle: e.sourceHandle || 'output',
          target_handle: e.targetHandle || 'input'
        }));

      const systemFields = ['label', 'category', 'inputs', 'outputs', 'pluginId', 'name', 'options'];
      const params = Object.keys(node.data)
        .filter(key => !systemFields.includes(key))
        .reduce((obj, key) => ({ ...obj, [key]: node.data[key] }), {});

      return {
        id: node.id,
        type: node.data.pluginId || node.type,
        params,
        inputs: nodeInputs
      };
    });

    try {
      const response = await fetch(`${API_BASE_URL}/render`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          nodes: pipeline_steps, 
          edges: edges, 
          settings: { use_gpu: true }
        }),
      });
      
      const { job_id } = await response.json();
      startPolling(job_id);
    } catch {
      stopPolling('Render Start Failed. Is Python backend running?');
    }
  }, [nodes, edges, startPolling, stopPolling]);

  const addNode = useCallback((plugin, screenToFlowPosition, nodeTypes) => {
    const id = `${plugin.id}_${Date.now()}`;
    const position = screenToFlowPosition({ 
      x: window.innerWidth / 2, 
      y: window.innerHeight / 2 
    });

    const newNode = {
      id,
      type: nodeTypes[plugin.type] ? plugin.type : 'default', 
      position,
      data: { 
        ...plugin.params,
        label: (plugin.name || 'Plugin').toUpperCase(),
        pluginId: plugin.id,
        category: plugin.category || 'NODE',
        inputs: plugin.inputs || [],
        outputs: plugin.outputs || [],
        name: plugin.name,
        options: plugin.options || {}
      },
    };

    setNodes((nds) => nds.concat(newNode));
  }, [setNodes]);

  return {
    isRendering,
    progress,
    currentFile,
    sendToPython,
    addNode,
    pollRef
  };
};