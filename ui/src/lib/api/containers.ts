/**
 * Containers API - Endpoints de gestión de contenedores
 * 
 * Endpoints:
 * - GET /api/containers/:id/status
 * - POST /api/containers/:id/start
 * - POST /api/containers/:id/stop
 * - GET /api/containers/events (SSE - implementado en sse-context.tsx)
 */

import { Project } from './types';
import { delay } from './storage';
import { getProject, updateProjectStatus } from './projects';

// ========================================
// GET /api/containers/:id/status
// ========================================
export const getContainerStatus = async (
  id: string
): Promise<Project['status']> => {
  await delay(400);

  const project = await getProject(id);
  return project?.status || 'stopped';
};

// ========================================
// POST /api/containers/:id/start
// ========================================
export const startContainer = async (id: string): Promise<void> => {
  await delay(1500);
  updateProjectStatus(id, 'running');
};

// ========================================
// POST /api/containers/:id/stop
// ========================================
export const stopContainer = async (id: string): Promise<void> => {
  await delay(1200);
  updateProjectStatus(id, 'stopped');
};
