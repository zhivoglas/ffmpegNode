// frontend\src\components\HeaderStyle.jsx
import { theme } from '../theme';

export const headerStyle = { overflow: 'visible', height: '28px', background: '#0f172a', display: 'flex', alignItems: 'center', padding: '2px 9px', borderBottom: '1px solid #1e293b', zIndex: 5000 };
export const logoCardStyle = { background: theme?.colors?.accent || '#4388f8', padding: '0px 30px', borderRadius: '6px', marginRight: '24px', position: 'relative', cursor: 'pointer' };
export const brandStyle = { fontWeight: '900', fontSize: '15px', color: '#fff' };
export const engineDropdownStyle = { display: 'none', position: 'absolute', top: '100%', left: 0, background: '#1e293b', width: '220px', padding: '6px', zIndex: 5001, borderRadius: '8px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)' };
export const largeCardStyle = { background: '#0f172a', padding: '12px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '12px', border: '1px solid #334155', marginBottom: '4px' };
export const cardTitleStyle = { fontWeight: 'bold', fontSize: '12px', color: '#fff' };
export const cardDescStyle = { fontSize: '10px', opacity: 0.5, color: '#77b2fb' };
export const menuContainer = { display: 'flex', gap: '4px', flex: 1 };
export const menuItemStyle = { padding: '8px 14px', cursor: 'pointer', fontSize: '12px', fontWeight: '600', color: '#9eb7d9', display: 'flex', alignItems: 'center' };
export const dropdownStyle = { display: 'none', position: 'absolute', top: '100%', left: 0, background: '#1e293b', minWidth: '120px', zIndex: 5001, borderRadius: '0 0 8px 8px', border: '1px solid #48586f', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.3)', overflow: 'hidden' };
export const dropdownItemStyle = { padding: '10px 16px', borderBottom: '1px solid #334155', fontSize: '12px', cursor: 'pointer', color: '#94a3b8' };
export const pluginItemStyle = { padding: '10px 16px', borderBottom: '1px solid #334155', cursor: 'pointer', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '10px', color: '#f1f5f9' };
export const actionsStyle = { display: 'flex', alignItems: 'center', gap: '20px' };
export const dividerStyle = { display: 'flex', gap: '12px', borderLeft: '1px solid #334155', paddingLeft: '20px', alignItems: 'center' };
export const secondaryBtnStyle = { background: 'transparent', border: 'none', color: '#a8c9f9', fontSize: '12px', cursor: 'pointer', fontWeight: '500' };
export const renderBtnStyle = { background: '#10b981', border: 'none', color: '#fff', padding: '1px 18px', borderRadius: '6px', fontWeight: 'bold', fontSize: '13px' };
export const progressContainerStyle = { display: 'flex', flexDirection: 'column', width: '260px' };
export const progressLabelStyle = { fontSize: '10px', fontWeight: 'bold', color: '#10b981', marginBottom: '6px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' };
export const progressBarStyle = { height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden', border: '1px solid #334155' };
export const progressFillStyle = { height: '100%', background: '#10b981', transition: 'width 0.4s ease' };
