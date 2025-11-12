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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
      {/* Theme Toggle Button - Fixed Position */}
      <div className="fixed top-4 right-4">
        <Button variant="outline" onClick={toggleTheme} size="icon" className="bg-card">
          {theme === 'dark' ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </Button>
      </div>

      <Card className="w-full max-w-md">
        <CardHeader className="space-y-4">
          <div className="w-16 h-16 bg-blue-600 rounded-xl flex items-center justify-center mx-auto">
            <Server className="w-10 h-10 text-white" />
          </div>
          <div className="text-center">
            <CardTitle>Welcome to CloudDeploy</CardTitle>
            <CardDescription>
              Sign in to manage your container hosting platform
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {validEmail && (
              <Alert className="bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-900">
                <AlertCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                <AlertDescription className="text-green-800 dark:text-green-200">
                  ¡Registro exitoso! Ahora ingresa tu contraseña para continuar.
                </AlertDescription>
              </Alert>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="login-email">Email</Label>
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
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="login-password">Password</Label>
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
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>

            <div className="text-center pt-4 border-t">
              <p className="text-muted-foreground">
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={onSwitchToRegister}
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Sign up
                </button>
              </p>
            </div>

          </form>
        </CardContent>
      </Card>
    </div>
  );
};
