import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  User,
  login as apiLogin,
  register as apiRegister,
  registerOnly as apiRegisterOnly,
  logout as apiLogout,
  getCurrentUser,
  getCachedUser,
  isAuthenticated,
} from './api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  registerOnly: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Validar sesión al montar
  useEffect(() => {
    const initAuth = async () => {
      // Primero intentar con cache (inmediato, sin loading)
      const cachedUser = getCachedUser();
      if (cachedUser) {
        setUser(cachedUser);
      }

      // Luego validar con el backend
      if (isAuthenticated()) {
        try {
          const currentUser = await getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          // Si falla, limpiar usuario
          setUser(null);
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  // Escuchar evento de unauthorized para auto-logout
  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null);
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, []);

  const login = async (email: string, password: string) => {
    const loggedInUser = await apiLogin(email, password);
    setUser(loggedInUser);
  };

  const register = async (email: string, password: string, name: string) => {
    const registeredUser = await apiRegister(email, password, name);
    setUser(registeredUser);
  };

  // Registrar sin autenticar automáticamente
  const registerOnly = async (email: string, password: string, name: string) => {
    await apiRegisterOnly(email, password, name);
    // No setear el usuario - mantener sesión no autenticada
  };

  const logout = async () => {
    await apiLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        registerOnly,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
