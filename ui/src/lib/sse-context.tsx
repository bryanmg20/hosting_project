/**
 * SSE Context - Real-time Container Monitoring via Server-Sent Events
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
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  // Conectar a SSE real
  const connectSSE = useCallback(() => {
    const token = getAuthToken();
    if (!token) {
      setSseStatus('disconnected');
      return;
    }

    setSseStatus('connecting');

    const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';
    
    // Conexión SSE real con token en query param
    const eventSource = new EventSource(`${apiBaseUrl}/containers/events?token=${token}`);
    
    eventSource.onopen = () => {
      setSseStatus('connected');
      toast.success('Conexión SSE establecida', {
        description: 'Actualizaciones automáticas activadas',
      });
    };

    // Evento: Cambio de estado de contenedor
    eventSource.addEventListener('container_status_changed', (event) => {
      try {
        const data = JSON.parse(event.data);
        setContainerStatus(prev => ({ 
          ...prev, 
          [data.projectId]: data.status 
        }));
        
        // Notificación de cambio de estado
        if (data.previousStatus && data.previousStatus !== data.status) {
          toast.info(`Estado actualizado: ${data.status}`, {
            description: `Contenedor ${data.projectId}`,
          });
        }
      } catch (error) {
        console.error('Error parsing container_status_changed:', error);
      }
    });

    // Evento: Métricas actualizadas
    eventSource.addEventListener('metrics_updated', (event) => {
      try {
        const data = JSON.parse(event.data);
        setContainerMetrics(prev => ({ 
          ...prev, 
          [data.projectId]: data.metrics 
        }));
      } catch (error) {
        console.error('Error parsing metrics_updated:', error);
      }
    });

    // Evento: Auto shutdown
    eventSource.addEventListener('auto_shutdown', (event) => {
      try {
        const data = JSON.parse(event.data);
        setContainerStatus(prev => ({ 
          ...prev, 
          [data.projectId]: 'inactive' 
        }));
        
        toast.warning('Auto-shutdown activado', {
          description: `Contenedor ${data.projectId} pausado por inactividad`,
        });
      } catch (error) {
        console.error('Error parsing auto_shutdown:', error);
      }
    });

    // Evento: Error del contenedor
    eventSource.addEventListener('container_error', (event) => {
      try {
        const data = JSON.parse(event.data);
        setContainerStatus(prev => ({ 
          ...prev, 
          [data.projectId]: 'error' 
        }));
        
        toast.error('Error en contenedor', {
          description: data.message || `Contenedor ${data.projectId}`,
        });
      } catch (error) {
        console.error('Error parsing container_error:', error);
      }
    });

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      setSseStatus('disconnected');
      eventSource.close();
      
      // Reconexión automática
      reconnectTimeoutRef.current = setTimeout(() => {
        connectSSE();
      }, 5000);
    };

    eventSourceRef.current = eventSource;

    // Cleanup function
    return () => {
      eventSource.close();
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  // Inicializar conexión SSE
  useEffect(() => {
    const cleanup = connectSSE();
    return cleanup;
  }, [connectSSE]);

  // Limpiar al desmontar
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const value: SSEContextType = {
    sseStatus,
    containerStatus,
    containerMetrics,
  };

  return (
    <SSEContext.Provider value={value}>
      {children}
    </SSEContext.Provider>
  );
};