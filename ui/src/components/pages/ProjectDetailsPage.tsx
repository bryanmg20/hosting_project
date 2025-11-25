import React, { useState, useEffect } from 'react';
import { Header } from '../hosting/Header';
import { LiveStatusBadge } from '../hosting/LiveStatusBadge';
import { LiveMetricsChart } from '../hosting/LiveMetricsChart';
import { SSEIndicator } from '../hosting/SSEIndicator';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Alert, AlertDescription } from '../ui/alert';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Separator } from '../ui/separator';
import {
  ArrowLeft,
  Play,
  Square,
  Trash2,
  ExternalLink,
  Activity,
  Cpu,
  HardDrive,
  Globe,
  Github,
  Calendar,
  AlertCircle,
  Loader2,
  RotateCw,
  PackagePlus,
} from 'lucide-react';
import {
  Project,
  getProject,
  startContainer,
  stopContainer,
  deleteProject,
  getContainerStatus,
  rebuildContainer,
  createContainer,
  normalizeUrl,
} from '../../lib/api';
import { toast } from 'sonner@2.0.3';
import { useSSE, ContainerStatus } from '../../lib/sse-context';

interface ProjectDetailsPageProps {
  projectId: string;
  onBack: () => void;
  onDeleted: () => void;
}

const statusConfig = {
  running: {
    label: 'Running',
    icon: <Activity className="w-4 h-4" />,
    className: 'bg-green-500 text-white',
    dotColor: 'bg-green-500',
  },
  exited: {
    label: 'Exited',
    icon: <Square className="w-4 h-4" />,
    className: 'bg-gray-500 text-white',
    dotColor: 'bg-gray-500',
  },
  deploying: {
    label: 'Deploying',
    icon: <Loader2 className="w-4 h-4 animate-spin" />,
    className: 'bg-yellow-500 text-white',
    dotColor: 'bg-yellow-500',
  },
  created: {
    label: 'Created',
    className: 'bg-blue-500 hover:bg-blue-600 text-white',
    dotColor: 'bg-blue-300',
  },
  error: {
    label: 'Error',
    icon: <AlertCircle className="w-4 h-4" />,
    className: 'bg-red-500 text-white',
    dotColor: 'bg-red-500',
  },
  removing: {
    label: 'Removing',
    icon: <AlertCircle className="w-4 h-4" />,
    className: 'bg-red-500 text-white',
    dotColor: 'bg-red-500',
  },
  unknown: {
    label: 'Unknown',
    icon: <AlertCircle className="w-4 h-4" />,
    className: 'bg-gray-400 text-white',
    dotColor: 'bg-gray-400',
  },
};

export const ProjectDetailsPage: React.FC<ProjectDetailsPageProps> = ({
  projectId,
  onBack,
  onDeleted,
}) => {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const { containerStatus, containerMetrics, updateContainerStatus } = useSSE();
  
  // Usar estado del SSE si está disponible
  const currentStatus = project ? (containerStatus[projectId] as ContainerStatus) || (project.status as ContainerStatus) : null;
  const liveMetrics = containerMetrics[projectId];

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      setLoading(true);
      setError('');
      // API Call: GET /api/projects/:id
      const data = await getProject(projectId);
      if (data) {
        setProject(data);
        // Solo sincronizar con SSE si NO tiene datos previos (evita sobrescribir)
        if (!containerStatus[projectId]) {
          updateContainerStatus(projectId, data.status as ContainerStatus);
        }
      } else {
        setError('Project not found');
      }
    } catch (err) {
      setError('Error loading project');
      toast.error('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async () => {
    if (!project) return;

    try {
      setActionLoading(true);
      
      // Actualizar estado optimista a "deploying"
      updateContainerStatus(projectId, 'deploying');
      
      // API Call: POST /api/containers/:id/start
      await startContainer(project.id);
      
      toast.success('Container started successfully');
      
      // El SSE actualizará el estado a "running" automáticamente
      // No necesitamos refetch
    } catch (err) {
      toast.error('Failed to start container');
      // Revertir en caso de error
      updateContainerStatus(projectId, 'exited');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStop = async () => {
    if (!project) return;

    try {
      setActionLoading(true);
      
      // API Call: POST /api/containers/:id/stop
      await stopContainer(project.id);
      
      toast.success('Container stopped successfully');
      
      // El SSE actualizará el estado a "exited" automáticamente
      // No necesitamos refetch
    } catch (err) {
      toast.error('Failed to stop container');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRebuild = async () => {
    if (!project) return;

    if (!confirm('This will rebuild your container with the latest code from GitHub. Continue?')) {
      return;
    }

    try {
      setActionLoading(true);
      
      // Actualizar estado optimista a "deploying"
      updateContainerStatus(projectId, 'deploying');
      
      // API Call: POST /api/containers/:id/rebuild
      await rebuildContainer(project.id);
      
      toast.success('Container rebuild started');
      
      // El SSE actualizará el estado a "running" cuando termine
      // No necesitamos refetch
    } catch (err) {
      toast.error('Failed to rebuild container');
      // Revertir en caso de error
      updateContainerStatus(projectId, currentStatus || 'exited');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!project) return;

    try {
      setActionLoading(true);
      
      // Actualizar estado optimista a "deploying"
      updateContainerStatus(projectId, 'deploying');
      
      // API Call: POST /api/containers/:id/create
      await createContainer(project.id);
      
      toast.success('Container created successfully');
      
      // El SSE actualizará el estado a "running" o "exited" automáticamente
      // No necesitamos refetch
    } catch (err) {
      toast.error('Failed to create container');
      // Revertir en caso de error
      updateContainerStatus(projectId, 'unknown');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!project) return;

    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return;
    }

    try {
      setActionLoading(true);
      // API Call: DELETE /api/projects/:id
      await deleteProject(project.id);
      toast.success('Project deleted successfully');
      onDeleted();
    } catch (err) {
      toast.error('Failed to delete project');
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <Button variant="ghost" onClick={onBack} className="mb-6">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || 'Project not found'}</AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  const status = statusConfig[currentStatus!] || statusConfig.unknown;

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <Button variant="ghost" onClick={onBack} className="mb-6">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>

        {/* SSE Connection Status */}
        <div className="mb-6">
          <SSEIndicator />
        </div>

        {/* Status Alerts */}
        {currentStatus === 'unknown' && (
          <Alert className="mb-6 bg-gray-50 dark:bg-gray-950 border-gray-200 dark:border-gray-800">
            <AlertCircle className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            <AlertDescription className="text-gray-800 dark:text-gray-200">
              <strong>Container Not Found:</strong> This project doesn't have a container yet. Click "Create Container" to deploy it.
            </AlertDescription>
          </Alert>
        )}

        {currentStatus === 'inactive' && (
          <Alert className="mb-6 bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800">
            <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
            <AlertDescription className="text-yellow-800 dark:text-yellow-200">
              <strong>Container Paused:</strong> This container has been paused due to inactivity. Click "Reactivate" to resume.
            </AlertDescription>
          </Alert>
        )}

        {currentStatus === 'error' && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Deployment Error:</strong> The container encountered an error during deployment. Check the logs below and click "Retry" to attempt redeployment.
            </AlertDescription>
          </Alert>
        )}

        {currentStatus === 'deploying' && (
          <Alert className="mb-6 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
            <Loader2 className="h-4 w-4 text-blue-600 dark:text-blue-400 animate-spin" />
            <AlertDescription className="text-blue-800 dark:text-blue-200">
              <strong>Deployment in Progress:</strong> Your container is currently being deployed. This may take a few minutes.
            </AlertDescription>
          </Alert>
        )}

        {/* Project Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2 flex-wrap">
                  <CardTitle>{project.name}</CardTitle>
                  <LiveStatusBadge status={currentStatus!} />
                </div>
                <CardDescription>
                  Created on {new Date(project.created_at).toLocaleDateString()}
                </CardDescription>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {currentStatus === 'unknown' ? (
                  <Button onClick={handleCreate} disabled={actionLoading}>
                    {actionLoading ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <PackagePlus className="w-4 h-4 mr-2" />
                    )}
                    Create Container
                  </Button>
                ) : currentStatus === 'exited' || currentStatus === 'inactive' || currentStatus === 'created' ? (
                  <>
                    <Button onClick={handleStart} disabled={actionLoading}>
                      {actionLoading ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Play className="w-4 h-4 mr-2" />
                      )}
                      {currentStatus === 'inactive' ? 'Reactivate' : 'Start'}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleRebuild}
                      disabled={actionLoading}
                      title="Rebuild with latest code from GitHub"
                    >
                      {actionLoading ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <RotateCw className="w-4 h-4 mr-2" />
                      )}
                      Rebuild
                    </Button>
                  </>
                ) : currentStatus === 'running' ? (
                  <>
                    <Button variant="outline" onClick={handleStop} disabled={actionLoading}>
                      {actionLoading ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Square className="w-4 h-4 mr-2" />
                      )}
                      Stop
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleRebuild}
                      disabled={actionLoading}
                      title="Rebuild with latest code from GitHub"
                    >
                      {actionLoading ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <RotateCw className="w-4 h-4 mr-2" />
                      )}
                      Rebuild
                    </Button>
                    <Button
                      variant="outline"
                      onClick={loadProject}
                      disabled={actionLoading}
                      title="Refresh metrics"
                    >
                      <RotateCw className="w-4 h-4" />
                    </Button>
                  </>
                ) : currentStatus === 'error' ? (
                  <Button onClick={handleStart} disabled={actionLoading} variant="default">
                    {actionLoading ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <RotateCw className="w-4 h-4 mr-2" />
                    )}
                    Retry
                  </Button>
                ) : null}

                {currentStatus === 'running' && (
                  <Button
                    variant="outline"
                    onClick={() => window.open(normalizeUrl(project.url), '_blank')}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Open
                  </Button>
                )}

                <Button
                  variant="destructive"
                  onClick={handleDelete}
                  disabled={actionLoading}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Live Metrics - Solo si el contenedor está running */}
            {currentStatus === 'running' && liveMetrics && (
              <LiveMetricsChart metrics={liveMetrics} projectId={projectId} />
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Project Info */}
            <Card>
              <CardHeader>
                <CardTitle>Project Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <Globe className="w-4 h-4" />
                    <span>URL</span>
                  </div>
                  <a
                    href={normalizeUrl(project.url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:underline break-all"
                  >
                    {project.url}
                  </a>
                </div>

                <Separator />

                <div>
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <Github className="w-4 h-4" />
                    <span>Repository</span>
                  </div>
                  <a
                    href={project.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:underline break-all"
                  >
                    {project.github_url}
                  </a>
                </div>

                <Separator />

                <div>
                  <div className="flex items-center gap-2 text-muted-foreground mb-1">
                    <Calendar className="w-4 h-4" />
                    <span>Created</span>
                  </div>
                  <p>{new Date(project.created_at).toLocaleString()}</p>
                </div>
              </CardContent>
            </Card>

            {/* Container Status */}
            <Card>
              <CardHeader>
                <CardTitle>Container Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                  <div className={`w-3 h-3 rounded-full ${status.dotColor} animate-pulse`} />
                  <div className="flex-1">
                    <p>Container is {status.label.toLowerCase()}</p>
                    <p className="text-muted-foreground">
                      Last checked: {new Date().toLocaleTimeString()}
                    </p>
                  </div>
                </div>
                <p className="text-muted-foreground mt-4">
                  {currentStatus === 'running'
                    ? 'Your application is accessible and serving traffic.'
                    : currentStatus === 'exited'
                    ? 'Start the container to make your application accessible.'
                    : currentStatus === 'deploying'
                    ? 'Your application is being deployed. This may take a few moments.'
                    : currentStatus === 'unknown'
                    ? 'No container exists for this project. Create one to deploy your application.'
                    : currentStatus === 'inactive'
                    ? 'Container has been paused due to inactivity. Click Reactivate to resume.'
                    : 'There was an error with your container. Please check the logs.'}
                </p>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {currentStatus === 'running' && (
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => window.open(normalizeUrl(project.url), '_blank')}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Visit Website
                  </Button>
                )}
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => window.open(project.github_url, '_blank')}
                >
                  <Github className="w-4 h-4 mr-2" />
                  View on GitHub
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                  onClick={handleDelete}
                  disabled={actionLoading}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Project
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};
