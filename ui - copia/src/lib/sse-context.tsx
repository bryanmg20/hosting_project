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
 * - Container status tracking (running, stopped, deploying, inactive, error)
 * - Toast notifications for status changes
 * 
 * SSE EVENTS:
 * - container_status_changed: Cuando cambia estado running/stopped
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
import { toast } from 'sonner';
import { getAuthToken } from './api';

export type ContainerStatus = 'running' | 'stopped' | 'deploying' | 'inactive' | 'error';

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

  // Conectar a SSE
  const connectSSE = useCallback(() => {
    const token = getAuthToken();
    if (!token) {
      setSseStatus('disconnected');
      return () => {};
    }

    setSseStatus('connecting');

    const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';
    const eventSource = new EventSource(`${apiBaseUrl}/containers/events?token=${token}`);
    
    eventSource.onopen = () => {
      setSseStatus('connected');
      toast.success('Conexión SSE establecida', {
        description: 'Actualizaciones automáticas activadas',
      });
    };

    eventSource.addEventListener('metrics_updated', (event) => {
      const data = JSON.parse(event.data);
      setContainerMetrics(prev => ({ ...prev, [data.projectId]: data.metrics }));
    });

    eventSource.addEventListener('container_status_changed', (event) => {
      const data = JSON.parse(event.data);
      setContainerStatus(prev => ({ ...prev, [data.projectId]: data.status }));
    });

    eventSource.addEventListener('auto_shutdown', (event) => {
      const data = JSON.parse(event.data);
      setContainerStatus(prev => ({ ...prev, [data.projectId]: 'inactive' }));
      toast.warning('Auto-shutdown activado', {
        description: `El contenedor ${data.projectId} ha sido pausado por inactividad`,
      });
    });

    eventSource.addEventListener('container_error', (event) => {
      const data = JSON.parse(event.data);
      setContainerStatus(prev => ({ ...prev, [data.projectId]: 'error' }));
      toast.error('Error en contenedor', {
        description: data.message || `Contenedor ${data.projectId}`,
      });
    });

    eventSource.addEventListener('connected', (event) => {
      const data = JSON.parse(event.data);
      console.log('SSE connected:', data.message);
    });

  // En connectSSE, modifica el onerror:
eventSource.onerror = (error) => {
  console.error('❌ SSE Error:', error);
  
  // Si es error de autenticación, reconectar después de 1 segundo
  if (eventSource.readyState === EventSource.CLOSED) {
    setTimeout(() => {
      const token = getAuthToken();
      if (token) {
        connectSSE(); // Reconectar si hay token
      }
    }, 1000);
  }
  
  setSseStatus('disconnected');
  eventSource.close();
};

    eventSourceRef.current = eventSource;

    return () => {
      eventSource.close();
    };
  }, []);

  // Reconexión automática
  const handleReconnect = useCallback(() => {
    if (sseStatus === 'disconnected') {
      reconnectTimeoutRef.current = setTimeout(() => {
        connectSSE();
      }, 3000);
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

  const updateContainerStatus = useCallback((projectId: string, status: ContainerStatus) => {
    setContainerStatus((prev) => ({ ...prev, [projectId]: status }));
    
    if (status === 'running') {
      setContainerMetrics((prev) => ({
        ...prev,
        [projectId]: {
          cpu: 10 + Math.random() * 20,
          memory: 100 + Math.random() * 100,
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