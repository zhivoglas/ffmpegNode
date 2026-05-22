// frontend\src\nodes\GenericNodeStyle.jsx
import { theme } from '../theme';

export const nodeContainerStyle = { background: theme?.colors?.bg_panel || '#1e293b', border: '1px solid', borderRadius: '8px', minWidth: '120px', color: '#f8fafc', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)', overflow: 'hidden' };
export const headerStyle = { padding: '1px 6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,0,0,0.3)', borderBottom: '1px solid rgba(255,255,255,0.05)' };
export const badgeStyle = { fontSize: '7px', fontWeight: 'bold', color: theme?.colors?.accent || '#9e8ffe' };
export const bodyStyle = { padding: '2px' };
export const titleStyle = { fontSize: '8px', fontWeight: 'bold', marginBottom: '2px', textAlign: 'center', color: '#e2e8f0' };
export const portsWrapperStyle = { display: 'flex', justifyContent: 'space-between', gap: '4px' };
export const columnStyle = { display: 'flex', flexDirection: 'column', gap: '2px', flex: 1 };
export const portItemStyle = { display: 'flex', alignItems: 'center', position: 'relative', minHeight: '2px' };
export const portLabelStyle = { fontSize: '7px', marginRight: '11px', marginLeft: '11px', color: '#8497b2', whiteSpace: 'nowrap' };
export const handleStyle = { width: '6px', height: '6px', background: '#3b82f6', border: '2px solid #0f172a' };
export const closeBtnStyle = { lineHeight: 0, height: '8px', fontWeight: '800', border: 'none', background: 'transparent', color: '#89a2c8', cursor: 'pointer', fontSize: '10px' };
export const fileControlStyle = { marginTop: '2px', padding: '2px', borderRadius: '6px', display: 'flex', flexDirection: 'column', gap: '2px', transition: 'background 0.2s ease' };
export const filePathStyle = { fontSize: '8px', color: '#9dc2f2', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontFamily: 'monospace' };
export const actionBtnStyle = { background: '#334155', border: '1px solid #475569', color: '#f8fafc', fontSize: '7px', fontWeight: 'bold', padding: '1px 1px', borderRadius: '4px', cursor: 'pointer', flex: 1, transition: 'background 0.2s' };
