// frontend\src\components\NodeInspector.jsx
import React, { useRef } from 'react';
import Draggable from 'react-draggable';
import {
  inspectorStyle, headerStyle, nodeNameStyle, bodyStyle, fieldStyle, labelStyle, inputStyle,
  selectStyle, checkboxWrapperStyle, checkboxStyle, emptyStateStyle
} from './NodeInStyle';

const NodeInspector = ({ node, onChange }) => {
  const nodeRef = useRef(null);

  if (!node) return null;

  const SYSTEM_FIELDS = ['label', 'id', 'category', 'inputs', 'outputs', 'type', 'name', 'options'];
  
  const handleInputChange = (key, value) => {
    onChange({ ...node.data, [key]: value });
  };

  const editableFields = Object.entries(node.data).filter(([key]) => !SYSTEM_FIELDS.includes(key));

  return (
    <Draggable 
      nodeRef={nodeRef} 
      handle=".drag-header" 
      bounds="parent"
    >
      <div ref={nodeRef} style={inspectorStyle}>
        <div style={{ ...headerStyle, cursor: 'grab' }} className="drag-header">
          <div style={nodeNameStyle}>{node.data.name || node.data.label || 'NODE'}</div>
        </div>

        <div style={bodyStyle}>
          {editableFields.length > 0 ? (
            editableFields.map(([key, value]) => {
              const optionsList = node.data.options?.[key];

              return (
                <div key={key} style={fieldStyle}>
                  <label style={labelStyle}>{key.replace(/_/g, ' ').toUpperCase()}</label>
                  
                  {optionsList ? (
                    <select 
                      value={value} 
                      onChange={(e) => handleInputChange(key, e.target.value)}
                      style={selectStyle}
                    >
                      {optionsList.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                    </select>
                  ) : 
                  typeof value === 'boolean' ? (
                    <div style={checkboxWrapperStyle}>
                      <input 
                        type="checkbox" 
                        checked={value}
                        onChange={(e) => handleInputChange(key, e.target.checked)}
                        style={checkboxStyle}
                      />
                      <span style={{ fontSize: '12px', color: '#94a3b8' }}>Enable</span>
                    </div>
                  ) : (
                    <input 
                      type={typeof value === 'number' ? 'number' : 'text'} 
                      style={inputStyle} 
                      value={value ?? ''} 
                      onChange={(e) => handleInputChange(key, typeof value === 'number' ? parseFloat(e.target.value) || 0 : e.target.value)} 
                    />
                  )}
                </div>
              );
            })
          ) : (
            <div style={emptyStateStyle}>No adjustable parameters</div>
          )}
        </div>
      </div>
    </Draggable>
  );
};

export default NodeInspector;
