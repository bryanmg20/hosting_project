/**
 * Auth API - Endpoints de autenticación
 * 
 * Endpoints:
 * - POST /api/auth/login
 * - POST /api/auth/register
 * - POST /api/auth/logout
 * - GET /api/auth/me
 */

import { User } from './types';
import { setCurrentUser, getCurrentUserData, delay } from './storage';

// ========================================
// POST /api/auth/login
// ========================================
export const login = async (email: string, password: string): Promise<User> => {
  await delay(1000); // Simula latencia de red

  // Validación mock
  if (!email || !password) {
    throw new Error('Email y contraseña son requeridos');
  }

  if (password.length < 6) {
    throw new Error('Contraseña incorrecta');
  }

  // Usuario mock
  const user: User = {
    id: '123',
    email,
    name: email.split('@')[0],
  };

  setCurrentUser(user);

  return user;
};

// ========================================
// POST /api/auth/register
// ========================================
export const register = async (
  email: string,
  password: string,
  name: string
): Promise<User> => {
  await delay(1200);

  if (!email || !password || !name) {
    throw new Error('Todos los campos son requeridos');
  }

  if (password.length < 6) {
    throw new Error('La contraseña debe tener al menos 6 caracteres');
  }

  const user: User = {
    id: Date.now().toString(),
    email,
    name,
  };

  setCurrentUser(user);

  return user;
};

// ========================================
// POST /api/auth/logout
// ========================================
export const logout = async (): Promise<void> => {
  await delay(300);
  setCurrentUser(null);
};

// ========================================
// GET /api/auth/me
// ========================================
export const getCurrentUser = (): User | null => {
  return getCurrentUserData();
};
