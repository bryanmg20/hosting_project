import React, { useState, useEffect } from 'react';
import { Header } from '../hosting/Header';
import { ProjectCard } from '../hosting/ProjectCard';
import { SSEIndicator } from '../hosting/SSEIndicator';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Plus, AlertCircle, Loader2, FolderOpen } from 'lucide-react';
import { Project, getProjects, startContainer, stopContainer, deleteProject } from '../../lib/api';
import { toast } from 'sonner@2.0.3';
import { useSSE } from '../../lib/sse-context';

interface DashboardPageProps {
  onCreateProject: () => void;
  onViewProject: (id: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onCreateProject,
  onViewProject,
}) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const { containerMetrics, updateContainerStatus } = useSSE();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError('');
      // API Call: GET /api/projects
      const data = await getProjects();
      setProjects(data);
      
      // Sincronizar estados iniciales con SSE
      data.forEach(project => {
        updateContainerStatus(project.id, project.status as any);
      });
    } catch (err) {
      setError('Error loading projects');
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async (id: string) => {
    try {
      setActionLoading(id);
      // Actualizar estado a "deploying" mientras arranca
      updateContainerStatus(id, 'deploying');
      
      // API Call: POST /api/containers/:id/start
      await startContainer(id);
      toast.success('Container started successfully');
      
      // El SSE actualizará el estado a "running" automáticamente
      // No necesitamos refetch completo
    } catch (err) {
      toast.error('Failed to start container');
      // Revertir a stopped en caso de error
      updateContainerStatus(id, 'stopped');
    } finally {
      setActionLoading(null);
    }
  };

  const handleStop = async (id: string) => {
    try {
      setActionLoading(id);
      
      // API Call: POST /api/containers/:id/stop
      await stopContainer(id);
      toast.success('Container stopped successfully');
      
      // El SSE actualizará el estado a "stopped" automáticamente
      // No necesitamos refetch completo
    } catch (err) {
      toast.error('Failed to stop container');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this project?')) {
      return;
    }

    try {
      setActionLoading(id);
      // API Call: DELETE /api/projects/:id
      await deleteProject(id);
      toast.success('Project deleted successfully');
      await loadProjects();
    } catch (err) {
      toast.error('Failed to delete project');
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <div className="container mx-auto px-4 py-8">
        {/* SSE Connection Status */}
        <div className="mb-6">
          <SSEIndicator />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2>Your Projects</h2>
            <p className="text-muted-foreground mt-1">
              Manage and monitor your deployed applications
            </p>
          </div>
          <Button onClick={onCreateProject}>
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </Button>
        </div>

        {/* Error State */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : projects.length === 0 ? (
          /* Empty State */
          <Card className="py-12">
            <CardContent className="text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FolderOpen className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="mb-2">No projects yet</h3>
              <p className="text-muted-foreground mb-6">
                Create your first project to start deploying applications
              </p>
              <Button onClick={onCreateProject}>
                <Plus className="w-4 h-4 mr-2" />
                Create First Project
              </Button>
            </CardContent>
          </Card>
        ) : (
          /* Projects Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onStart={handleStart}
                onStop={handleStop}
                onDelete={handleDelete}
                onViewDetails={onViewProject}
                loading={actionLoading === project.id}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
