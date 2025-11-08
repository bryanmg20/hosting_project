import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Activity, AlertCircle, TrendingUp, Power } from 'lucide-react';

interface SSEEvent {
  id: string;
  type: 'container_status_changed' | 'metrics_updated' | 'deployment_progress' | 'auto_shutdown';
  timestamp: string;
  projectId: string;
  data: any;
}

const eventConfig = {
  container_status_changed: {
    icon: Activity,
    color: 'bg-blue-500',
    textColor: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-50 dark:bg-blue-950/30',
    label: 'Status Changed',
  },
  metrics_updated: {
    icon: TrendingUp,
    color: 'bg-green-500',
    textColor: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-950/30',
    label: 'Metrics Update',
  },
  deployment_progress: {
    icon: AlertCircle,
    color: 'bg-purple-500',
    textColor: 'text-purple-600 dark:text-purple-400',
    bgColor: 'bg-purple-50 dark:bg-purple-950/30',
    label: 'Deploy Progress',
  },
  auto_shutdown: {
    icon: Power,
    color: 'bg-orange-500',
    textColor: 'text-orange-600 dark:text-orange-400',
    bgColor: 'bg-orange-50 dark:bg-orange-950/30',
    label: 'Auto Shutdown',
  },
};

export const SSEEventsDemo: React.FC<{ projectId?: string }> = ({ projectId }) => {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Simular eventos SSE entrantes para demostración
    const eventTypes: SSEEvent['type'][] = [
      'metrics_updated',
      'container_status_changed',
      'deployment_progress',
    ];

    const interval = setInterval(() => {
      const randomType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      
      const newEvent: SSEEvent = {
        id: `${Date.now()}-${Math.random()}`,
        type: randomType,
        timestamp: new Date().toISOString(),
        projectId: projectId || 'proj-1',
        data: {
          message: `Simulated ${randomType} event`,
        },
      };

      setEvents((prev) => {
        const updated = [...prev, newEvent];
        return updated.slice(-20); // Mantener solo los últimos 20
      });
    }, 8000); // Nuevo evento cada 8 segundos

    return () => clearInterval(interval);
  }, [projectId]);

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      const scrollContainer = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [events]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              SSE Events Stream
            </CardTitle>
            <CardDescription className="mt-1">
              Eventos en tiempo real desde el backend
            </CardDescription>
          </div>
          <Badge variant="outline" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            {events.length} eventos
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div ref={scrollRef}>
          <ScrollArea className="h-[300px] w-full rounded-md border bg-muted/30 p-4">
            {events.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <Activity className="w-8 h-8 mb-2 opacity-50" />
                <p className="text-sm">Esperando eventos SSE...</p>
              </div>
            ) : (
              <div className="space-y-2">
                {events.map((event) => {
                  const config = eventConfig[event.type];
                  const Icon = config.icon;
                  
                  return (
                    <div
                      key={event.id}
                      className={`flex items-start gap-3 p-3 rounded-lg ${config.bgColor} transition-all duration-300 animate-in fade-in slide-in-from-bottom-2`}
                    >
                      <div className={`w-2 h-2 rounded-full ${config.color} mt-1.5 animate-pulse`} />
                      <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${config.textColor}`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <code className={`text-xs ${config.textColor}`}>
                            {event.type}
                          </code>
                          <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Project: {event.projectId}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </ScrollArea>
        </div>
        <div className="mt-3 text-xs text-muted-foreground">
          <p>📡 Endpoint: <code className="px-1 py-0.5 bg-muted rounded">GET /api/containers/events</code></p>
        </div>
      </CardContent>
    </Card>
  );
};
