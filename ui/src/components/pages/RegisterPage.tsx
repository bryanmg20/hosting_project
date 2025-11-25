import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { Server, AlertCircle, Loader2, Moon, Sun } from 'lucide-react';
import { useAuth } from '../../lib/auth-context';
import { useTheme } from '../../lib/theme-context';
import { toast } from 'sonner';

interface RegisterPageProps {
  onSwitchToLogin: (email: string) => void;
}

export const RegisterPage: React.FC<RegisterPageProps> = ({ onSwitchToLogin }) => {
  const { registerOnly } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Validar username: solo letras, números, guiones bajos y guiones medios
  const handleUsernameChange = (value: string) => {
    // Solo permitir caracteres alfanuméricos, guiones bajos y guiones medios
    const sanitized = value.replace(/[^a-zA-Z0-9_-]/g, '');
    setName(sanitized);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Username is required');
      return;
    }

    if (name.length < 3) {
      setError('Username must be at least 3 characters long');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      // API Call: POST /api/auth/register (sin autenticar automáticamente)
      await registerOnly(email, password, name);
      
      // Mostrar mensaje de éxito
      toast.success('Account created successfully!', {
        description: 'You can now log in with your credentials.'
      });
      
      // Redirigir a login con el email prellenado
      onSwitchToLogin(email);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration error');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 -right-40 w-96 h-96 bg-indigo-400/20 dark:bg-indigo-600/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-32 -left-40 w-96 h-96 bg-blue-400/20 dark:bg-blue-600/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-400/10 dark:bg-purple-600/5 rounded-full blur-3xl"></div>
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
        <CardHeader className="space-y-6 pb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-indigo-600/30 dark:shadow-indigo-500/20 ring-4 ring-indigo-100 dark:ring-indigo-950 transition-transform duration-300 hover:scale-105">
            <Server className="w-11 h-11 text-white" />
          </div>
          <div className="text-center space-y-2">
            <CardTitle className="text-2xl">Create Your Account</CardTitle>
            <CardDescription className="text-base">
              Start deploying your applications in seconds
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="pb-8">
          <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
            {error && (
              <Alert variant="destructive" className="shadow-sm">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="register-username" className="text-foreground/90">Username</Label>
              <Input
                id="register-username"
                name="username"
                type="text"
                placeholder="john_doe"
                value={name}
                onChange={(e) => handleUsernameChange(e.target.value)}
                required
                disabled={loading}
                autoComplete="username"
                minLength={3}
                maxLength={20}
                pattern="[a-zA-Z0-9_-]+"
                title="Solo letras, números, guiones bajos (_) y guiones medios (-)"
                className="h-11 bg-input-background dark:bg-muted/50 border-border/50 focus:border-indigo-500 dark:focus:border-indigo-400 transition-all duration-200"
              />
              <p className="text-xs text-muted-foreground pl-1">
                Only letters, numbers, underscores and hyphens
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="register-email" className="text-foreground/90">Email</Label>
              <Input
                id="register-email"
                name="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
                autoComplete="email"
                className="h-11 bg-input-background dark:bg-muted/50 border-border/50 focus:border-indigo-500 dark:focus:border-indigo-400 transition-all duration-200"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="register-password" className="text-foreground/90">Password</Label>
              <Input
                id="register-password"
                name="new-password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                minLength={6}
                autoComplete="new-password"
                className="h-11 bg-input-background dark:bg-muted/50 border-border/50 focus:border-indigo-500 dark:focus:border-indigo-400 transition-all duration-200"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="register-confirm-password" className="text-foreground/90">Confirm Password</Label>
              <Input
                id="register-confirm-password"
                name="confirm-password"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={loading}
                minLength={6}
                autoComplete="new-password"
                className="h-11 bg-input-background dark:bg-muted/50 border-border/50 focus:border-indigo-500 dark:focus:border-indigo-400 transition-all duration-200"
              />
            </div>

            <Button 
              type="submit" 
              className="w-full h-11 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg shadow-indigo-600/30 dark:shadow-indigo-500/20 transition-all duration-300 hover:shadow-xl hover:scale-[1.02] mt-6" 
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
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
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => onSwitchToLogin('')}
                  className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors duration-200 inline-flex items-center gap-1 hover:gap-2"
                >
                  Sign in
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
