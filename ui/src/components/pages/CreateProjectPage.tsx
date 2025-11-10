import React, { useState } from 'react';
import { Header } from '../hosting/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { ArrowLeft, CheckCircle2, XCircle, Loader2, Code2, Rocket, Flame, ExternalLink } from 'lucide-react';
import { createProject, Project } from '../../lib/api';
import { toast } from 'sonner@2.0.3';

interface CreateProjectPageProps {
  onBack: () => void;
  onSuccess: (projectId: string) => void;
}

type Template = Project['template'];

const templates: Array<{
  id: Template;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  githubUrl: string;
}> = [
  {
    id: 'static',
    name: 'HTML/CSS/JavaScript',
    description: 'Static websites with vanilla JavaScript',
    icon: <Code2 className="w-8 h-8" />,
    color: 'border-blue-500 bg-blue-50 dark:bg-blue-950 dark:border-blue-700',
    githubUrl: 'https://github.com/clouddeploy-templates/html-static',
  },
  {
    id: 'react',
    name: 'React Application',
    description: 'React apps with modern build tools',
    icon: <Rocket className="w-8 h-8" />,
    color: 'border-cyan-500 bg-cyan-50 dark:bg-cyan-950 dark:border-cyan-700',
    githubUrl: 'https://github.com/clouddeploy-templates/react-app',
  },
  {
    id: 'flask',
    name: 'Flask Backend',
    description: 'Python Flask web applications',
    icon: <Flame className="w-8 h-8" />,
    color: 'border-purple-500 bg-purple-50 dark:bg-purple-950 dark:border-purple-700',
    githubUrl: 'https://github.com/clouddeploy-templates/flask-backend',
  },
];

type DeployState = 'idle' | 'deploying' | 'success' | 'error';

export const CreateProjectPage: React.FC<CreateProjectPageProps> = ({
  onBack,
  onSuccess,
}) => {
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [projectName, setProjectName] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [deployState, setDeployState] = useState<DeployState>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [createdProjectId, setCreatedProjectId] = useState('');

  const handleDeploy = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedTemplate) {
      toast.error('Please select a template');
      return;
    }

    setError('');
    setDeployState('deploying');
    setProgress(0);

    try {
      // Simulate deployment progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // API Call: POST /api/projects
      const project = await createProject(projectName, githubUrl, selectedTemplate);
      
      clearInterval(progressInterval);
      setProgress(100);
      setDeployState('success');
      setCreatedProjectId(project.id);
      toast.success('Project deployed successfully!');

      // Auto-redirect after 2 seconds
      setTimeout(() => {
        onSuccess(project.id);
        window.location.reload();
      }, 2000);
    } catch (err) {
      setDeployState('error');
      setError(err instanceof Error ? err.message : 'Failed to deploy project');
      toast.error('Deployment failed');
    }
  };

  const resetForm = () => {
    setDeployState('idle');
    setProgress(0);
    setError('');
    setProjectName('');
    setGithubUrl('');
    setSelectedTemplate(null);
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <Button variant="ghost" onClick={onBack} className="mb-6">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>

        <div className="max-w-3xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>Create New Project</CardTitle>
              <CardDescription>
                Deploy your application from a GitHub repository
              </CardDescription>
            </CardHeader>
            <CardContent>
              {deployState === 'deploying' ? (
                /* Deploying State */
                <div className="py-8 text-center">
                  <Loader2 className="w-16 h-16 animate-spin text-blue-600 mx-auto mb-4" />
                  <h3 className="mb-2">Deploying your project...</h3>
                  <p className="text-gray-500 mb-6">
                    This may take a few moments
                  </p>
                  <Progress value={progress} className="max-w-md mx-auto" />
                  <p className="text-gray-500 mt-4">{progress}%</p>
                </div>
              ) : deployState === 'success' ? (
                /* Success State */
                <div className="py-8 text-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 className="w-10 h-10 text-green-600" />
                  </div>
                  <h3 className="mb-2">Deployment Successful!</h3>
                  <p className="text-gray-500 mb-6">
                    Your project is now live and running
                  </p>
                  <Button onClick={() => onSuccess(createdProjectId)}>
                    View Project
                  </Button>
                </div>
              ) : deployState === 'error' ? (
                /* Error State */
                <div className="py-8 text-center">
                  <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <XCircle className="w-10 h-10 text-red-600" />
                  </div>
                  <h3 className="mb-2">Deployment Failed</h3>
                  <p className="text-gray-500 mb-6">{error}</p>
                  <Button onClick={resetForm}>Try Again</Button>
                </div>
              ) : (
                /* Form */
                <form onSubmit={handleDeploy} className="space-y-6">
                  {/* Template Selection */}
                  <div className="space-y-3">
                    <Label>Select Template</Label>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {templates.map((template) => (
                        <div key={template.id} className="space-y-2">
                          <button
                            type="button"
                            onClick={() => setSelectedTemplate(template.id)}
                            className={`w-full p-4 border-2 rounded-lg text-left transition-all hover:shadow-md ${
                              selectedTemplate === template.id
                                ? `${template.color} border-current`
                                : 'border-border bg-card hover:border-muted-foreground'
                            }`}
                          >
                            <div className="mb-3">{template.icon}</div>
                            <h4 className="mb-1">{template.name}</h4>
                            <p className="text-muted-foreground">{template.description}</p>
                          </button>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="w-full"
                            onClick={() => window.open(template.githubUrl, '_blank')}
                          >
                            <ExternalLink className="w-3 h-3 mr-2" />
                            Ver en GitHub
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Project Details */}
                  <div className="space-y-4 pt-4 border-t">
                    <div className="space-y-2">
                      <Label htmlFor="projectName">Project Name</Label>
                      <Input
                        id="projectName"
                        placeholder="my-awesome-project"
                        value={projectName}
                        onChange={(e) => setProjectName(e.target.value)}
                        required
                      />
                      <p className="text-muted-foreground">
                        This will be used in your project URL
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="githubUrl">GitHub Repository URL</Label>
                      <Input
                        id="githubUrl"
                        type="url"
                        placeholder="https://github.com/username/repo"
                        value={githubUrl}
                        onChange={(e) => setGithubUrl(e.target.value)}
                        required
                      />
                      <p className="text-muted-foreground">
                        Make sure the repository is public or you have access
                      </p>
                    </div>
                  </div>

                  {/* Preview */}
                  {projectName && selectedTemplate && (
                    <Alert className="bg-muted">
                      <AlertDescription>
                        <strong>Your project will be available at:</strong>
                        <br />
                        <code className="text-blue-600">
                          http://{projectName}.yourusername.localhost
                        </code>
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* Submit */}
                  <div className="flex gap-3 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={onBack}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      className="flex-1"
                      disabled={!selectedTemplate || !projectName || !githubUrl}
                    >
                      <Rocket className="w-4 h-4 mr-2" />
                      Deploy Project
                    </Button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
