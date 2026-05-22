// frontend\src\components\headerConfig.jsx
export const engineCards = [
  { 
    title: 'Get ffmpegNode', 
    desc: 'installation required', 
    icon: '🎬',
    url: 'https://google.com'
  },
  { 
    title: 'YouTube lessons', 
    desc: 'Educational materials',
    icon: '▶️',
    url: 'https://google.com'
  },
];

/* export const menuGroups = [
  { 
    label: 'File', 
    items: ['New Project', 'Open Source', 'Save Workspace', 'Export Project'] 
  },
  { 
    label: 'Edit', 
    items: ['Undo', 'Redo', 'Clear Canvas', 'Settings'] 
  },
]; */

export const actionButtons = [
/*   { label: 'Timeline', func: () => console.log('Action: Timeline') },
  { label: 'Inspector', func: () => console.log('Action: Inspector') }, */
  { label: 'Help', func: () => window.dispatchEvent(new CustomEvent('open-help-modal')) },
  { label: '⚙️', func: () => window.dispatchEvent(new CustomEvent('open-bg-settings')) },
];