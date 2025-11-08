/**
 * SSE Context - Real-time Container Monitoring via Server-Sent Events
 * 
 * SSE CONNECTION (Mock Implementation):
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
 */

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { toast } from 'sonner@2.0.3';

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

  // Simular conexión SSE
  const connectSSE = useCallback(() => {
    setSseStatus('connecting');
    
    // Simular proceso de conexión
    const connectTimeout = setTimeout(() => {
      setSseStatus('connected');
      toast.success('Conexión SSE establecida', {
        description: 'Actualizaciones automáticas activadas',
      });

      // Simular EventSource (en producción sería: new EventSource('/api/containers/events'))
      // Como es mock, usamos intervalos para simular eventos SSE
    }, 1500);

    return () => clearTimeout(connectTimeout);
  }, []);

  // Reconexión automática
  const handleReconnect = useCallback(() => {
    if (sseStatus === 'disconnected') {
      console.log('Intentando reconectar SSE...');
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

  // Simular evento SSE: metrics_updated
  useEffect(() => {
    if (sseStatus !== 'connected') return;

    const metricsInterval = setInterval(() => {
      setContainerMetrics((prev) => {
        const updated = { ...prev };
        Object.keys(containerStatus).forEach((projectId) => {
          if (containerStatus[projectId] === 'running') {
            const currentMetrics = prev[projectId] || {
              cpu: 0,
              memory: 0,
              requests: 0,
              uptime: '0s',
              lastActivity: new Date().toISOString(),
            };

            updated[projectId] = {
              cpu: Math.min(100, Math.max(0, currentMetrics.cpu + (Math.random() - 0.5) * 10)),
              memory: Math.min(512, Math.max(50, currentMetrics.memory + (Math.random() - 0.5) * 20)),
              requests: currentMetrics.requests + Math.floor(Math.random() * 5),
              uptime: currentMetrics.uptime,
              lastActivity: new Date().toISOString(),
            };
          }
        });
        return updated;
      });
    }, 4000); // Backend envía métricas cada 4 segundos

    return () => clearInterval(metricsInterval);
  }, [sseStatus, containerStatus]);

  // Simular evento SSE: auto_shutdown
  useEffect(() => {
    if (sseStatus !== 'connected') return;

    const autoShutdownInterval = setInterval(() => {
      Object.keys(containerStatus).forEach((projectId) => {
        // 1% de probabilidad de auto-shutdown por check
        if (Math.random() < 0.01) {
          const currentStatus = containerStatus[projectId];
          if (currentStatus === 'running' && Math.random() < 0.3) {
            // Simular evento auto_shutdown
            setContainerStatus((prev) => ({ ...prev, [projectId]: 'inactive' }));
            toast.warning('Auto-shutdown activado', {
              description: `El contenedor ha sido pausado por inactividad`,
            });
          }
        }
      });
    }, 30000); // Cada 30 segundos

    return () => clearInterval(autoShutdownInterval);
  }, [sseStatus, containerStatus]);

  const updateContainerStatus = useCallback((projectId: string, status: ContainerStatus) => {
    setContainerStatus((prev) => ({ ...prev, [projectId]: status }));
    
    // Si cambia a running, crear métricas iniciales
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

  // Inicializar métricas para proyectos existentes
  useEffect(() => {
    const projects = ['proj-1', 'proj-2', 'proj-3'];
    const initialMetrics: Record<string, ContainerMetrics> = {};
    const initialStatus: Record<string, ContainerStatus> = {};

    projects.forEach((id, index) => {
      const statuses: ContainerStatus[] = ['running', 'stopped', 'deploying'];
      const status = statuses[index % statuses.length];
      
      initialStatus[id] = status;
      
      if (status === 'running') {
        initialMetrics[id] = {
          cpu: 30 + Math.random() * 40,
          memory: 150 + Math.random() * 200,
          requests: Math.floor(Math.random() * 1000),
          uptime: `${Math.floor(Math.random() * 24)}h ${Math.floor(Math.random() * 60)}m`,
          lastActivity: new Date().toISOString(),
        };
      }
    });

    setContainerMetrics(initialMetrics);
    setContainerStatus(initialStatus);
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
