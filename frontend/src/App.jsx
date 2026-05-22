// frontend\src\App.jsx
import React, { useCallback, useState, useEffect } from 'react';
import ReactFlow, { 
  useNodesState, 
  useEdgesState, 
  addEdge, 
  Background, 
  Controls, 
  MiniMap, 
  useReactFlow, 
  ReactFlowProvider, 
  Panel 
} from 'reactflow';
import 'reactflow/dist/style.css';

import Header from './components/Header';
import NodeInspector from './components/NodeInspector';
import { nodeTypes } from './nodes/nodeFactory';
import { theme } from './theme';
import DeletableEdge from './edges/DeletableEdge';

import { appContainerStyle, workspaceStyle, panelStyle, panelBtnStyle } from './AppStyle';
import { useAppPlugins, setApiBaseUrl } from './AppPlugins';

import AnimatedBackground from './components/AnimatedBackground';
import BackgroundSettingsModal from './components/BackgroundSettingsModal';
import HelpModal from './components/HelpModal';

export { API_BASE_URL } from './AppPlugins';

const defaultBgSettings = {
  opacity: 0.4,
  transitionDuration: 2,
  holdDuration: 5,
  scale: 1.1,
  transitionType: 'zoom',
  showAnimatedBg: true,   // Показывать ли картинки вообще
  enableAnimation: true,  // Включено ли слайдшоу/анимация
  selectedImage: 'auto',  // 'auto' или индекс картинки (0, 1, 2)
  showGrid: true          // Показывать ли сетку ReactFlow
};

const FlowEditor = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isReady, setIsReady] = useState(false);

  const [isBgSettingsOpen, setIsBgSettingsOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [bgSettings, setBgSettings] = useState(() => {
  const saved = localStorage.getItem('ffmpegNode_bg_settings');
    return saved ? { ...defaultBgSettings, ...JSON.parse(saved) } : defaultBgSettings;
  });

    useEffect(() => {
    localStorage.setItem('ffmpegNode_bg_settings', JSON.stringify(bgSettings));
  }, [bgSettings]);

  // Слушаем событие от кнопки ⚙️ из Header
  useEffect(() => {
    const handleOpenSettings = () => setIsBgSettingsOpen(true);
    const handleOpenHelp = () => setIsHelpOpen(true);
    window.addEventListener('open-bg-settings', handleOpenSettings);
    window.addEventListener('open-help-modal', handleOpenHelp);
    return () => window.removeEventListener('open-bg-settings', handleOpenSettings);
  }, []);
  
  const { screenToFlowPosition } = useReactFlow();
  const {
    isRendering,
    progress,
    currentFile,
    sendToPython,
    addNode
  } = useAppPlugins(nodes, edges, setNodes);

  useEffect(() => {
    const initApp = async () => {
      if (window.electronAPI && window.electronAPI.getBackendPort) {
        try {
          const port = await window.electronAPI.getBackendPort();
          setApiBaseUrl(`http://127.0.0.1:${port}`);
          console.log("Backend connected on:", `http://127.0.0.1:${port}`);
        } catch (e) {
          console.error("Failed to get backend port", e);
        }
      }
      setIsReady(true);
    };
    initApp();
  }, []);

  const handleEdgeDelete = useCallback((edgeId) => {
    setEdges((eds) => eds.filter((e) => e.id !== edgeId));
  }, [setEdges]);

  useEffect(() => {
    const saved = localStorage.getItem('ffmpegNode_graph');
    if (saved) {
      try {
        const { nodes: sn, edges: se } = JSON.parse(saved);
        setNodes(sn || []);
        
        const restoredEdges = (se || []).map(edge => ({
          ...edge,
          data: { ...edge.data, onDelete: handleEdgeDelete }
        }));
        setEdges(restoredEdges);
      } catch {
        console.error("Failed to parse saved graph");
      }
    }
  }, [setNodes, setEdges, handleEdgeDelete]);

  const saveGraph = useCallback(() => {
    localStorage.setItem('ffmpegNode_graph', JSON.stringify({ nodes, edges }));
    alert("Graph saved locally!");
  }, [nodes, edges]);

  const onConnect = useCallback((params) => {
    const isPortBusy = edges.some(
      (e) => e.target === params.target && e.targetHandle === params.targetHandle
    );
    if (isPortBusy) return;

    const edge = { 
      ...params, 
      id: `edge_${Date.now()}`,
      type: 'deletable', 
      animated: true,
      data: { onDelete: handleEdgeDelete } 
    };
    setEdges((eds) => addEdge(edge, eds));
  }, [edges, setEdges, handleEdgeDelete]);

  const handleAddNode = useCallback((plugin) => {
    addNode(plugin, screenToFlowPosition, nodeTypes);
  }, [addNode, screenToFlowPosition]);

  if (!isReady) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#0f172a', color: 'white' }}>
        <h2>Initializing ffmpegNode Engine...</h2>
      </div>
    );
  }

  return (
    <div style={appContainerStyle}>
      <Header 
        onAddNode={handleAddNode} 
        onRender={sendToPython} 
        isRendering={isRendering} 
        progress={progress} 
        currentFile={currentFile}
      />
      
      <div style={workspaceStyle}>
        {bgSettings.showAnimatedBg && <AnimatedBackground settings={bgSettings} />}
          <BackgroundSettingsModal 
          isOpen={isBgSettingsOpen} 
          onClose={() => setIsBgSettingsOpen(false)} 
          settings={bgSettings} 
          setSettings={setBgSettings} 
        />
        <HelpModal 
          isOpen={isHelpOpen} 
          onClose={() => setIsHelpOpen(false)} 
        />
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          edgeTypes={{ deletable: DeletableEdge }}
          onNodeClick={(_, node) => setSelectedNode(node)}
          onPaneClick={() => setSelectedNode(null)}
          fitView
        >
          {bgSettings.showGrid && <Background variant="lines" color="#1e293b" />}
          <Controls />
          <MiniMap style={{ background: theme.colors.bg_panel }} />
          
          <Panel position="top-right" style={panelStyle}>
            <button style={panelBtnStyle} onClick={saveGraph}>SAVE</button>
            <button style={panelBtnStyle} onClick={() => { localStorage.clear(); window.location.reload(); }}>RESET</button>
          </Panel>

          {selectedNode && (
            <NodeInspector 
              node={nodes.find(n => n.id === selectedNode.id)}
              onChange={(newData) => {
                setNodes(nds => nds.map(n => n.id === selectedNode.id 
                  ? { ...n, data: { ...n.data, ...newData } } 
                  : n
                ));
              }} 
            />
          )}
        </ReactFlow>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <ReactFlowProvider>
      <FlowEditor />
    </ReactFlowProvider>
  );
}
