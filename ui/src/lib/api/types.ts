/**
 * API Types - Interfaces y tipos compartidos
 */

// ========================================
// Domain Models
// ========================================

export interface Project {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'deploying' | 'error';
  url: string;
  template: 'static' | 'react' | 'flask' | 'nodejs';
  github_url: string;
  created_at: string;
  metrics: {
    cpu: number;
    memory: number;
    requests: number;
  };
}

export interface User {
  id: string;
  email: string;
  name: string;
}

// ========================================
// API Request/Response Types
// ========================================

// Auth Endpoints
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
  refresh_token?: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface RegisterResponse {
  user: User;
  token: string;
  refresh_token?: string;
}

export interface MeResponse {
  user: User;
}

// Project Endpoints
export interface CreateProjectRequest {
  name: string;
  github_url: string;
  template: Project['template'];
}

export interface CreateProjectResponse {
  project: Project;
}

export interface GetProjectsResponse {
  projects: Project[];
}

export interface GetProjectResponse {
  project: Project;
}

// Container Endpoints
export interface ContainerStatusResponse {
  status: Project['status'];
}

// Generic API Error
export interface ApiError {
  error: string;
  message: string;
  statusCode: number;
}

// ========================================
// API Configuration
// ========================================

export interface ApiConfig {
  baseUrl: string;
  timeout?: number;
  enableMock?: boolean; // Para testing
}
