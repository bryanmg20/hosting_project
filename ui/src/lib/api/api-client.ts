/**
 * API Client - Cliente HTTP centralizado con autenticación y auto-refresh
 */

import { getAuthToken, getRefreshToken, setAuthToken, setRefreshToken, clearAuthTokens } from './storage';
import type { ApiError, RefreshTokenResponse } from './types';

// ========================================
// Configuration
// ========================================

const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) 
  ? import.meta.env.VITE_API_URL 
  : 'http://localhost:3000/api';
const DEFAULT_TIMEOUT = 30000; // 30 segundos

// ========================================
// Refresh Token State
// ========================================

let isRefreshing = false;
let refreshQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

// ========================================
// Custom Error Class
// ========================================

export class ApiClientError extends Error {
  statusCode: number;
  response?: any;

  constructor(message: string, statusCode: number, response?: any) {
    super(message);
    this.name = 'ApiClientError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

// ========================================
// Request Options
// ========================================

interface RequestOptions extends RequestInit {
  timeout?: number;
  requiresAuth?: boolean;
  _isRetry?: boolean; // Flag interno para evitar loops infinitos
}

// ========================================
// Refresh Token Function
// ========================================

async function performRefreshToken(): Promise<string> {
  // Si ya hay un refresh en progreso, encolar este request
  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      refreshQueue.push({ resolve, reject });
    });
  }

  isRefreshing = true;

  const currentRefreshToken = getRefreshToken();
  if (!currentRefreshToken) {
    isRefreshing = false;
    clearAuthTokens();
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    throw new ApiClientError('No refresh token found', 401);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentRefreshToken}`,
      },
    });

    if (!response.ok) {
      // El refresh token expiró o es inválido
      let errorData: ApiError;
      try {
        errorData = await response.json();
      } catch {
        errorData = {
          error: 'Refresh failed',
          message: 'Failed to refresh authentication',
          statusCode: response.status,
        };
      }

      isRefreshing = false;
      clearAuthTokens();
      window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      
      const error = new ApiClientError(
        errorData.message || 'Refresh token expired',
        response.status,
        errorData
      );

      // Rechazar todos los requests encolados
      refreshQueue.forEach(({ reject }) => reject(error));
      refreshQueue = [];

      throw error;
    }

    const refreshResponse: RefreshTokenResponse = await response.json();
    
    // Guardar nuevos tokens (el backend devuelve "access_token" no "token")
    setAuthToken(refreshResponse.access_token);
    if (refreshResponse.refresh_token) {
      setRefreshToken(refreshResponse.refresh_token);
    }

    isRefreshing = false;

    // Resolver todos los requests encolados con el nuevo token
    refreshQueue.forEach(({ resolve }) => resolve(refreshResponse.access_token));
    refreshQueue = [];

    return refreshResponse.access_token;
  } catch (error: any) {
    isRefreshing = false;
    clearAuthTokens();
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));

    // Rechazar todos los requests encolados
    refreshQueue.forEach(({ reject }) => reject(error));
    refreshQueue = [];

    throw error;
  }
}

// ========================================
// Core API Client Function
// ========================================

async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    timeout = DEFAULT_TIMEOUT,
    requiresAuth = true,
    _isRetry = false,
    headers = {},
    ...fetchOptions
  } = options;

  // Construir URL completa
  const url = `${API_BASE_URL}${endpoint}`;

  // Headers base
  const requestHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...headers,
  };

  // Agregar Authorization header si se requiere autenticación
  if (requiresAuth) {
    const token = getAuthToken();
    if (!token) {
      throw new ApiClientError('No authentication token found', 401);
    }
    requestHeaders['Authorization'] = `Bearer ${token}`;
  }

  // Configurar timeout con AbortController
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers: requestHeaders,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Manejo de respuestas no-OK
    if (!response.ok) {
      // Parsear error
      let errorData: ApiError;
      try {
        errorData = await response.json();
      } catch {
        errorData = {
          error: 'Error',
          message: response.statusText || 'Unknown error',
          statusCode: response.status,
        };
      }

      // Caso especial: 401 Unauthorized
      if (response.status === 401 && requiresAuth && !_isRetry) {
        // No intentar refresh si estamos en el endpoint de refresh
        if (endpoint === '/auth/refresh') {
          clearAuthTokens();
          window.dispatchEvent(new CustomEvent('auth:unauthorized'));
          throw new ApiClientError(
            'Refresh token expired - please login again',
            401,
            errorData
          );
        }

        // Intentar refresh y retry automático
        try {
          const newToken = await performRefreshToken();
          
          // Retry el request original con el nuevo token
          return await apiRequest<T>(endpoint, {
            ...options,
            _isRetry: true, // Marcar como retry para evitar loops infinitos
            headers: {
              ...headers,
            },
          });
        } catch (refreshError) {
          // El refresh falló, propagar el error
          throw refreshError;
        }
      }

      // Para otros errores, lanzar directamente
      if (response.status === 401) {
        clearAuthTokens();
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      }

      throw new ApiClientError(
        errorData.message || errorData.error,
        response.status,
        errorData
      );
    }

    // Parsear respuesta JSON
    const data = await response.json();
    return data as T;
  } catch (error: any) {
    clearTimeout(timeoutId);

    // Timeout error
    if (error.name === 'AbortError') {
      throw new ApiClientError('Request timeout', 408);
    }

    // Network error
    if (error instanceof TypeError) {
      throw new ApiClientError('Network error - Cannot reach server', 0);
    }

    // Re-throw si ya es ApiClientError
    if (error instanceof ApiClientError) {
      throw error;
    }

    // Error desconocido
    throw new ApiClientError(error.message || 'Unknown error', 500);
  }
}

// ========================================
// HTTP Method Helpers
// ========================================

export const apiClient = {
  get: function <T>(endpoint: string, options?: RequestOptions) {
    return apiRequest<T>(endpoint, { ...options, method: 'GET' });
  },

  post: function <T>(endpoint: string, data?: any, options?: RequestOptions) {
    return apiRequest<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  put: function <T>(endpoint: string, data?: any, options?: RequestOptions) {
    return apiRequest<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  patch: function <T>(endpoint: string, data?: any, options?: RequestOptions) {
    return apiRequest<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  delete: function <T>(endpoint: string, options?: RequestOptions) {
    return apiRequest<T>(endpoint, { ...options, method: 'DELETE' });
  },
};

// ========================================
// Utility Functions
// ========================================

export const getApiBaseUrl = () => API_BASE_URL;

export const isNetworkError = (error: any): boolean => {
  return error instanceof ApiClientError && error.statusCode === 0;
};

export const isUnauthorizedError = (error: any): boolean => {
  return error instanceof ApiClientError && error.statusCode === 401;
};

export const isServerError = (error: any): boolean => {
  return error instanceof ApiClientError && error.statusCode >= 500;
};