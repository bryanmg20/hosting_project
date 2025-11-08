/**
 * Projects API - Endpoints de gestión de proyectos
 * 
 * Endpoints:
 * - GET /api/projects
 * - POST /api/projects
 * - GET /api/projects/:id
 * - DELETE /api/projects/:id
 */

import { Project } from './types';
import { getStoredProjects, setStoredProjects, getCurrentUserData, delay } from './storage';

// ========================================
// GET /api/projects
// ========================================
export const getProjects = async (): Promise<Project[]> => {
  await delay(800);
  return getStoredProjects();
};

// ========================================
// POST /api/projects
// ========================================
export const createProject = async (
  name: string,
  githubUrl: string,
  template: Project['template']
): Promise<Project> => {
  await delay(2000); // Deploy toma tiempo

  const newProject: Project = {
    id: Date.now().toString(),
    name,
    status: 'deploying',
    url: `http://${name}.${getCurrentUserData()?.name || 'user'}.localhost`,
    template,
    github_url: githubUrl,
    created_at: new Date().toISOString(),
    metrics: {
      cpu: 0,
      memory: 0,
      requests: 0,
    },
  };

  const projects = getStoredProjects();
  const updatedProjects = [...projects, newProject];
  setStoredProjects(updatedProjects);

  // Simular que después de unos segundos el deploy termina
  setTimeout(() => {
    updateProjectStatus(newProject.id, 'running');
  }, 3000);

  return newProject;
};

// ========================================
// GET /api/projects/:id
// ========================================
export const getProject = async (id: string): Promise<Project | null> => {
  await delay(500);

  const projects = getStoredProjects();
  return projects.find(p => p.id === id) || null;
};

// ========================================
// DELETE /api/projects/:id
// ========================================
export const deleteProject = async (id: string): Promise<void> => {
  await delay(1000);

  const projects = getStoredProjects();
  const updatedProjects = projects.filter(p => p.id !== id);
  setStoredProjects(updatedProjects);
};

// ========================================
// Helper para actualizar el estado de un proyecto
// ========================================
export const updateProjectStatus = (
  id: string,
  status: Project['status']
): void => {
  const projects = getStoredProjects();
  const updatedProjects = projects.map(p =>
    p.id === id ? { ...p, status } : p
  );
  setStoredProjects(updatedProjects);
};
