// frontend\src\components\PluginList.jsx 
import React from 'react';

/**
 * Component for displaying grouped plugin list
 * @param {Array} plugins - массив доступных плагинов с бэкенда (с полями inputs, outputs, params)
 * @param {Function} onAddNode - функция добавления принимает объект плагина
 * @param {Object} styles - стили из родителя
 */
const PluginList = ({ plugins, onAddNode, styles }) => {
  const { dropdownItemStyle, pluginItemStyle } = styles;

  if (!plugins || plugins.length === 0) {
    return (
      <div style={{ ...dropdownItemStyle, opacity: 0.5, fontStyle: 'italic', textAlign: 'center' }}>
        Searching for plugins...
      </div>
    );
  }

  return (
    <>
      {plugins.map((plugin) => (
        <div
          key={plugin.id || plugin.name}
          onClick={() => onAddNode(plugin)}
          style={pluginItemStyle}
          className="plugin-item-hover"
        >
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '11px' }}>
              {plugin.name || 'Unnamed Node'}
            </span>
          </div>
        </div>
      ))}
    </>
  );
};

export default PluginList;

