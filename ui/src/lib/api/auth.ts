/**
 * Auth API - Endpoints de autenticación
 * 
 * Endpoints:
 * - POST /api/auth/login
 * - POST /api/auth/register
 * - POST /api/auth/logout
 * - POST /api/auth/refresh
 * - GET /api/auth/me
 */

import { apiClient } from './api-client';
import {
  setAuthToken,
  setRefreshToken,
  clearAuthTokens,
  setCachedUserData,
  getCachedUserData,
} from './storage';
import type {
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  MeResponse,
} from './types';

// ========================================
// POST /api/auth/login
// ========================================
export const login = async (email: string, password: string): Promise<User> => {
  const requestData: LoginRequest = { email, password };

  const response = await apiClient.post<LoginResponse>(
    '/auth/login',
    requestData,
    { requiresAuth: false } // Login no requiere token
  );

  // Guardar tokens
  setAuthToken(response.token);
  if (response.refresh_token) {
    setRefreshToken(response.refresh_token);
  }

  // Guardar datos de usuario en cache (opcional)
  setCachedUserData(response.user);

  return response.user;
};

// ========================================
// POST /api/auth/register
// ========================================
export const register = async (
  email: string,
  password: string,
  name: string
): Promise<User> => {
  const requestData: RegisterRequest = { email, password, name };

  const response = await apiClient.post<RegisterResponse>(
    '/auth/register',
    requestData,
    { requiresAuth: false } // Register no requiere token
  );

  // Guardar tokens
  setAuthToken(response.token);
  if (response.refresh_token) {
    setRefreshToken(response.refresh_token);
  }

  // Guardar datos de usuario en cache
  setCachedUserData(response.user);

  return response.user;
};

// ========================================
// POST /api/auth/register (sin autenticar)
// ========================================
export const registerOnly = async (
  email: string,
  password: string,
  name: string
): Promise<void> => {
  const requestData: RegisterRequest = { email, password, name };

  await apiClient.post<RegisterResponse>(
    '/auth/register',
    requestData,
    { requiresAuth: false } // Register no requiere token
  );

  // NO guardar tokens - el usuario deberá hacer login manualmente
};

// ========================================
// POST /api/auth/logout
// ========================================
export const logout = async (): Promise<void> => {
  try {
    // Intentar notificar al backend (opcional)
    await apiClient.post('/auth/logout', {}, { requiresAuth: true });
  } catch (error) {
    // Ignorar errores de logout en backend
    console.warn('Logout request failed, clearing local session anyway');
  } finally {
    // Siempre limpiar tokens locales
    clearAuthTokens();
  }
};

// ========================================
// POST /api/auth/refresh
// ========================================
// Nota: Esta función ya no se usa directamente porque el refresh
// se maneja automáticamente en api-client.ts cuando hay un 401.
// Se mantiene solo por compatibilidad, pero NO es necesaria.
export const refreshAccessToken = async (): Promise<string> => {
  // El refresh se hace automáticamente en api-client.ts
  throw new Error('refreshAccessToken is deprecated - refresh happens automatically');
};

// ========================================
// GET /api/auth/me
// ========================================
export const getCurrentUser = async (): Promise<User | null> => {
  try {
    const response = await apiClient.get<MeResponse>(
      '/auth/me',
      { requiresAuth: true }
    );
    
    // Actualizar cache
    setCachedUserData(response.user);
    
    return response.user;
  } catch (error: any) {
    // Si falla (401, network, etc.), retornar null
    clearAuthTokens();
    return null;
  }
};

// ========================================
// Helper: Obtener usuario del cache (sync)
// ========================================
export const getCachedUser = (): User | null => {
  return getCachedUserData();
};

// ========================================
// Helper: Validar sesión actual
// ========================================
export const validateSession = async (): Promise<boolean> => {
  const user = await getCurrentUser();
  return user !== null;
};