# 🏗️ Arquitectura del Sistema - Backend Real

## 📊 Diagrama de Flujo

```
┌─────────────┐
│   Frontend  │
│  (React)    │
└──────┬──────┘
       │
       │ HTTP/SSE
       │
┌──────▼──────────────────────┐
│   API Client Layer          │
│  - Manejo de tokens         │
│  - Headers automáticos      │
│  - Error handling 401       │
│  - Timeout control          │
└──────┬──────────────────────┘
       │
       │ fetch()
       │
┌──────▼──────────────────────┐
│   Backend API               │
│  - JWT Validation           │
│  - Business Logic           │
│  - Database Access          │
│  - Container Management     │
└─────────────────────────────┘
```

---

## 🗂️ Estructura de Archivos

```
/lib/api/
│
├── api-client.ts        ← Core HTTP client
│   ├── apiClient.get()
│   ├── apiClient.post()
│   ├── apiClient.put()
│   ├── apiClient.delete()
│   ├── Error handling
│   └── Timeout control
│
├── storage.ts          ← Token & cache management
│   ├── getAuthToken()
│   ├── setAuthToken()
│   ├── clearAuthTokens()
│   ├── getCachedUserData()
│   └── isAuthenticated()
│
├── types.ts            ← TypeScript interfaces
│   ├── User
│   ├── Project
│   ├── LoginRequest/Response
│   ├── ApiError
│   └── ...
│
├── auth.ts             ← Authentication endpoints
│   ├── login()
│   ├── register()
│   ├── logout()
│   └── getCurrentUser()
│
├── projects.ts         ← Project endpoints
│   ├── getProjects()
│   ├── createProject()
│   ├── getProject()
│   ├── deleteProject()
│   └── updateProjectStatus()
│
├── containers.ts       ← Container endpoints
│   ├── getContainerStatus()
│   ├── startContainer()
│   ├── stopContainer()
│   └── restartContainer()
│
└── index.ts            ← Re-exports everything
```

---

## 🔐 Sistema de Autenticación

### 1. Login Flow

```javascript
// Frontend
login(email, password)
  ↓
POST /api/auth/login
  ↓
Backend valida credenciales
  ↓
Backend genera JWT token
  ↓
Response: { user, token }
  ↓
localStorage.setItem('auth_token', token)
  ↓
AuthContext actualiza user state
  ↓
Redirect a /dashboard
```

### 2. Authenticated Request Flow

```javascript
// Frontend
getProjects()
  ↓
apiClient.get('/projects')
  ↓
Lee token: getAuthToken()
  ↓
Agrega header: Authorization: Bearer {token}
  ↓
fetch('http://localhost:3000/api/projects', { headers })
  ↓
Backend valida JWT
  ↓
Backend procesa request
  ↓
Response: { projects: [...] }
```

### 3. Token Expiration Flow

```javascript
Request → Backend
  ↓
Backend: Token expirado
  ↓
Response: 401 Unauthorized
  ↓
apiClient detecta 401
  ↓
clearAuthTokens()
  ↓
dispatchEvent('auth:unauthorized')
  ↓
AuthContext escucha evento
  ↓
setUser(null)
  ↓
Redirect a /login
```

---

## 📦 localStorage Strategy

### Datos Guardados

```javascript
{
  // Autenticación (requerido)
  "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  
  // Refresh token (opcional, para implementación futura)
  "refresh_token": "refresh_token_string...",
  
  // Cache de usuario (opcional, solo para UI rápida)
  "user_data": {
    "id": "123",
    "email": "usuario@example.com",
    "name": "Usuario"
  },
  
  // Preferencias (no relacionado a backend)
  "theme": "dark"
}
```

### Estrategia de Cache

**user_data (cache):**
- ✅ Se guarda al login/register
- ✅ Se usa para mostrar nombre/email sin request
- ❌ NO se usa para validar sesión
- ✅ Se actualiza en cada call a `/api/auth/me`
- ✅ Se borra en logout

**auth_token (source of truth):**
- ✅ Es la única fuente de verdad de autenticación
- ✅ Se valida en cada request al backend
- ✅ Backend determina si es válido o expiró
- ✅ Frontend solo lo almacena y envía

---

## 🌐 API Client Features

### Características Principales

1. **Headers Automáticos**
   ```javascript
   // Agrega automáticamente en cada request:
   {
     'Content-Type': 'application/json',
     'Authorization': 'Bearer {token}'
   }
   ```

2. **Timeout Control**
   ```javascript
   // Timeout por defecto: 30 segundos
   // Personalizable por request
   apiClient.get('/endpoint', { timeout: 10000 })
   ```

3. **Error Handling**
   ```javascript
   try {
     await getProjects()
   } catch (error) {
     if (isNetworkError(error)) {
       // Sin conexión
     } else if (isUnauthorizedError(error)) {
       // Token expirado
     } else if (isServerError(error)) {
       // Error 500+
     }
   }
   ```

4. **Auto-logout en 401**
   ```javascript
   // Si backend devuelve 401:
   // 1. Limpia tokens
   // 2. Dispara evento global
   // 3. AuthContext hace logout automático
   ```

---

## 🔄 Real-Time Updates (SSE)

### Conexión SSE

```javascript
// Backend endpoint:
GET /api/containers/events?token={jwt}

// Frontend:
const eventSource = new EventSource(url)

// Eventos que emite el backend:
eventSource.addEventListener('metrics_updated', (event) => {
  const { projectId, metrics } = JSON.parse(event.data)
  // Actualizar estado
})

eventSource.addEventListener('container_status_changed', (event) => {
  const { projectId, status } = JSON.parse(event.data)
  // Actualizar estado
})
```

### Mock vs Real

**Mock (actual):**
- Usa `setInterval` para simular eventos
- No requiere backend
- Datos aleatorios generados localmente

**Real (implementar):**
- Descomentar código en `sse-context.tsx`
- Backend debe implementar SSE endpoint
- Token via query param (ya que EventSource no soporta headers)

---

## ⚙️ Variables de Entorno

### Configuración

```bash
# .env
VITE_API_URL=http://localhost:3000/api
```

**Valores comunes:**
- Desarrollo local: `http://localhost:3000/api`
- Backend remoto: `https://api.miapp.com/api`
- Docker compose: `http://backend:3000/api`

### Uso en código

```javascript
// api-client.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

// SSE
const sseUrl = `${API_BASE_URL}/containers/events?token=${token}`;
```

---

## 🧪 Testing Strategy

### Unit Tests

```javascript
// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ user: {...} })
  })
)

// Test login
await login('test@test.com', 'password')
expect(getAuthToken()).toBe('mock_token')
```

### Integration Tests

```javascript
// Mock Service Worker (MSW)
import { http, HttpResponse } from 'msw'

const handlers = [
  http.post('/api/auth/login', () => {
    return HttpResponse.json({
      user: { id: '1', email: 'test@test.com', name: 'Test' },
      token: 'mock_jwt_token'
    })
  })
]
```

---

## 🚀 Deployment

### Frontend

1. Configurar `VITE_API_URL` en producción
2. Build: `npm run build`
3. Deploy a static hosting (Vercel, Netlify, etc.)

### Backend Requirements

- Implementar todos los endpoints (ver `MIGRATION_TO_BACKEND.md`)
- Configurar CORS para permitir frontend
- Implementar JWT validation middleware
- Implementar SSE endpoint para real-time updates
- Base de datos para usuarios y proyectos
- Integración con Docker API para containers

### CORS Configuration

```javascript
// Express.js ejemplo
app.use(cors({
  origin: process.env.FRONTEND_URL, // URL del frontend
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
}))
```

---

## 🔍 Debugging

### Token Issues

```javascript
// Verificar si hay token
console.log(getAuthToken())

// Verificar si está autenticado
console.log(isAuthenticated())

// Ver datos de usuario en cache
console.log(getCachedUserData())
```

### Network Requests

```javascript
// apiClient ya logea errores en consola
// Para debugging detallado:
try {
  await getProjects()
} catch (error) {
  console.error('Error details:', {
    message: error.message,
    statusCode: error.statusCode,
    response: error.response
  })
}
```

### SSE Connection

```javascript
// Ver estado de conexión SSE
const { sseStatus } = useSSE()
console.log('SSE Status:', sseStatus) // 'connecting' | 'connected' | 'disconnected'
```

---

## 📝 Checklist de Migración

### Frontend (Ya hecho ✅)

- [x] Sistema de tokens en localStorage
- [x] API Client con headers automáticos
- [x] Manejo de errores 401
- [x] Auth context con validación
- [x] Todos los endpoints preparados
- [x] TypeScript types definidos
- [x] SSE preparado para real backend
- [x] Documentación completa

### Backend (Por implementar)

- [ ] POST `/api/auth/login`
- [ ] POST `/api/auth/register`
- [ ] GET `/api/auth/me`
- [ ] POST `/api/auth/logout`
- [ ] GET `/api/projects`
- [ ] POST `/api/projects`
- [ ] GET `/api/projects/:id`
- [ ] DELETE `/api/projects/:id`
- [ ] PATCH `/api/projects/:id/status`
- [ ] GET `/api/containers/:id/status`
- [ ] POST `/api/containers/:id/start`
- [ ] POST `/api/containers/:id/stop`
- [ ] POST `/api/containers/:id/restart`
- [ ] GET `/api/containers/events` (SSE)
- [ ] Middleware JWT validation
- [ ] CORS configuration
- [ ] Error handling
- [ ] Database setup

---

## 🎯 Next Steps

1. **Implementar Backend:**
   - Seguir especificaciones en `MIGRATION_TO_BACKEND.md`
   - Usar estructura de responses definida en `types.ts`

2. **Testing:**
   - Probar login/register
   - Probar CRUD de proyectos
   - Probar control de containers
   - Probar expiración de tokens

3. **SSE Real:**
   - Descomentar código en `sse-context.tsx`
   - Implementar endpoint SSE en backend
   - Probar eventos en tiempo real

4. **Production:**
   - Configurar variables de entorno
   - Deploy frontend + backend
   - Configurar CORS correctamente
   - Monitoreo y logs
