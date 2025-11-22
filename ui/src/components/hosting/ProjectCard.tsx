import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { ExternalLink, Play, Square, Trash2, Activity, PackagePlus } from 'lucide-react';
import { Project, normalizeUrl } from '../../lib/api';
import { LiveStatusBadge } from './LiveStatusBadge';
import { ContainerStatus, useSSE } from '../../lib/sse-context';

interface ProjectCardProps {
  project: Project;
  onStart?: (id: string) => void;
  onStop?: (id: string) => void;
  onCreate?: (id: string) => void;
  onDelete?: (id: string) => void;
  onViewDetails?: (id: string) => void;
  loading?: boolean;
}

const statusConfig = {
  running: {
    label: 'Running',
    variant: 'default' as const,
    className: 'bg-green-500 hover:bg-green-600',
  },
  exited: {
    label: 'Exited',
    variant: 'secondary' as const,
    className: 'bg-gray-500 hover:bg-gray-600',
  },
  deploying: {
    label: 'Deploying',
    variant: 'default' as const,
    className: 'bg-yellow-500 hover:bg-yellow-600',
  },
  error: {
    label: 'Error',
    variant: 'destructive' as const,
    className: 'bg-red-500 hover:bg-red-600',
  },
  unknown: {
    label: 'Unknown',
    variant: 'secondary' as const,
    className: 'bg-gray-400 hover:bg-gray-500',
  },
};

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onStart,
  onStop,
  onCreate,
  onDelete,
  onViewDetails,
  loading = false,
}) => {
  const { containerStatus, containerMetrics } = useSSE();
  
  // Usar estado del SSE si está disponible, sino usar el del proyecto
  const currentStatus = (containerStatus[project.id] as ContainerStatus) || (project.status as ContainerStatus);
  const currentMetrics = containerMetrics[project.id] || project.metrics;

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2">
              {project.name}
              <LiveStatusBadge status={currentStatus} />
            </CardTitle>
            <a
              href={normalizeUrl(project.url)}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 dark:text-blue-400 hover:underline mt-1 inline-flex items-center gap-1"
              onClick={(e) => e.stopPropagation()}
            >
              {project.url}
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Metrics */}
          <div className="grid grid-cols-3 gap-4 py-3 border-t border-b">
            <div>
              <p className="text-muted-foreground flex items-center gap-1">
                <Activity className="w-4 h-4" /> CPU
              </p>
              <p className="mt-1">{Math.round(currentMetrics.cpu)}%</p>
            </div>
            <div>
              <p className="text-muted-foreground">Memory</p>
              <p className="mt-1">{Math.round(currentMetrics.memory)} MB</p>
            </div>
            <div>
              <p className="text-muted-foreground">Requests</p>
              <p className="mt-1">{currentMetrics.requests}</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {currentStatus === 'unknown' ? (
              <Button
                size="sm"
                onClick={() => onCreate?.(project.id)}
                disabled={loading}
                className="flex-1"
              >
                <PackagePlus className="w-4 h-4 mr-2" />
                Create
              </Button>
            ) : currentStatus === 'exited' || currentStatus === 'inactive' || currentStatus === 'created' ? (
              <Button
                size="sm"
                onClick={() => onStart?.(project.id)}
                disabled={loading}
                className="flex-1"
              >
                <Play className="w-4 h-4 mr-2" />
                Start
              </Button>
            ) : currentStatus === 'running' ? (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onStop?.(project.id)}
                disabled={loading}
                className="flex-1"
              >
                <Square className="w-4 h-4 mr-2" />
                Stop
              </Button>
            ) : null}

            <Button
              size="sm"
              variant="outline"
              onClick={() => onViewDetails?.(project.id)}
              className="flex-1"
            >
              View Details
            </Button>

            <Button
              size="sm"
              variant="ghost"
              onClick={() => onDelete?.(project.id)}
              disabled={loading}
              className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
