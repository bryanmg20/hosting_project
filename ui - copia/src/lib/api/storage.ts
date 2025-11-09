/**
 * Storage - Gestión de tokens y preferencias locales
 */

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token', 
  USER_DATA: 'user_data', // Cache opcional para UI
  THEME: 'theme',
} as const;

// ========================================
// Token Management
// ========================================

export const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
};

export const setAuthToken = (token: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
};

export const getRefreshToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
};

export const setRefreshToken = (token: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, token);
};

export const clearAuthTokens = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
  localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  localStorage.removeItem(STORAGE_KEYS.USER_DATA);
};

// ========================================
// User Data Cache (opcional, solo para UI)
// ========================================

export const getCachedUserData = (): any | null => {
  if (typeof window === 'undefined') return null;
  const data = localStorage.getItem(STORAGE_KEYS.USER_DATA);
  return data ? JSON.parse(data) : null;
};

export const setCachedUserData = (userData: any): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
};

// ========================================
// Theme Management
// ========================================

export const getStoredTheme = (): 'light' | 'dark' | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(STORAGE_KEYS.THEME) as 'light' | 'dark' | null;
};

export const setStoredTheme = (theme: 'light' | 'dark'): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEYS.THEME, theme);
};

// ========================================
// Helpers
// ========================================

export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};

// Helper para simular delay de red (útil para testing)
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
