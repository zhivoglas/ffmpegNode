// frontend\src\components\Header.jsx
import React, { useState, useEffect } from 'react';
import { theme } from '../theme';
import { engineCards, /* menuGroups, */ actionButtons } from './headerConfig';
import PluginList from './PluginList';
import { API_BASE_URL } from '../App';
import { headerStyle, logoCardStyle, brandStyle, engineDropdownStyle, largeCardStyle, cardTitleStyle, cardDescStyle, menuContainer,
  menuItemStyle, dropdownStyle, dropdownItemStyle, pluginItemStyle, actionsStyle, dividerStyle, secondaryBtnStyle, renderBtnStyle,
  progressContainerStyle, progressLabelStyle, progressBarStyle, progressFillStyle} from './HeaderStyle';

const Header = ({ onAddNode, onRender, isRendering, progress, currentFile }) => {
  const [availablePlugins, setAvailablePlugins] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/plugins`)
      .then((res) => {
        if (!res.ok) throw new Error('Backend offline');
        return res.json();
      })
      .then((data) => {
        setAvailablePlugins(data?.nodes || []);
      })
      .catch((err) => console.error('Plugin sync failed:', err));
  }, []);

  return (
    <div style={headerStyle}>
      <div className="engine-container" style={logoCardStyle}>
        <div style={brandStyle}>ffmpegNode PRO</div>
        
<div className="engine-dropdown" style={engineDropdownStyle}>
{engineCards.map((card) => (
  <div 
    key={card.title} 
    className="card-item" 
    style={{ ...largeCardStyle, cursor: 'pointer' }}

    onMouseDown={(e) => {
      e.preventDefault();
      e.stopPropagation(); 
      console.log("Клик зафиксирован, URL:", card.url);
      
      if (card.url) {
        // Проверяем, есть ли Electron API
        if (window.electronAPI && window.electronAPI.openExternal) {
          try {
            window.electronAPI.openExternal(card.url);
          } catch (err) {
            console.error("Ошибка Electron API:", err);
            window.open(card.url, '_blank'); // Запасной вариант
          }
        } else {
          // Если мы в обычном браузере (Vite)
          console.log("Открываем через обычный браузер");
          window.open(card.url, '_blank');
        }
      }
    }}
            >
              <span style={{ fontSize: '16px' }}>{card.icon}</span>
              <div style={{ textAlign: 'left' }}>
                <div style={cardTitleStyle}>{card.title}</div>
                <div style={cardDescStyle}>{card.desc}</div>
              </div>
            </div>
          ))}
        </div>
        </div>

{/* NAVIGATION MENUS */}
      <div style={menuContainer}>
{/*         {menuGroups.map((group) => (
          <div key={group.label} className="menu-group" style={menuItemStyle}>
            {group.label}
            <div className="dropdown" style={dropdownStyle}>
              {group.items.map(item => (
                <div key={`${group.label}-${item}`} className="dropdown-item" style={dropdownItemStyle}>
                  {item}
                </div>
              ))}
            </div>
          </div>
        ))} */}

        {/* ДИНАМИЧЕСКИЕ КАТЕГОРИИ ПЛАГИНОВ */}
        {/* Получаем уникальные категории (если категории нет, кидаем в 'Other') */}
        {[...new Set(availablePlugins.map(p => p.category || 'Other'))].map(category => (
          <div key={category} className="menu-group" style={menuItemStyle}>
            {category} {/* Название категории в меню, например "Video" или "Audio" */}
            <div className="dropdown" style={dropdownStyle}>
              {/* Переиспользуем тот же PluginList, но передаем только отфильтрованные плагины */}
              <PluginList 
                plugins={availablePlugins.filter(p => (p.category || 'Other') === category)} 
                onAddNode={onAddNode} 
                styles={{ dropdownItemStyle, pluginItemStyle }} 
              />
            </div>
          </div>
        ))}
      </div>

      {/* RENDER STATUS & CONTROLS */}
      <div style={actionsStyle}>
        {isRendering && (
          <div style={progressContainerStyle}>
            <div style={progressLabelStyle}>
              {currentFile ? currentFile : `Rendering: ${progress}%`}
            </div>
            <div style={progressBarStyle}>
              <div style={{ ...progressFillStyle, width: `${progress}%` }} />
            </div>
          </div>
        )}

        <div style={dividerStyle}>
          {actionButtons.map((btn) => (
            <button key={btn.label} onClick={btn.func} style={secondaryBtnStyle}>
              {btn.label}
            </button>
          ))}
          
          <button 
            onClick={onRender} 
            disabled={isRendering}
            style={{ 
              ...renderBtnStyle,
              opacity: isRendering ? 0.6 : 1,
              cursor: isRendering ? 'not-allowed' : 'pointer',
              boxShadow: isRendering ? 'none' : '0 4px 12px rgba(16, 185, 129, 0.3)'
            }}
          >
            {isRendering ? 'Processing...' : 'Render'}
          </button>
        </div>
      </div>

      <style>{`
        .engine-container:hover .engine-dropdown { display: flex !important; flex-direction: column; gap: 6px; }
        .menu-group { position: relative; transition: 0.2s; border-radius: 4px; }
        .menu-group:hover .dropdown { display: block !important; }
        .menu-group:hover { background: ${theme?.colors?.bg_hover || '#2d3748'}; color: #fff; }
        .card-item:hover { background: ${theme?.colors?.bg_hover || '#2d3748'}; border-color: ${theme?.colors?.accent || '#3b82f6'}; }
        .dropdown-item:hover { background: ${theme?.colors?.bg_hover || '#2d3748'}; color: ${theme?.colors?.accent || '#3b82f6'}; }
        .plugin-item-hover:hover { background: ${theme?.colors?.bg_hover || '#2d3748'}; color: ${theme?.colors?.accent || '#3b82f6'}; }
        .plugin-item:active { transform: scale(0.98); }
      `}</style>
    </div>
  );
};

export default Header;