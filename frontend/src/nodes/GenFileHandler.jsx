// frontend\src\nodes\GenFileHandler.jsx
import { useState } from 'react';
import { useReactFlow } from 'reactflow';
import { getFiltersFromData, getExtensionsFromData, ALL_SUPPORTED_EXTENSIONS } from '../fileConstants';

export const useGenFileHandler = (id, data) => { 
  const { setNodes, setEdges } = useReactFlow();
  const [isDragging, setIsDragging] = useState(false);
  const isInputNode = data.type === 'input' || data.pluginId === 'input' || (data.category === 'source' && data.type !== 'batch_input' && data.pluginId !== 'batch_input');
  const isBatchInputNode = data.type === 'batch_input' || data.pluginId === 'batch_input';
  const isOutputNode = data.type === 'output' || data.pluginId === 'output' || data.category === 'output';
  const handleDeleteNode = (e) => {
    e.stopPropagation();
    setNodes((nds) => nds.filter((n) => n.id !== id));
    setEdges((eds) => eds.filter((e) => e.source !== id && e.target !== id));
  };

  const updateFilePath = (newPath, additionalData = {}) => {
    const normalizedPath = newPath.replace(/\\/g, '/');
    setNodes((nds) =>
      nds.map((n) => n.id === id ? { 
        ...n, 
        data: { 
          ...n.data, 
          ...additionalData, 
          file_path: normalizedPath,
          dir_path: undefined 
        } 
      } : n)
    );
  };

  const shortenPath = (path) => {
    if (!path) return 'No path selected';
    if (path.length <= 28) return path;
    const parts = path.split(/[/\\]/);
    if (parts.length <= 2) return path;
    return `${parts[0]}/.../${parts[parts.length - 1]}`;
  };

  const handleBrowseInputFile = async () => {
    if (window.electronAPI) {
      const path = await window.electronAPI.openFile({
        filters: getFiltersFromData(data)
      });
      if (path) {
        updateFilePath(path, { file_count: undefined });
      }
    }
  };

  const handleBrowseInputDir = async () => {
    if (window.electronAPI) {
      const result = await window.electronAPI.scanDir({
        extensions: getExtensionsFromData(data)
      });
      if (result && result.path) {
        updateFilePath(result.path, { file_count: result.count });
      }
    }
  };

  const handleBrowseOutputFile = async () => {
    if (window.electronAPI) {
      const path = await window.electronAPI.saveFile({ 
        defaultPath: 'output.mp4',
        filters: getFiltersFromData(data)
      });
      if (path) updateFilePath(path);
    }
  };

  const handleBrowseOutputDir = async () => {
    if (window.electronAPI) {
      const path = await window.electronAPI.openDir();
      if (path) updateFilePath(`${path.replace(/\\/g, '/')}/output.mp4`);
    }
  };

  const onDragOver = (e) => {
    e.preventDefault();
    if (isInputNode || isBatchInputNode || isOutputNode) setIsDragging(true);
  };

  const onDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const onDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if ((isInputNode || isBatchInputNode || isOutputNode) && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      let path = file.path; 
      if (!path) return; 
      
      path = path.replace(/\\/g, '/');

      if (isOutputNode) {
        if (!path.match(/\.[a-zA-Z0-9]+$/)) path = `${path}/output.mp4`;
        updateFilePath(path);
      } 
      else if (isInputNode || isBatchInputNode) {
        if (window.electronAPI) {
          const result = await window.electronAPI.scanDir({
            dropPath: path,
            extensions: getExtensionsFromData(data)
          });
          if (result.count > 0 || !path.match(/\.[a-zA-Z0-9]+$/)) {
             updateFilePath(result.path, { file_count: result.count });
          } else {
            updateFilePath(path);
          }
        }
      }
    }
  };

  return {
    isDragging,
    isInputNode,
    isBatchInputNode,
    isOutputNode,
    handleDeleteNode,
    shortenPath,
    handleBrowseInputFile,
    handleBrowseInputDir,
    handleBrowseOutputFile,
    handleBrowseOutputDir,
    onDragOver,
    onDragLeave,
    onDrop
  };
};
