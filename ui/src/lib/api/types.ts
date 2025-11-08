/**
 * API Types - Interfaces y tipos compartidos
 */

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
