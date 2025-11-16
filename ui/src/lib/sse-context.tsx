/**
 * SSE Context - Real-time Container Monitoring via Server-Sent Events
 * 
 * SSE CONNECTION:
 * - GET /api/containers/events → Stream de eventos de estado
 * 
 * FEATURES:
 * - Conexión SSE permanente al backend
 * - Reconexión automática si se pierde la conexión
 * - Frecuencia de updates manejada internamente por el backend
 * - Connection status indicator (connecting, connected, disconnected)
 * - Container status tracking (running, exited, deploying, inactive, error)
 * - Toast notifications for status changes
 * 
 * SSE EVENTS:
 * - container_status_changed: Cuando cambia estado running/exited
 * - metrics_updated: Métricas cada X tiempo definido internamente
 * - auto_shutdown: Cuando se apaga por inactividad
 * 
 * ESTADOS DE CONEXIÓN:
 * - connecting: 🔵 Conectando...
 * - connected: ✅ Conectado (actualizaciones automáticas)
 * - disconnected: 🔴 Desconectado
 * 
 * BACKEND IMPLEMENTATION:
 * El backend debe implementar SSE endpoint que incluya Authorization header:
 * - Aceptar token via query param: /api/containers/events?token={jwt}
 * - O usar EventSource polyfill que soporte headers
 */

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { toast } from 'sonner@2.0.3';
import { getAuthToken } from './api';

export type ContainerStatus = 'running' | 'exited' | 'deploying' | 'inactive' | 'error' | 'unknown';

export interface ContainerMetrics {
  cpu: number;
  memory: number;
  requests: number;
  uptime: string;
  lastActivity: string;
}

export type SSEStatus = 'connecting' | 'connected' | 'disconnected';

interface SSEContextType {
  sseStatus: SSEStatus;
  containerStatus: Record<string, ContainerStatus>;
  containerMetrics: Record<string, ContainerMetrics>;
  updateContainerStatus: (projectId: string, status: ContainerStatus) => void;
}

const SSEContext = createContext<SSEContextType | undefined>(undefined);

export const useSSE = () => {
  const context = useContext(SSEContext);
  if (!context) {
    throw new Error('useSSE must be used within SSEProvider');
  }
  return context;
};

export const SSEProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sseStatus, setSseStatus] = useState<SSEStatus>('disconnected');
  const [containerStatus, setContainerStatus] = useState<Record<string, ContainerStatus>>({});
  const [containerMetrics, setContainerMetrics] = useState<Record<string, ContainerMetrics>>({});
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const eventSourceRef = useRef<EventSource | null>(null);
  const isInitialSyncRef = useRef<boolean>(true); // Flag para suprimir notificaciones iniciales

  // Conectar a SSE
  const connectSSE = useCallback(() => {
    // Obtener token de autenticación
    const token = getAuthToken();
    if (!token) {
      // Usuario no autenticado, no conectar SSE
      setSseStatus('disconnected');
      return () => {};
    }

    setSseStatus('connecting');

    // IMPLEMENTACIÓN REAL: Conexión SSE con backend
    const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';
    const eventSource = new EventSource(`${apiBaseUrl}/containers/events?token=${token}`);
    
    eventSource.onopen = () => {
      setSseStatus('connected');
      toast.success('Conexión SSE establecida', {
        description: 'Actualizaciones automáticas activadas',
      });
      
      // Marcar como sync inicial para suprimir notificaciones de contenedores
      isInitialSyncRef.current = true;
      
      // Después de 2 segundos, permitir notificaciones normales
      setTimeout(() => {
        isInitialSyncRef.current = false;
      }, 2000);
    };

    // Evento: Métricas actualizadas (CPU, memoria, requests)
    eventSource.addEventListener('metrics_updated', (event) => {
      const data = JSON.parse(event.data);
      setContainerMetrics(prev => ({ ...prev, [data.projectId]: data.metrics }));
    });

    // Evento: Estado del contenedor cambió (running, exited, deploying, etc.)
    eventSource.addEventListener('container_status_changed', (event) => {
      const data = JSON.parse(event.data);
      setContainerStatus(prev => ({ ...prev, [data.projectId]: data.status }));
      
      // Opcional: Notificar al usuario del cambio
      // Suprimir notificaciones durante sincronización inicial (primeros 2s)
      if (data.notify !== false && !isInitialSyncRef.current) {
        const statusLabels = {
          running: 'iniciado',
          exited: 'detenido',
          deploying: 'desplegando',
          error: 'con error',
          inactive: 'inactivo',
          unknown: 'desconocido',
        };
        toast.info(`Contenedor ${statusLabels[data.status as ContainerStatus] || data.status}`);
      }
    });

    // Evento: Auto-shutdown por inactividad
    eventSource.addEventListener('auto_shutdown', (event) => {
      const data = JSON.parse(event.data);
      setContainerStatus(prev => ({ ...prev, [data.projectId]: 'inactive' }));
      toast.warning('Auto-shutdown activado', {
        description: `El contenedor ${data.projectName || ''} ha sido pausado por inactividad`,
      });
    });

    eventSource.onerror = () => {
      setSseStatus('disconnected');
      eventSource.close();
      toast.error('Conexión SSE perdida', {
        description: 'Reintentando conexión...',
      });
    };

    eventSourceRef.current = eventSource;

    return () => {
      eventSource.close();
    };
  }, []);

  // Reconexión automática
  const handleReconnect = useCallback(() => {
    // Solo reconectar si hay token de autenticación
    const token = getAuthToken();
    if (sseStatus === 'disconnected' && token) {
      reconnectTimeoutRef.current = setTimeout(() => {
        connectSSE();
      }, 3000); // Reintentar después de 3 segundos
    }
  }, [sseStatus, connectSSE]);

  // Inicializar conexión SSE
  useEffect(() => {
    const cleanup = connectSSE();
    return cleanup;
  }, [connectSSE]);

  // Manejar reconexión automática
  useEffect(() => {
    if (sseStatus === 'disconnected') {
      handleReconnect();
    }
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [sseStatus, handleReconnect]);

  // Escuchar eventos de logout/login/project para manejar conexión SSE
  useEffect(() => {
    const handleLogout = () => {
      // Cerrar conexión SSE existente
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      
      // Limpiar timeout de reconexión
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = undefined;
      }
      
      // Actualizar estados
      setSseStatus('disconnected');
      setContainerStatus({});
      setContainerMetrics({});
      
      // Resetear flag de sync inicial para próximo login
      isInitialSyncRef.current = true;
      
      console.log('SSE desconectado por logout');
    };

    const handleUnauthorized = () => {
      // Similar al logout, cerrar conexión SSE cuando se detecta unauthorized
      handleLogout();
    };

    const handleLogin = () => {
      // Cuando el usuario hace login, conectar SSE inmediatamente
      console.log('Login detectado, conectando SSE...');
      connectSSE();
    };

    const handleProjectCreated = () => {
      // Cuando se crea un proyecto, reconectar SSE para que el backend cargue la lista actualizada
      console.log('Proyecto creado, reconectando SSE...');
      
      // Cerrar conexión existente
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      
      // Reconectar inmediatamente
      connectSSE();
    };

    const handleProjectDeleted = () => {
      // Cuando se elimina un proyecto, reconectar SSE para que el backend actualice la lista
      console.log('Proyecto eliminado, reconectando SSE...');
      
      // Cerrar conexión existente
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      
      // Reconectar inmediatamente
      connectSSE();
    };

    window.addEventListener('auth:logout', handleLogout);
    window.addEventListener('auth:unauthorized', handleUnauthorized);
    window.addEventListener('auth:login', handleLogin);
    window.addEventListener('project:created', handleProjectCreated);
    window.addEventListener('project:deleted', handleProjectDeleted);
    
    return () => {
      window.removeEventListener('auth:logout', handleLogout);
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
      window.removeEventListener('auth:login', handleLogin);
      window.removeEventListener('project:created', handleProjectCreated);
      window.removeEventListener('project:deleted', handleProjectDeleted);
    };
  }, [connectSSE]);

  // OPCIONAL: Simular eventos SSE para testing sin backend
  // Descomentar estos efectos solo si necesitas testing local sin backend
  
  // useEffect(() => {
  //   if (sseStatus !== 'connected') return;
  //
  //   const metricsInterval = setInterval(() => {
  //     setContainerMetrics((prev) => {
  //       const updated = { ...prev };
  //       Object.keys(containerStatus).forEach((projectId) => {
  //         if (containerStatus[projectId] === 'running') {
  //           const currentMetrics = prev[projectId] || {
  //             cpu: 0,
  //             memory: 0,
  //             requests: 0,
  //             uptime: '0s',
  //             lastActivity: new Date().toISOString(),
  //           };
  //
  //           updated[projectId] = {
  //             cpu: Math.min(100, Math.max(0, currentMetrics.cpu + (Math.random() - 0.5) * 10)),
  //             memory: Math.min(512, Math.max(50, currentMetrics.memory + (Math.random() - 0.5) * 20)),
  //             requests: currentMetrics.requests + Math.floor(Math.random() * 5),
  //             uptime: currentMetrics.uptime,
  //             lastActivity: new Date().toISOString(),
  //           };
  //         }
  //       });
  //       return updated;
  //     });
  //   }, 4000);
  //
  //   return () => clearInterval(metricsInterval);
  // }, [sseStatus, containerStatus]);

  // Actualizar manualmente el estado de un contenedor (usado por componentes)
  const updateContainerStatus = useCallback((projectId: string, status: ContainerStatus) => {
    setContainerStatus((prev) => ({ ...prev, [projectId]: status }));
    
    // Si cambia a running, inicializar métricas
    if (status === 'running') {
      setContainerMetrics((prev) => ({
        ...prev,
        [projectId]: prev[projectId] || {
          cpu: 0,
          memory: 0,
          requests: 0,
          uptime: '0s',
          lastActivity: new Date().toISOString(),
        },
      }));
    }
  }, []);

  const value: SSEContextType = {
    sseStatus,
    containerStatus,
    containerMetrics,
    updateContainerStatus,
  };

  return (
    <SSEContext.Provider value={value}>
      {children}
    </SSEContext.Provider>
  );
};
