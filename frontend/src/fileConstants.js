// frontend\src\fileConstants.js
export const FILE_TYPES = {
    VIDEO: ['mp4', 'mov', 'mkv', 'avi', 'webm', 'flv'],
    IMAGE: ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'gif'],
    AUDIO: ['mp3', 'wav', 'ogg', 'm4a', 'flac'],
    TEXT: ['txt', 'json', 'csv', 'md', 'srt', 'vtt']
};

// Все поддерживаемые расширения одним списком
export const ALL_SUPPORTED_EXTENSIONS = [
    ...FILE_TYPES.VIDEO,
    ...FILE_TYPES.IMAGE,
    ...FILE_TYPES.AUDIO,
    ...FILE_TYPES.TEXT
];

// Готовые пресеты фильтров для диалоговых окон Electron
export const ELECTRON_FILTERS = {
    VIDEO: { name: 'Video Files', extensions: FILE_TYPES.VIDEO },
    IMAGE: { name: 'Image Files', extensions: FILE_TYPES.IMAGE },
    AUDIO: { name: 'Audio Files', extensions: FILE_TYPES.AUDIO },
    TEXT: { name: 'Text Files', extensions: FILE_TYPES.TEXT },
    ALL: { name: 'All Supported Files', extensions: ALL_SUPPORTED_EXTENSIONS },
    ANY: { name: 'Any Files', extensions: ['*'] }
};

export const getExtensionsFromData = (data) => {
    // 1. Check if manifest explicitly defines extensions
    const exts = data?.params?.extensions || data?.extensions;
    if (exts) {
        return exts.split(',').map(e => e.replace('.', '').trim().toLowerCase());
    }
    
    // 2. Infer from output type
    const outType = data?.outputs?.[0]?.type;
    if (outType === 'image') return FILE_TYPES.IMAGE;
    if (outType === 'audio') return FILE_TYPES.AUDIO;
    if (outType === 'video') return FILE_TYPES.VIDEO;
    if (outType === 'text') return FILE_TYPES.TEXT;
    
    // 3. Infer from pluginId or category
    if (data?.pluginId?.includes('image')) return FILE_TYPES.IMAGE;
    if (data?.pluginId?.includes('audio')) return FILE_TYPES.AUDIO;
    if (data?.pluginId?.includes('text')) return FILE_TYPES.TEXT;
    
    // Default to all supported
    return ALL_SUPPORTED_EXTENSIONS;
};

export const getFiltersFromData = (data) => {
    const exts = getExtensionsFromData(data);
    return [
        { name: 'Supported Files', extensions: exts },
        ELECTRON_FILTERS.ANY
    ];
};
