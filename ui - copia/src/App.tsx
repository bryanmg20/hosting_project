import React, { useState } from 'react';
import { AuthProvider, useAuth } from './lib/auth-context';
import { ThemeProvider } from './lib/theme-context';
import { SSEProvider } from './lib/sse-context';
import { LoginPage } from './components/pages/LoginPage';
import { RegisterPage } from './components/pages/RegisterPage';
import { DashboardPage } from './components/pages/DashboardPage';
import { CreateProjectPage } from './components/pages/CreateProjectPage';
import { ProjectDetailsPage } from './components/pages/ProjectDetailsPage';
import { Toaster } from './components/ui/sonner';
import { Loader2 } from 'lucide-react';

type Page = 'login' | 'register' | 'dashboard' | 'create-project' | 'project-details';

interface AppState {
  page: Page;
  selectedProjectId?: string;
}

function AppContent() {
  const { user, loading } = useAuth();
  const [appState, setAppState] = useState<AppState>({
    page: 'dashboard',
  });

  // Handle navigation
  const navigateTo = (page: Page, projectId?: string) => {
    setAppState({ page, selectedProjectId: projectId });
  };

  // Show loading screen while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-muted-foreground">Loading CloudDeploy...</p>
        </div>
      </div>
    );
  }

  // Show authentication pages if not logged in
  if (!user) {
    if (appState.page === 'register') {
      return (
        <RegisterPage onSwitchToLogin={() => navigateTo('login')} />
      );
    }
    return (
      <LoginPage onSwitchToRegister={() => navigateTo('register')} />
    );
  }

  // Show application pages for authenticated users
  switch (appState.page) {
    case 'create-project':
      return (
        <CreateProjectPage
          onBack={() => navigateTo('dashboard')}
          onSuccess={(projectId) => navigateTo('project-details', projectId)}
        />
      );

    case 'project-details':
      if (!appState.selectedProjectId) {
        navigateTo('dashboard');
        return null;
      }
      return (
        <ProjectDetailsPage
          projectId={appState.selectedProjectId}
          onBack={() => navigateTo('dashboard')}
          onDeleted={() => navigateTo('dashboard')}
        />
      );

    case 'dashboard':
    default:
      return (
        <DashboardPage
          onCreateProject={() => navigateTo('create-project')}
          onViewProject={(projectId) => navigateTo('project-details', projectId)}
        />
      );
  }
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <SSEProvider>
          <AppContent />
          <Toaster position="top-right" />
        </SSEProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
