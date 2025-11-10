import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { ExternalLink, Play, Square, Trash2, Activity } from 'lucide-react';
import { Project, normalizeUrl } from '../../lib/api';
import { LiveStatusBadge } from './LiveStatusBadge';
import { ContainerStatus, useSSE } from '../../lib/sse-context';

interface ProjectCardProps {
  project: Project;
  onStart?: (id: string) => void;
  onStop?: (id: string) => void;
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
  stopped: {
    label: 'Stopped',
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
};

const templateConfig = {
  static: { label: 'Static', color: 'bg-blue-100 text-blue-800' },
  react: { label: 'React', color: 'bg-cyan-100 text-cyan-800' },
  flask: { label: 'Flask', color: 'bg-purple-100 text-purple-800' },
  nodejs: { label: 'Node.js', color: 'bg-green-100 text-green-800' },
};

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onStart,
  onStop,
  onDelete,
  onViewDetails,
  loading = false,
}) => {
  const template = templateConfig[project.template];
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
          <Badge variant="outline" className={template.color}>
            {template.label}
          </Badge>
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
            {currentStatus === 'stopped' || currentStatus === 'inactive' ? (
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
