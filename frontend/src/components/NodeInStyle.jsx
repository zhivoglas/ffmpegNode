import { theme } from '../theme';

export const inspectorStyle = {
  position: 'absolute',
  right: '20px',
  top: '80px',
  width: '180px',
  maxHeight: '80vh',
  overflowY: 'auto',
  background: theme?.colors?.bg_panel || '#1e293b',
  border: `1px solid ${theme?.colors?.border || '#334155'}`,
  borderRadius: '12px',
  zIndex: 1000,
  boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)',
  color: '#f1f5f9',
  touchAction: 'none',
};

export const headerStyle = {
  padding: '5px',
  borderBottom: `1px solid ${theme?.colors?.border || '#334155'}`,
  background: 'rgba(0,0,0,0.2)',
  cursor: 'grab',
  userSelect: 'none',
};

export const nodeNameStyle = {
  fontSize: '12px',
  fontWeight: '600',
  color: '#fff',
  marginTop: '4px',
  textAlign: 'center'
};

export const bodyStyle = {
  padding: '10px'
};

export const fieldStyle = {
  marginBottom: '16px'
};

export const labelStyle = {
  display: 'block',
  fontSize: '10px',
  marginBottom: '8px',
  fontWeight: '600',
  color: '#b4c8e4'
};

export const inputStyle = {
  width: '100%',
  background: '#0f172a',
  border: '1px solid #334155',
  borderRadius: '6px',
  padding: '6px 4px',
  color: '#f8fafc',
  fontSize: '12px',
  outline: 'none',
  boxSizing: 'border-box',
  transition: 'border-color 0.2s, box-shadow 0.2s',
};

export const selectStyle = {
  ...inputStyle,
  cursor: 'pointer',
  appearance: 'auto',
};

export const checkboxWrapperStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px'
};

export const checkboxStyle = {
  width: '16px',
  height: '16px',
  cursor: 'pointer',
  accentColor: theme?.colors?.primary || '#a292fa'
};

export const emptyStateStyle = {
  textAlign: 'center',
  fontSize: '12px',
  color: '#677a94',
  padding: '20px 0',
  fontStyle: 'italic'
};
