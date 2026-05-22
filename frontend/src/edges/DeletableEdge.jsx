// frontend\src\edges\DeletableEdge.jsx
import React, { useState } from 'react';
import { BaseEdge, getBezierPath, EdgeLabelRenderer } from 'reactflow';
import { theme } from '../theme';

const DeletableEdge = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const handleDelete = (event) => {
    event.stopPropagation();
    if (data?.onDelete) {
      data.onDelete(id);
    }
  };

  return (
    <>
      <BaseEdge 
        path={edgePath} 
        style={{ 
          ...style, 
          strokeWidth: isHovered ? 4 : 2, 
          stroke: isHovered ? theme.colors.accent : theme.colors.border,
          transition: 'stroke 0.2s, stroke-width 0.2s'
        }} 
        markerEnd={markerEnd} 
      />
      
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            fontSize: 12,
            pointerEvents: 'all',
            zIndex: 1001,
          }}
          className="nodrag nopan"
        >
          <button 
            style={{
              ...deleteButtonStyle,
              background: isHovered ? theme.colors.error : '#0f172a',
              color: isHovered ? '#fff' : '#94a3b8',
              borderColor: isHovered ? theme.colors.error : theme.colors.border,
              transform: isHovered ? 'scale(1.2)' : 'scale(1)',
            }} 
            onClick={handleDelete}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            title="Remove connection"
          >
            ×
          </button>
        </div>
      </EdgeLabelRenderer>
    </>
  );
};

const deleteButtonStyle = {
  width: '11px',
  height: '11px',
  borderRadius: '50%',
  border: '1px solid',
  fontSize: '12px',
  lineHeight: '1',
  textAlign: 'center',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '0 0 2px 0',
  boxShadow: '0 2px 8px rgba(0,0,0,0.5)',
  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
};

export default DeletableEdge;
