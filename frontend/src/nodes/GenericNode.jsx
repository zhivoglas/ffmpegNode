// frontend\src\nodes\GenericNode.jsx
import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { theme } from '../theme';
import { useGenFileHandler } from './GenFileHandler';
import {
  nodeContainerStyle,
  headerStyle,
  badgeStyle,
  bodyStyle,
  titleStyle,
  portsWrapperStyle,
  columnStyle,
  portItemStyle,
  portLabelStyle,
  handleStyle,
  closeBtnStyle,
  fileControlStyle,
  filePathStyle,
  actionBtnStyle
} from './GenericNodeStyle';

const GenericNode = ({ id, data, selected }) => {
  const {
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
  } = useGenFileHandler(id, data);

  const inputs = data.inputs || [];
  const outputs = data.outputs || [];

  return (
    <div 
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      style={{
        ...nodeContainerStyle,
        borderColor: selected ? (theme?.colors?.primary || '#3b82f6') : (theme?.colors?.border || '#334155'),
        boxShadow: isDragging ? `0 0 15px ${theme?.colors?.primary || '#3b82f6'}` : nodeContainerStyle.boxShadow,
        transform: isDragging ? 'scale(1.02)' : 'scale(1)',
        transition: 'all 0.2s ease'
      }}
    >
      <div style={headerStyle}>
        <div style={badgeStyle}>{data.category || 'NODE'}</div>
        <button type="button" onClick={handleDeleteNode} style={closeBtnStyle}>×</button>
      </div>

      <div style={bodyStyle}>
        <div style={titleStyle}>{data.name || data.label || 'Plugin'}</div>

        <div style={portsWrapperStyle}>
          <div style={columnStyle}>
            {inputs.map((input) => (
              <div key={input.id} style={portItemStyle}>
                <Handle type="target" position={Position.Left} id={input.id} style={handleStyle} />
                <span style={portLabelStyle}>{input.label || input.id}</span>
              </div>
            ))}
          </div>

          <div style={{ ...columnStyle, alignItems: 'flex-end' }}>
            {outputs.map((output) => (
              <div key={output.id} style={portItemStyle}>
                <span style={portLabelStyle}>{output.label || output.id}</span>
                <Handle type="source" position={Position.Right} id={output.id} style={handleStyle} />
              </div>
            ))}
          </div>
        </div>

        {/* FILE CONTROLS FOR SINGLE INPUT NODE */}
        {isInputNode && (
          <div style={{...fileControlStyle, background: isDragging ? 'rgba(59, 130, 246, 0.2)' : 'rgba(0,0,0,0.2)'}}>
            <div style={filePathStyle} title={data.file_path || data.dir_path}>
              {shortenPath(data.file_path || data.dir_path)}
            </div>
            <div style={{ display: 'flex', gap: '4px' }}>
              <button onClick={handleBrowseInputFile} style={{...actionBtnStyle, width: '100%'}}>FILE</button>
            </div>
          </div>
        )}

        {/* FILE CONTROLS FOR BATCH INPUT NODE */} 
        {isBatchInputNode && (
          <div style={{...fileControlStyle, background: isDragging ? 'rgba(59, 130, 246, 0.2)' : 'rgba(0,0,0,0.2)'}}>
            <div style={filePathStyle} title={data.file_path || data.dir_path}>
              {shortenPath(data.file_path || data.dir_path)}
            </div>
            {data.file_count !== undefined && (
              <div style={{ fontSize: '9px', color: '#3b82f6', textAlign: 'center', marginBottom: '4px' }}>
                Batch mode: {data.file_count} files
              </div>
            )}
            <div style={{ display: 'flex', gap: '4px' }}>
              <button onClick={handleBrowseInputDir} style={{...actionBtnStyle, width: '100%'}}>FOLDER</button>
            </div>
          </div>
        )}

        {/* FILE CONTROLS FOR OUTPUT NODE */}
        {isOutputNode && (
          <div style={{...fileControlStyle, background: isDragging ? 'rgba(16, 185, 129, 0.2)' : 'rgba(0,0,0,0.2)'}}>
            <div style={filePathStyle} title={data.file_path}>
              {shortenPath(data.file_path || 'output.mp4')}
            </div>
            <div style={{ display: 'flex', gap: '4px' }}>
              <button onClick={handleBrowseOutputFile} style={actionBtnStyle}>FILE</button>
              <button onClick={handleBrowseOutputDir} style={actionBtnStyle}>FOLDER</button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default memo(GenericNode);
