import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { Server, AlertCircle, Loader2, Moon, Sun } from 'lucide-react';
import { useAuth } from '../../lib/auth-context';
import { useTheme } from '../../lib/theme-context';

interface LoginPageProps {
  onSwitchToRegister: () => void;
  prefilledEmail?: string;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSwitchToRegister, prefilledEmail }) => {
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();
  // Solo usar prefilledEmail si es un string válido y no vacío
  const validEmail = typeof prefilledEmail === 'string' && prefilledEmail.trim() ? prefilledEmail : '';
  const [email, setEmail] = useState(validEmail);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // API Call: POST /api/auth/login
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/20 dark:bg-blue-600/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-400/20 dark:bg-indigo-600/10 rounded-full blur-3xl"></div>
      </div>

      {/* Theme Toggle Button - Fixed Position */}
      <div className="fixed top-6 right-6 z-10">
        <Button 
          variant="outline" 
          onClick={toggleTheme} 
          size="icon" 
          className="bg-card/80 backdrop-blur-sm border-border/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
        >
          {theme === 'dark' ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </Button>
      </div>

      <Card className="w-full max-w-md shadow-2xl border-border/50 backdrop-blur-sm bg-card/95 relative z-10">
        <CardHeader className="space-y-6 pb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-blue-600/30 dark:shadow-blue-500/20 ring-4 ring-blue-100 dark:ring-blue-950 transition-transform duration-300 hover:scale-105">
            <Server className="w-11 h-11 text-white" />
          </div>
          <div className="text-center space-y-2">
            <CardTitle className="text-2xl">Welcome</CardTitle>
            <CardDescription className="text-base">
              Sign in to manage your container hosting platform
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="pb-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {validEmail && (
              <Alert className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/50 dark:to-emerald-950/50 border-green-300/50 dark:border-green-800/50 shadow-sm">
                <AlertCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                <AlertDescription className="text-green-700 dark:text-green-300">
                  ¡Registro exitoso! Ahora ingresa tu contraseña para continuar.
                </AlertDescription>
              </Alert>
            )}

            {error && (
              <Alert variant="destructive" className="shadow-sm">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="login-email" className="text-foreground/90">Email</Label>
              <Input
                id="login-email"
                name="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
                autoComplete="email"
                className="h-11 bg-input-background dark:bg-muted/50 border-border/50 focus:border-blue-500 dark:focus:border-blue-400 transition-all duration-200"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="login-password" className="text-foreground/90">Password</Label>
              <Input
                id="login-password"
                name="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                autoComplete="current-password"
                className="h-11 bg-input-background dark:bg-muted/50 border-border/50 focus:border-blue-500 dark:focus:border-blue-400 transition-all duration-200"
              />
            </div>

            <Button 
              type="submit" 
              className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-600/30 dark:shadow-blue-500/20 transition-all duration-300 hover:shadow-xl hover:scale-[1.02]" 
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border/50"></span>
              </div>
              <div className="relative flex justify-center">
                <span className="bg-card px-4 text-sm text-muted-foreground">or</span>
              </div>
            </div>

            <div className="text-center">
              <p className="text-muted-foreground">
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={onSwitchToRegister}
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors duration-200 inline-flex items-center gap-1 hover:gap-2"
                >
                  Sign up
                  <span className="transition-transform duration-200">→</span>
                </button>
              </p>
            </div>

          </form>
        </CardContent>
      </Card>
    </div>
  );
};
