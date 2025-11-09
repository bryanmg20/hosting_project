/**
 * API Client - Cliente HTTP centralizado con autenticación
 */

import { getAuthToken, clearAuthTokens } from './storage';
import type { ApiError } from './types';

// ========================================
// Configuration
// ========================================

const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) 
  ? import.meta.env.VITE_API_URL 
  : 'http://localhost:3000/api';
const DEFAULT_TIMEOUT = 30000; // 30 segundos

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
      await handleErrorResponse(response);
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
// Error Response Handler
// ========================================

async function handleErrorResponse(response: Response): Promise<never> {
  let errorData: ApiError;

  try {
    errorData = await response.json();
  } catch {
    // Si no puede parsear JSON, crear error genérico
    errorData = {
      error: 'Error',
      message: response.statusText || 'Unknown error',
      statusCode: response.status,
    };
  }

  // 401 - Token inválido/expirado - Auto logout
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
