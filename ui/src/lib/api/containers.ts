/**
 * Containers API - Endpoints de gestión de contenedores
 * 
 * Endpoints:
 * - GET /api/containers/:id/status
 * - POST /api/containers/:id/start
 * - POST /api/containers/:id/stop
 * - POST /api/containers/:id/restart
 * - GET /api/containers/events (SSE - implementado en sse-context.tsx)
 */

import { apiClient } from './api-client';
import type { Project, ContainerStatusResponse } from './types';

// ========================================
// GET /api/containers/:id/status
// ========================================
export const getContainerStatus = async (
  id: string
): Promise<Project['status']> => {
  const response = await apiClient.get<ContainerStatusResponse>(
    `/containers/${id}/status`,
    { requiresAuth: true }
  );
  
  return response.status;
};

// ========================================
// POST /api/containers/:id/start
// ========================================
export const startContainer = async (id: string): Promise<void> => {
  await apiClient.post(
    `/containers/${id}/start`,
    {},
    { requiresAuth: true }
  );
};

// ========================================
// POST /api/containers/:id/stop
// ========================================
export const stopContainer = async (id: string): Promise<void> => {
  await apiClient.post(
    `/containers/${id}/stop`,
    {},
    { requiresAuth: true }
  );
};

// ========================================
// POST /api/containers/:id/restart
// ========================================
export const restartContainer = async (id: string): Promise<void> => {
  await apiClient.post(
    `/containers/${id}/restart`,
    {},
    { requiresAuth: true }
  );
};

// ========================================
// POST /api/containers/:id/rebuild
// ========================================
export const rebuildContainer = async (id: string): Promise<void> => {
  await apiClient.post(
    `/containers/${id}/rebuild`,
    {},
    { requiresAuth: true }
  );
};

// ========================================
// POST /api/containers/:id/create
// ========================================
export const createContainer = async (id: string): Promise<void> => {
  await apiClient.post(
    `/containers/${id}/create`,
    {},
    { requiresAuth: true }
  );
};
