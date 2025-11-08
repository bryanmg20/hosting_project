import React from 'react';
import { Button } from '../ui/button';
import { LogOut, Server, Moon, Sun } from 'lucide-react';
import { useAuth } from '../../lib/auth-context';
import { useTheme } from '../../lib/theme-context';

interface HeaderProps {}

export const Header: React.FC<HeaderProps> = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Server className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1>CloudDeploy</h1>
              <p className="text-muted-foreground">Container Hosting Platform</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden md:block">
              <p className="text-muted-foreground">Welcome back,</p>
              <p>{user?.name}</p>
            </div>
            <Button variant="ghost" onClick={toggleTheme} size="icon">
              {theme === 'dark' ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </Button>
            <Button variant="outline" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};
