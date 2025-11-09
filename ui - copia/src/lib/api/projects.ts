/**
 * Projects API - Endpoints de gestión de proyectos
 * 
 * Endpoints:
 * - GET /api/projects
 * - POST /api/projects
 * - GET /api/projects/:id
 * - DELETE /api/projects/:id
 */

import { apiClient } from './api-client';
import type {
  Project,
  CreateProjectRequest,
  CreateProjectResponse,
  GetProjectsResponse,
  GetProjectResponse,
} from './types';

// ========================================
// GET /api/projects
// ========================================
export const getProjects = async (): Promise<Project[]> => {
  const response = await apiClient.get<GetProjectsResponse>(
    '/projects',
    { requiresAuth: true }
  );
  
  return response.projects;
};

// ========================================
// POST /api/projects
// ========================================
export const createProject = async (
  name: string,
  githubUrl: string,
  template: Project['template']
): Promise<Project> => {
  const requestData: CreateProjectRequest = {
    name,
    github_url: githubUrl,
    template,
  };

  const response = await apiClient.post<CreateProjectResponse>(
    '/projects',
    requestData,
    { requiresAuth: true }
  );

  return response.project;
};

// ========================================
// GET /api/projects/:id
// ========================================
export const getProject = async (id: string): Promise<Project | null> => {
  try {
    const response = await apiClient.get<GetProjectResponse>(
      `/projects/${id}`,
      { requiresAuth: true }
    );
    
    return response.project;
  } catch (error: any) {
    // Si es 404, retornar null
    if (error.statusCode === 404) {
      return null;
    }
    throw error;
  }
};

// ========================================
// DELETE /api/projects/:id
// ========================================
export const deleteProject = async (id: string): Promise<void> => {
  await apiClient.delete(
    `/projects/${id}`,
    { requiresAuth: true }
  );
};

// ========================================
// PATCH /api/projects/:id/status
// Helper para actualizar el estado de un proyecto
// ========================================
export const updateProjectStatus = async (
  id: string,
  status: Project['status']
): Promise<Project> => {
  const response = await apiClient.patch<GetProjectResponse>(
    `/projects/${id}/status`,
    { status },
    { requiresAuth: true }
  );
  
  return response.project;
};
