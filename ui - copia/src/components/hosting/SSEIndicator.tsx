import React, { useState } from 'react';
import { Radio, WifiOff, Loader2, Info } from 'lucide-react';
import { useSSE, SSEStatus } from '../../lib/sse-context';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '../ui/popover';

const statusConfig: Record<SSEStatus, {
  icon: React.ElementType;
  label: string;
  className: string;
  animate: boolean;
  description: string;
}> = {
  connecting: {
    icon: Loader2,
    label: '🔵 Conectando...',
    className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    animate: true,
    description: 'Estableciendo conexión SSE',
  },
  connected: {
    icon: Radio,
    label: '✅ Conectado',
    className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    animate: false,
    description: 'Actualizaciones automáticas',
  },
  disconnected: {
    icon: WifiOff,
    label: '🔴 Desconectado',
    className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    animate: false,
    description: 'Reconectando automáticamente...',
  },
};

const sseEvents = [
  {
    name: 'container_status_changed',
    description: 'Cuando cambia estado running/stopped',
    color: 'text-blue-600 dark:text-blue-400',
  },
  {
    name: 'metrics_updated',
    description: 'Métricas cada X tiempo definido por el backend',
    color: 'text-green-600 dark:text-green-400',
  },
  {
    name: 'deployment_progress',
    description: 'Durante deploy de contenedores',
    color: 'text-purple-600 dark:text-purple-400',
  },
  {
    name: 'auto_shutdown',
    description: 'Cuando se apaga por inactividad',
    color: 'text-orange-600 dark:text-orange-400',
  },
];

export const SSEIndicator: React.FC = () => {
  const { sseStatus } = useSSE();
  const config = statusConfig[sseStatus];
  const Icon = config.icon;

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 p-4 bg-muted/50 rounded-lg border">
      <div className="flex items-center gap-3 flex-1">
        {/* SSE Status */}
        <Badge variant="outline" className={config.className}>
          <Icon className={`w-3 h-3 mr-1.5 ${config.animate ? 'animate-spin' : ''}`} />
          {config.label}
        </Badge>

        {/* Connection Info */}
        <div className="text-muted-foreground text-sm">
          <span className="hidden sm:inline">
            {config.description}
          </span>
        </div>
      </div>

      {/* Event Types Info */}
      <div className="flex items-center gap-2">
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" size="sm" className="h-8">
              <Info className="w-3 h-3 mr-1.5" />
              Eventos SSE
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80" align="end">
            <div className="space-y-3">
              <div>
                <h4 className="font-medium mb-1">Server-Sent Events</h4>
                <p className="text-xs text-muted-foreground">
                  Eventos que el backend envía automáticamente
                </p>
              </div>
              <div className="space-y-2">
                {sseEvents.map((event) => (
                  <div key={event.name} className="text-xs">
                    <code className={`${event.color}`}>
                      {event.name}
                    </code>
                    <p className="text-muted-foreground mt-0.5 ml-1">
                      {event.description}
                    </p>
                  </div>
                ))}
              </div>
              <div className="pt-2 border-t">
                <code className="text-xs text-muted-foreground">
                  GET /api/containers/events
                </code>
              </div>
            </div>
          </PopoverContent>
        </Popover>
      </div>
    </div>
  );
};
