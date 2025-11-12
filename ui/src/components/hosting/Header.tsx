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
    <header className="border-b border-border/50 bg-card/95 backdrop-blur-sm shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-600/20 dark:shadow-blue-500/10 ring-2 ring-blue-100 dark:ring-blue-950 transition-transform duration-300 hover:scale-105">
              <Server className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-lg">CloudDeploy</h1>
              <p className="text-sm text-muted-foreground">Container Hosting Platform</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right hidden md:block mr-2">
              <p>{user?.name}</p>
            </div>
            <Button 
              variant="ghost" 
              onClick={toggleTheme} 
              size="icon"
              className="hover:bg-muted/50 transition-all duration-200"
            >
              {theme === 'dark' ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </Button>
            <Button 
              variant="outline" 
              onClick={handleLogout}
              className="border-border/50 hover:bg-muted/50 transition-all duration-200"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};
