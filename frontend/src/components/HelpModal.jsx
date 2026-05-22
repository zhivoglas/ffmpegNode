// frontend/src/components/HelpModal.jsx
import React from 'react';
/* eslint-disable no-unused-vars */
import { motion, AnimatePresence } from "framer-motion";

export default function HelpModal({ isOpen, onClose }) {
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
              width: '500px', maxWidth: '90vw',
              boxShadow: '0 20px 40px rgba(0,0,0,0.6)',
              display: 'flex', flexDirection: 'column', gap: '16px',
              maxHeight: '90vh', overflowY: 'auto',
              border: '1px solid #334155'
            }}
          >
            {/* ШАПКА */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '12px' }}>
              <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>Справка (Help)</h2>
              <button 
                onClick={onClose} 
                style={{ background: 'transparent', color: '#94a3b8', border: 'none', fontSize: '1.8rem', cursor: 'pointer', lineHeight: 1 }}
              >
                &times;
              </button>
            </div>

            {/* КОНТЕНТ */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', lineHeight: '1.5', fontSize: '0.95rem', color: '#cbd5e1' }}>
              <p>
                Добро пожаловать в <b>ffmpegNode</b>! Здесь вы можете создавать и редактировать графы для обработки видео.
              </p>
              
              {/* МЕСТО ДЛЯ КАРТИНКИ (PNG) */}
              <div style={{ 
                width: '100%', 
                height: '220px', 
                backgroundColor: '#0f172a', 
                borderRadius: '8px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                overflow: 'hidden',
                border: '1px solid #334155'
              }}>
                <img 
                  src="https://dl.dropboxusercontent.com/scl/fi/0abaznu4zzf23k869yehx/ai-generated-8959902.svg?rlkey=xnhu76el8aej76ef5mmfg4mlt&raw=1" 
                  alt="Help Guide" 
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </div>

              <p>
                <b>Основные действия:</b><br/>
                • <b>ЛКМ</b> — Выделение узлов и перемещение<br/>
                • <b>Колесико мыши</b> — Масштабирование рабочей области<br/>
                • <b>Delete / Backspace</b> — Удалить выделенный узел или связь
              </p>
            </div>

            {/* КНОПКА ЗАКРЫТИЯ */}
            <button onClick={onClose} style={{
              marginTop: '10px', padding: '12px', background: '#3b82f6', color: 'white',
              border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold',
              transition: 'background 0.2s'
            }}
            onMouseOver={(e) => e.target.style.background = '#2563eb'}
            onMouseOut={(e) => e.target.style.background = '#3b82f6'}
            >
              Ok
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}