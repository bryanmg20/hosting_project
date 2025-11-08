/**
 * Storage - Gestión de datos en localStorage
 */

import { Project, User } from './types';

export const STORAGE_KEYS = {
  USER: 'hosting_user',
  PROJECTS: 'hosting_projects',
} as const;

// Mock Projects Data - Estado inicial
export const initialProjects: Project[] = [
  {
    id: '1',
    name: 'mi-portafolio',
    status: 'running',
    url: 'http://miportafolio.juan.localhost',
    template: 'react',
    github_url: 'https://github.com/juan/mi-portafolio',
    created_at: '2025-11-01T10:30:00Z',
    metrics: {
      cpu: 45,
      memory: 512,
      requests: 1250,
    },
  },
  {
    id: '2',
    name: 'landing-page',
    status: 'running',
    url: 'http://landing.juan.localhost',
    template: 'static',
    github_url: 'https://github.com/juan/landing-page',
    created_at: '2025-10-28T14:20:00Z',
    metrics: {
      cpu: 12,
      memory: 128,
      requests: 450,
    },
  },
  {
    id: '3',
    name: 'api-backend',
    status: 'stopped',
    url: 'http://api.juan.localhost',
    template: 'nodejs',
    github_url: 'https://github.com/juan/api-backend',
    created_at: '2025-10-25T09:15:00Z',
    metrics: {
      cpu: 0,
      memory: 0,
      requests: 0,
    },
  },
];

// Mock User Data - Estado en memoria
let currentUser: User | null = null;

// Inicializar datos desde localStorage
export const initializeData = () => {
  const storedUser = localStorage.getItem(STORAGE_KEYS.USER);
  const storedProjects = localStorage.getItem(STORAGE_KEYS.PROJECTS);

  if (storedUser) {
    currentUser = JSON.parse(storedUser);
  }

  if (!storedProjects) {
    localStorage.setItem(STORAGE_KEYS.PROJECTS, JSON.stringify(initialProjects));
  }
};

// Gestión de usuario actual
export const setCurrentUser = (user: User | null) => {
  currentUser = user;
  if (user) {
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  } else {
    localStorage.removeItem(STORAGE_KEYS.USER);
  }
};

export const getCurrentUserData = (): User | null => {
  if (!currentUser) {
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER);
    if (storedUser) {
      currentUser = JSON.parse(storedUser);
    }
  }
  return currentUser;
};

// Gestión de proyectos en storage
export const getStoredProjects = (): Project[] => {
  const storedProjects = localStorage.getItem(STORAGE_KEYS.PROJECTS);
  if (storedProjects) {
    return JSON.parse(storedProjects);
  }
  return initialProjects;
};

export const setStoredProjects = (projects: Project[]): void => {
  localStorage.setItem(STORAGE_KEYS.PROJECTS, JSON.stringify(projects));
};

// Helper para simular delay de red
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Inicializar datos al cargar el módulo
if (typeof window !== 'undefined') {
  initializeData();
}
