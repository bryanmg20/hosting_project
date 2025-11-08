/**
 * API Index - Re-exporta todas las funciones y tipos
 * Mantiene compatibilidad con las importaciones existentes
 */

// Types
export type { Project, User } from './types';

// Auth
export { login, register, logout, getCurrentUser } from './auth';

// Projects
export {
  getProjects,
  createProject,
  getProject,
  deleteProject,
  updateProjectStatus,
} from './projects';

// Containers
export {
  getContainerStatus,
  startContainer,
  stopContainer,
} from './containers';

// Storage (por si se necesita acceso directo)
export { STORAGE_KEYS } from './storage';
