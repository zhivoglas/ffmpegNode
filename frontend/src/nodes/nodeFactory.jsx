// frontend/src/nodes/nodeFactory.js
import GenericNode from './GenericNode';

export const nodeTypes = {
  default: GenericNode,
};

/**
 * Получение компонента ноды по типу.
 * Если кастомный UI для плагина не прописан, возвращается GenericNode.
 * 
 * @param {string} type - тип ноды (из manifest.json)
 * @returns React компонент ноды
 */ 
export const getNodeComponent = (type) => {
  if (!type) return nodeTypes.default;
  return nodeTypes[type.toLowerCase()] || nodeTypes.default;
};