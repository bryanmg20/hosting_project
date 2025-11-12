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
      setError('El nombre de usuario es requerido');
      return;
    }

    if (name.length < 3) {
      setError('El nombre de usuario debe tener al menos 3 caracteres');
      return;
    }

    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    setLoading(true);

    try {
      // API Call: POST /api/auth/register (sin autenticar automáticamente)
      await registerOnly(email, password, name);
      
      // Mostrar mensaje de éxito
      toast.success('¡Cuenta creada exitosamente!', {
        description: 'Ahora puedes iniciar sesión con tus credenciales.'
      });
      
      // Redirigir a login con el email prellenado
      onSwitchToLogin(email);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al registrarse');
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
            <CardTitle>Create your account</CardTitle>
            <CardDescription>
              Start deploying your applications in seconds
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="register-username">User</Label>
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
              />
              <p className="text-xs text-muted-foreground">
                Solo letras, números, guiones bajos (_) y guiones medios (-)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="register-email">Email</Label>
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
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="register-password">Password</Label>
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
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="register-confirm-password">Confirm Password</Label>
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
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>

            <div className="text-center pt-4 border-t">
              <p className="text-muted-foreground">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => onSwitchToLogin('')}
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Sign in
                </button>
              </p>
            </div>

          </form>
        </CardContent>
      </Card>
    </div>
  );
};
