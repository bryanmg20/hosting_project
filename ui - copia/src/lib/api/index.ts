/**
 * API Index - Re-exporta todas las funciones y tipos
 * Mantiene compatibilidad con las importaciones existentes
 */

// Types
export type {
  Project,
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  MeResponse,
  CreateProjectRequest,
  CreateProjectResponse,
  GetProjectsResponse,
  GetProjectResponse,
  ContainerStatusResponse,
  ApiError,
  ApiConfig,
} from './types';

// Auth
export {
  login,
  register,
  logout,
  getCurrentUser,
  getCachedUser,
  validateSession,
} from './auth';

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
  restartContainer,
} from './containers';

// Storage helpers (por si se necesita acceso directo)
export {
  STORAGE_KEYS,
  getAuthToken,
  setAuthToken,
  clearAuthTokens,
  isAuthenticated,
  getStoredTheme,
  setStoredTheme,
} from './storage';

// API Client utilities
export {
  apiClient,
  ApiClientError,
  getApiBaseUrl,
  isNetworkError,
  isUnauthorizedError,
  isServerError,
} from './api-client';
