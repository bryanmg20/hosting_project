import React from 'react';
import { Header } from '../hosting/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Code2,
  Database,
  Layers,
  GitBranch,
  Workflow,
  CheckCircle2,
  XCircle,
  Info,
  ArrowLeft,
} from 'lucide-react';

interface DocumentationPageProps {
  onBack?: () => void;
}

export const DocumentationPage: React.FC<DocumentationPageProps> = ({ onBack }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="container mx-auto px-4 py-8">
        {onBack && (
          <Button variant="ghost" onClick={onBack} className="mb-6">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        )}
        
        <div className="mb-8">
          <h1 className="mb-2">API Documentation</h1>
          <p className="text-gray-500">
            Complete reference for backend integration
          </p>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="auth">Authentication</TabsTrigger>
            <TabsTrigger value="projects">Projects</TabsTrigger>
            <TabsTrigger value="containers">Containers</TabsTrigger>
            <TabsTrigger value="flows">User Flows</TabsTrigger>
          </TabsList>

          {/* Overview */}
          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="w-5 h-5" />
                  Architecture Overview
                </CardTitle>
                <CardDescription>
                  Understanding the platform structure
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert className="bg-blue-50 border-blue-200">
                  <Info className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-blue-800">
                    This is a <strong>frontend-only mockup</strong>. All data is stored in localStorage and all API calls are simulated with delays to mimic real network behavior.
                  </AlertDescription>
                </Alert>

                <div>
                  <h3 className="mb-2">Base URL</h3>
                  <code className="block p-3 bg-gray-100 rounded-lg">
                    https://api.clouddeploy.com
                  </code>
                </div>

                <div>
                  <h3 className="mb-2">Authentication</h3>
                  <p className="text-gray-600">
                    All authenticated endpoints require a Bearer token in the Authorization header:
                  </p>
                  <code className="block p-3 bg-gray-100 rounded-lg mt-2">
                    Authorization: Bearer YOUR_JWT_TOKEN
                  </code>
                </div>

                <div>
                  <h3 className="mb-2">Response Format</h3>
                  <p className="text-gray-600">All responses follow this structure:</p>
                  <pre className="block p-3 bg-gray-100 rounded-lg mt-2 overflow-x-auto">
{`{
  "success": true,
  "data": { ... },
  "error": null
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Authentication */}
          <TabsContent value="auth" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>POST /api/auth/register</CardTitle>
                <CardDescription>Create a new user account</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">Request Body</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}`}
                  </pre>
                </div>
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "user": {
      "id": "usr_123",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}`}
                  </pre>
                </div>
                <div>
                  <h4 className="mb-2">Error Response (400 Bad Request)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": false,
  "error": "Email already exists"
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>POST /api/auth/login</CardTitle>
                <CardDescription>Authenticate an existing user</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">Request Body</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "email": "user@example.com",
  "password": "securepassword"
}`}
                  </pre>
                </div>
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "user": {
      "id": "usr_123",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>POST /api/auth/logout</CardTitle>
                <CardDescription>Invalidate the current session</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">Headers</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`Authorization: Bearer YOUR_JWT_TOKEN`}
                  </pre>
                </div>
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Projects */}
          <TabsContent value="projects" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>GET /api/projects</CardTitle>
                <CardDescription>List all projects for the authenticated user</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">Headers</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`Authorization: Bearer YOUR_JWT_TOKEN`}
                  </pre>
                </div>
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": [
    {
      "id": "proj_123",
      "name": "mi-portafolio",
      "status": "running",
      "url": "http://miportafolio.user.localhost",
      "template": "react",
      "github_url": "https://github.com/user/repo",
      "created_at": "2025-11-01T10:30:00Z",
      "metrics": {
        "cpu": 45,
        "memory": 512,
        "requests": 1250
      }
    }
  ]
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>GET /api/projects/:id</CardTitle>
                <CardDescription>Get details of a specific project</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">URL Parameters</h4>
                  <p className="text-gray-600">
                    <code className="bg-gray-100 px-2 py-1 rounded">id</code> - Project ID
                  </p>
                </div>
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "id": "proj_123",
    "name": "mi-portafolio",
    "status": "running",
    "url": "http://miportafolio.user.localhost",
    "template": "react",
    "github_url": "https://github.com/user/repo",
    "created_at": "2025-11-01T10:30:00Z",
    "metrics": {
      "cpu": 45,
      "memory": 512,
      "requests": 1250
    }
  }
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>POST /api/projects</CardTitle>
                <CardDescription>Create and deploy a new project</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">Request Body</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "name": "my-awesome-project",
  "github_url": "https://github.com/user/repo",
  "template": "react"
}`}
                  </pre>
                  <p className="text-gray-600 mt-2">
                    Template options: <code className="bg-gray-100 px-2 py-1 rounded">static</code>, <code className="bg-gray-100 px-2 py-1 rounded">react</code>, <code className="bg-gray-100 px-2 py-1 rounded">nodejs</code>, <code className="bg-gray-100 px-2 py-1 rounded">flask</code>
                  </p>
                </div>
                <div>
                  <h4 className="mb-2">Response (201 Created)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "id": "proj_456",
    "name": "my-awesome-project",
    "status": "deploying",
    "url": "http://my-awesome-project.user.localhost",
    "template": "react",
    "github_url": "https://github.com/user/repo",
    "created_at": "2025-11-07T14:30:00Z"
  }
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>DELETE /api/projects/:id</CardTitle>
                <CardDescription>Delete a project and its container</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">URL Parameters</h4>
                  <p className="text-gray-600">
                    <code className="bg-gray-100 px-2 py-1 rounded">id</code> - Project ID
                  </p>
                </div>
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "message": "Project deleted successfully"
  }
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Containers */}
          <TabsContent value="containers" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>GET /api/containers/:id/status</CardTitle>
                <CardDescription>Get the current status of a container</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "status": "running",
    "uptime": 86400,
    "last_restart": "2025-11-07T08:00:00Z"
  }
}`}
                  </pre>
                  <p className="text-gray-600 mt-2">
                    Status values: <code className="bg-gray-100 px-2 py-1 rounded">running</code>, <code className="bg-gray-100 px-2 py-1 rounded">stopped</code>, <code className="bg-gray-100 px-2 py-1 rounded">deploying</code>, <code className="bg-gray-100 px-2 py-1 rounded">error</code>
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>POST /api/containers/:id/start</CardTitle>
                <CardDescription>Start a stopped container</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "message": "Container started successfully",
    "status": "running"
  }
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>POST /api/containers/:id/stop</CardTitle>
                <CardDescription>Stop a running container</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "message": "Container stopped successfully",
    "status": "stopped"
  }
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>GET /api/containers/:id/logs</CardTitle>
                <CardDescription>Get container logs</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="mb-2">Query Parameters</h4>
                  <p className="text-gray-600">
                    <code className="bg-gray-100 px-2 py-1 rounded">lines</code> - Number of log lines (default: 100)
                  </p>
                </div>
                <div>
                  <h4 className="mb-2">Response (200 OK)</h4>
                  <pre className="p-3 bg-gray-100 rounded-lg overflow-x-auto">
{`{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-11-07T10:30:15Z",
        "level": "info",
        "message": "Server started on port 3000"
      }
    ]
  }
}`}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* User Flows */}
          <TabsContent value="flows" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Workflow className="w-5 h-5" />
                  Flow 1: New User Registration
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-3 list-decimal list-inside">
                  <li>User lands on registration page</li>
                  <li>User fills in name, email, password</li>
                  <li>Frontend validates input (password length, email format)</li>
                  <li>POST /api/auth/register with user data</li>
                  <li>Backend creates user account</li>
                  <li>Backend returns JWT token</li>
                  <li>Frontend stores token and user data</li>
                  <li>User redirected to dashboard</li>
                </ol>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Workflow className="w-5 h-5" />
                  Flow 2: Creating and Deploying a Project
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-3 list-decimal list-inside">
                  <li>User clicks "Create New Project" from dashboard</li>
                  <li>User selects template (Static, React, Node.js)</li>
                  <li>User enters project name and GitHub URL</li>
                  <li>Frontend shows URL preview</li>
                  <li>User clicks "Deploy Project"</li>
                  <li>POST /api/projects with project data</li>
                  <li>Backend clones repository</li>
                  <li>Backend builds and creates container</li>
                  <li>Frontend shows deployment progress (loading state)</li>
                  <li>Deployment completes, status changes to "running"</li>
                  <li>User redirected to project details page</li>
                </ol>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Workflow className="w-5 h-5" />
                  Flow 3: Managing Container Lifecycle
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-3 list-decimal list-inside">
                  <li>User navigates to project details page</li>
                  <li>GET /api/projects/:id to load project data</li>
                  <li>GET /api/containers/:id/status to check container status</li>
                  <li>User clicks "Stop" button</li>
                  <li>POST /api/containers/:id/stop</li>
                  <li>Backend stops container</li>
                  <li>Frontend updates UI to show "Stopped" status</li>
                  <li>User clicks "Start" button</li>
                  <li>POST /api/containers/:id/start</li>
                  <li>Backend starts container</li>
                  <li>Frontend updates UI to show "Running" status</li>
                </ol>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Workflow className="w-5 h-5" />
                  Flow 4: Deleting a Project
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-3 list-decimal list-inside">
                  <li>User clicks "Delete" button on project</li>
                  <li>Frontend shows confirmation dialog</li>
                  <li>User confirms deletion</li>
                  <li>DELETE /api/projects/:id</li>
                  <li>Backend stops container</li>
                  <li>Backend deletes container and project data</li>
                  <li>Frontend removes project from list</li>
                  <li>User redirected to dashboard</li>
                </ol>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
