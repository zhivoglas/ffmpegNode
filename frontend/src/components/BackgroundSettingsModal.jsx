import React from 'react';
/* eslint-disable no-unused-vars */
import { motion, AnimatePresence } from "framer-motion";

export default function BackgroundSettingsModal({ isOpen, onClose, settings, setSettings }) {
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' || type === 'range' ? parseFloat(value) : value)
    }));
  };

  const isAuto = settings.selectedImage === 'auto';
  const isAnimEnabled = settings.enableAnimation && isAuto;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex', justifyContent: 'center', alignItems: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(4px)'
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.95 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            onClick={(e) => e.stopPropagation()}
            style={{
              backgroundColor: '#1e293b', color: 'white',
              padding: '24px', borderRadius: '12px',
              width: '420px', boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
              display: 'flex', flexDirection: 'column', gap: '16px',
              maxHeight: '90vh', overflowY: 'auto',
              border: '1px solid #334155'
            }}
          >
            {/* ШАПКА */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '12px' }}>
              <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>Настройки фона</h2>
              <button 
                onClick={onClose} 
                style={{ background: 'transparent', color: '#94a3b8', border: 'none', fontSize: '1.8rem', cursor: 'pointer', lineHeight: 1 }}
              >
                &times;
              </button>
            </div>

            {/* ГЛОБАЛЬНЫЕ ПЕРЕКЛЮЧАТЕЛИ */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '12px', background: '#0f172a', borderRadius: '8px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', fontSize: '0.95rem' }}>
                <input type="checkbox" name="showAnimatedBg" checked={settings.showAnimatedBg} onChange={handleChange} style={{ width: '16px', height: '16px' }} />
                Показывать картинки на фоне
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', fontSize: '0.95rem' }}>
                <input type="checkbox" name="showGrid" checked={settings.showGrid} onChange={handleChange} style={{ width: '16px', height: '16px' }} />
                Показывать сетку (линии графа)
              </label>
            </div>

            {/* НАСТРОЙКИ КАРТИНОК */}
            {settings.showAnimatedBg && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
              >
                <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.9rem', color: '#94a3b8' }}>
                  Выбор фона:
                  <select name="selectedImage" value={settings.selectedImage} onChange={handleChange} style={{ padding: '10px', background: '#0f172a', color: 'white', border: '1px solid #3b82f6', borderRadius: '6px', outline: 'none' }}>
                    <option value="auto">Слайдшоу (Все картинки)</option>
                    <option value="0">Картинка 1 (Синяя абстракция)</option>
                    <option value="1">Картинка 2 (AI Градиент)</option>
                    <option value="2">Картинка 3 (Самолет)</option>
                  </select>
                </label>

                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', opacity: isAuto ? 1 : 0.5, fontSize: '0.95rem' }}>
                  <input type="checkbox" name="enableAnimation" checked={settings.enableAnimation} onChange={handleChange} disabled={!isAuto} />
                  Анимировать фон (переходы)
                </label>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <label style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.9rem' }}>
                    Прозрачность: <span style={{ color: '#3b82f6' }}>{settings.opacity}</span>
                    <input type="range" name="opacity" min="0" max="1" step="0.05" value={settings.opacity} onChange={handleChange} style={{ cursor: 'pointer' }} />
                  </label>

                  <label style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.9rem', opacity: isAnimEnabled ? 1 : 0.5 }}>
                    Время перехода (сек): <span style={{ color: '#3b82f6' }}>{settings.transitionDuration}</span>
                    <input type="range" name="transitionDuration" min="0.5" max="10" step="0.5" value={settings.transitionDuration} onChange={handleChange} disabled={!isAnimEnabled} />
                  </label>

                  <label style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.9rem', opacity: isAnimEnabled ? 1 : 0.5 }}>
                    Время удержания (сек): <span style={{ color: '#3b82f6' }}>{settings.holdDuration}</span>
                    <input type="range" name="holdDuration" min="1" max="20" step="1" value={settings.holdDuration} onChange={handleChange} disabled={!isAnimEnabled} />
                  </label>

                  <label style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.9rem', opacity: isAnimEnabled ? 1 : 0.5 }}>
                    Масштаб (Zoom): <span style={{ color: '#3b82f6' }}>{settings.scale}</span>
                    <input type="range" name="scale" min="1" max="2" step="0.1" value={settings.scale} onChange={handleChange} disabled={!isAnimEnabled} />
                  </label>
                </div>

                <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.9rem', opacity: isAnimEnabled ? 1 : 0.5 }}>
                  Тип перехода:
                  <select name="transitionType" value={settings.transitionType} onChange={handleChange} disabled={!isAnimEnabled} style={{ padding: '10px', background: '#0f172a', color: 'white', border: '1px solid #3b82f6', borderRadius: '6px' }}>
                    <option value="none">Без анимации (Мгновенно)</option>
                    <option value="fade">Fade (Затухание)</option>
                    <option value="zoom">Zoom (Приближение)</option>
                    <option value="slide-left">Slide Left (Влево)</option>
                    <option value="slide-right">Slide Right (Вправо)</option>
                    <option value="slide-up">Slide Up (Вверх)</option>
                    <option value="slide-down">Slide Down (Вниз)</option>
                    <option value="random">Random (Случайный)</option>
                  </select>
                </label>
              </motion.div>
            )}

            <button onClick={onClose} style={{
              marginTop: '10px', padding: '12px', background: '#3b82f6', color: 'white',
              border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold',
              transition: 'background 0.2s'
            }}
            onMouseOver={(e) => e.target.style.background = '#2563eb'}
            onMouseOut={(e) => e.target.style.background = '#3b82f6'}
            >
              Готово
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
