# 📁 Estructura de Archivos - CloudDeploy

## 🎯 Overview

Sistema completamente preparado para backend real con autenticación JWT.

---

## 📂 Estructura Completa

```
CloudDeploy/
│
├── 📄 App.tsx                      # Entry point principal
│
├── 📚 Documentación
│   ├── README.md                   # Overview del proyecto
│   ├── QUICKSTART.md               # Guía rápida de 3 pasos ⭐
│   ├── MIGRATION_TO_BACKEND.md     # Specs de todos los endpoints ⭐
│   ├── BACKEND_EXAMPLES.md         # Código de ejemplo del backend ⭐
│   ├── ARCHITECTURE.md             # Arquitectura técnica del sistema
│   ├── CHANGELOG_JWT.md            # Qué cambió en la migración
│   ├── FILE_STRUCTURE.md           # Este archivo
│   ├── REAL_TIME_MONITORING.md     # Docs de SSE (legacy)
│   ├── Attributions.md             # Créditos
│   └── guidelines/
│       └── Guidelines.md           # Guías de desarrollo
│
├── ⚙️ Configuración
│   ├── .env.example                # Ejemplo de variables de entorno
│   ├── package.json                # Dependencies
│   ├── tsconfig.json               # TypeScript config
│   └── vite.config.ts              # Vite config
│
├── 🎨 Componentes
│   ├── pages/                      # Páginas principales
│   │   ├── LoginPage.tsx           # Login con JWT
│   │   ├── RegisterPage.tsx        # Registro con JWT
│   │   ├── DashboardPage.tsx       # Dashboard de proyectos
│   │   ├── CreateProjectPage.tsx   # Crear nuevo proyecto
│   │   ├── ProjectDetailsPage.tsx  # Detalles de proyecto
│   │   └── DocumentationPage.tsx   # Docs de API (no usado)
│   │
│   ├── hosting/                    # Componentes de hosting
│   │   ├── Header.tsx              # Header con logout
│   │   ├── ProjectCard.tsx         # Card de proyecto
│   │   ├── LiveMetricsChart.tsx    # Gráficos de métricas
│   │   ├── LiveStatusBadge.tsx     # Badge de estado
│   │   ├── SSEIndicator.tsx        # Indicador de conexión SSE
│   │   └── SSEEventsDemo.tsx       # Demo de eventos SSE
│   │
│   ├── ui/                         # Sistema de UI (40+ componentes)
│   │   ├── button.tsx              # Botones
│   │   ├── card.tsx                # Cards
│   │   ├── input.tsx               # Inputs
│   │   ├── badge.tsx               # Badges
│   │   ├── alert.tsx               # Alertas
│   │   ├── dialog.tsx              # Modales
│   │   ├── ... (40+ más)
│   │   └── sonner.tsx              # Toast notifications
│   │
│   └── figma/                      # Componentes protegidos
│       └── ImageWithFallback.tsx   # Helper de imágenes
│
├── 🔧 Lógica de Negocio
│   ├── lib/
│   │   │
│   │   ├── 🔐 Contextos
│   │   ├── auth-context.tsx        # Autenticación con JWT ⭐
│   │   ├── theme-context.tsx       # Modo dark/light
│   │   └── sse-context.tsx         # Real-time SSE ⭐
│   │   │
│   │   └── 📡 API Layer (NUEVO) ⭐
│   │       ├── api/
│   │       │   ├── index.ts        # Re-exports centralizados
│   │       │   │
│   │       │   ├── api-client.ts   # Cliente HTTP con auth ⭐⭐⭐
│   │       │   │   └── Features:
│   │       │   │       ├── Headers Authorization automáticos
│   │       │   │       ├── Timeout configurable
│   │       │   │       ├── Error handling centralizado
│   │       │   │       ├── Auto-logout en 401
│   │       │   │       └── Custom error class
│   │       │   │
│   │       │   ├── storage.ts      # Token & cache management ⭐
│   │       │   │   └── Functions:
│   │       │   │       ├── getAuthToken()
│   │       │   │       ├── setAuthToken()
│   │       │   │       ├── clearAuthTokens()
│   │       │   │       ├── getCachedUserData()
│   │       │   │       ├── isAuthenticated()
│   │       │   │       └── Theme helpers
│   │       │   │
│   │       │   ├── types.ts        # TypeScript interfaces ⭐
│   │       │   │   └── Types:
│   │       │   │       ├── User, Project
│   │       │   │       ├── LoginRequest/Response
│   │       │   │       ├── RegisterRequest/Response
│   │       │   │       ├── CreateProjectRequest/Response
│   │       │   │       ├── ApiError
│   │       │   │       └── All API types
│   │       │   │
│   │       │   ├── auth.ts         # Auth endpoints ⭐
│   │       │   │   └── Functions:
│   │       │   │       ├── login() → POST /api/auth/login
│   │       │   │       ├── register() → POST /api/auth/register
│   │       │   │       ├── logout() → POST /api/auth/logout
│   │       │   │       ├── getCurrentUser() → GET /api/auth/me
│   │       │   │       ├── getCachedUser() → Sync read cache
│   │       │   │       └── validateSession() → Validate token
│   │       │   │
│   │       │   ├── projects.ts     # Project endpoints ⭐
│   │       │   │   └── Functions:
│   │       │   │       ├── getProjects() → GET /api/projects
│   │       │   │       ├── createProject() → POST /api/projects
│   │       │   │       ├── getProject(id) → GET /api/projects/:id
│   │       │   │       ├── deleteProject(id) → DELETE /api/projects/:id
│   │       │   │       └── updateProjectStatus() → PATCH /api/projects/:id/status
│   │       │   │
│   │       │   └── containers.ts   # Container endpoints ⭐
│   │       │       └── Functions:
│   │       │           ├── getContainerStatus(id) → GET /api/containers/:id/status
│   │       │           ├── startContainer(id) → POST /api/containers/:id/start
│   │       │           ├── stopContainer(id) → POST /api/containers/:id/stop
│   │       │           └── restartContainer(id) → POST /api/containers/:id/restart
│   │       │
│   │       └── 📝 Nota: SSE endpoint en sse-context.tsx
│   │           └── GET /api/containers/events (preparado para real)
│   │
│   └── styles/
│       └── globals.css             # Tailwind + custom styles
│
└── 🚫 Archivos Protegidos
    └── components/figma/
        └── ImageWithFallback.tsx   # No modificar

```

---

## 🔍 Archivos Clave por Función

### 🚀 Para Empezar (Lectura Obligatoria)

1. **`QUICKSTART.md`** - Guía rápida de 3 pasos
2. **`README.md`** - Overview general
3. **`.env.example`** - Configurar variables de entorno

### 🔐 Autenticación

| Archivo | Descripción |
|---------|-------------|
| `lib/api/auth.ts` | Endpoints de login/register/logout |
| `lib/api/storage.ts` | Manejo de tokens JWT |
| `lib/auth-context.tsx` | Contexto React de autenticación |
| `components/pages/LoginPage.tsx` | UI de login |
| `components/pages/RegisterPage.tsx` | UI de registro |

### 📡 API Integration

| Archivo | Descripción |
|---------|-------------|
| `lib/api/api-client.ts` | **CORE** - Cliente HTTP con auth automático |
| `lib/api/types.ts` | Todos los tipos TypeScript |
| `lib/api/projects.ts` | Endpoints de proyectos |
| `lib/api/containers.ts` | Endpoints de contenedores |
| `lib/api/index.ts` | Re-exports para fácil import |

### 📚 Documentación para Implementar Backend

| Archivo | Para Qué |
|---------|----------|
| `MIGRATION_TO_BACKEND.md` | Specs de TODOS los endpoints |
| `BACKEND_EXAMPLES.md` | Código completo del backend |
| `ARCHITECTURE.md` | Arquitectura técnica |
| `CHANGELOG_JWT.md` | Qué cambió vs mock |

### 🎨 UI Components

| Directorio | Contenido |
|------------|-----------|
| `components/pages/` | 6 páginas principales |
| `components/hosting/` | Componentes de hosting específicos |
| `components/ui/` | 40+ componentes reutilizables |

### ⚙️ Configuración

| Archivo | Descripción |
|---------|-------------|
| `.env.example` | Template de variables de entorno |
| `package.json` | Dependencies y scripts |
| `styles/globals.css` | Estilos globales y tema |

---

## 🎯 Imports Comunes

### Para Componentes

```typescript
// Autenticación
import { useAuth } from './lib/auth-context'

// Tema
import { useTheme } from './lib/theme-context'

// SSE (real-time)
import { useSSE } from './lib/sse-context'

// API
import {
  // Auth
  login,
  register,
  logout,
  getCurrentUser,
  
  // Projects
  getProjects,
  createProject,
  deleteProject,
  
  // Containers
  startContainer,
  stopContainer,
  
  // Utils
  apiClient,
  isNetworkError,
  isUnauthorizedError,
} from './lib/api'

// Types
import type { User, Project } from './lib/api'

// UI Components
import { Button } from './components/ui/button'
import { Card } from './components/ui/card'
import { Badge } from './components/ui/badge'
// ... etc
```

### Para API Layer

```typescript
// En lib/api/*.ts
import { apiClient } from './api-client'
import { getAuthToken, setAuthToken } from './storage'
import type { User, Project, LoginResponse } from './types'
```

---

## 🔄 Flujo de Datos

### Login Flow

```
LoginPage.tsx
    ↓ (user clicks login)
lib/auth-context.tsx: login()
    ↓
lib/api/auth.ts: login()
    ↓
lib/api/api-client.ts: apiClient.post()
    ↓ (fetch con timeout)
Backend: POST /api/auth/login
    ↓ (response)
lib/api/auth.ts: setAuthToken(token)
    ↓
lib/api/storage.ts: localStorage.setItem('auth_token')
    ↓
lib/auth-context.tsx: setUser(user)
    ↓ (re-render)
App.tsx: Muestra DashboardPage
```

### Protected Request Flow

```
DashboardPage.tsx
    ↓ (useEffect)
lib/api/projects.ts: getProjects()
    ↓
lib/api/api-client.ts: apiClient.get('/projects')
    ↓
lib/api/storage.ts: getAuthToken()
    ↓ (agrega header)
Headers: { Authorization: Bearer {token} }
    ↓ (fetch)
Backend: GET /api/projects
    ↓ (validate token)
Backend: Retorna { projects: [...] }
    ↓
DashboardPage.tsx: Renderiza proyectos
```

### Token Expiration Flow

```
Any Component
    ↓
lib/api/api-client.ts: apiClient.get()
    ↓ (fetch)
Backend: 401 Unauthorized
    ↓
lib/api/api-client.ts: handleErrorResponse()
    ↓
lib/api/storage.ts: clearAuthTokens()
    ↓
lib/api/api-client.ts: dispatchEvent('auth:unauthorized')
    ↓
lib/auth-context.tsx: (listener) setUser(null)
    ↓
App.tsx: Muestra LoginPage
```

---

## 📊 localStorage Keys

```javascript
// Autenticación (IMPORTANTE)
'auth_token'       → JWT token (string)
'refresh_token'    → Refresh token (string, opcional)
'user_data'        → User cache (JSON, opcional)

// Preferencias (NO relacionado a backend)
'theme'            → 'dark' | 'light'
```

---

## 🚫 Archivos que NO Tocar

```
components/figma/ImageWithFallback.tsx   # Protegido, sistema interno
```

---

## ✅ Archivos Modificados en Migración JWT

### Reescritos Completamente ♻️

- `lib/api/storage.ts` - Solo tokens, no más mock data
- `lib/api/auth.ts` - Fetch real con JWT
- `lib/api/projects.ts` - Fetch real
- `lib/api/containers.ts` - Fetch real
- `lib/api/types.ts` - Tipos de API extendidos
- `lib/auth-context.tsx` - Validación con backend

### Nuevos Archivos ✨

- `lib/api/api-client.ts` - **CORE del sistema**
- `.env.example` - Variables de entorno
- `MIGRATION_TO_BACKEND.md` - Documentación
- `BACKEND_EXAMPLES.md` - Ejemplos de código
- `ARCHITECTURE.md` - Arquitectura
- `CHANGELOG_JWT.md` - Changelog
- `QUICKSTART.md` - Guía rápida
- `FILE_STRUCTURE.md` - Este archivo

### Actualizados Levemente 🔧

- `lib/sse-context.tsx` - Preparado para SSE real
- `lib/api/index.ts` - Nuevos exports
- `README.md` - Actualizado con info de JWT

### Sin Cambios ✅

- `App.tsx` - Compatible con nueva API
- `components/pages/*.tsx` - Compatible
- `components/hosting/*.tsx` - Compatible
- `components/ui/*.tsx` - Sin cambios
- Todos los componentes React funcionan igual

---

## 🎯 Quick Reference

### Necesito...

| Necesidad | Archivo |
|-----------|---------|
| Empezar rápido | `QUICKSTART.md` |
| Ver todos los endpoints | `MIGRATION_TO_BACKEND.md` |
| Implementar backend | `BACKEND_EXAMPLES.md` |
| Entender arquitectura | `ARCHITECTURE.md` |
| Ver qué cambió | `CHANGELOG_JWT.md` |
| Hacer login | `lib/api/auth.ts` |
| Crear proyecto | `lib/api/projects.ts` |
| Start/stop container | `lib/api/containers.ts` |
| Manejar errores | `lib/api/api-client.ts` |
| Tipos TypeScript | `lib/api/types.ts` |

---

## 📝 Notas Importantes

### ⚠️ Breaking Changes

**NO HAY breaking changes para componentes React.**

Todos los imports siguen funcionando:
```typescript
import { login, getProjects } from './lib/api'
```

Solo cambió la implementación interna (localStorage → fetch).

### ✅ Compatibilidad

- Todos los componentes funcionan sin cambios
- Misma API pública
- Solo cambia comportamiento interno
- Backend-ready desde ahora

### 🎯 Próximos Pasos

1. Leer `QUICKSTART.md`
2. Implementar backend con `BACKEND_EXAMPLES.md`
3. Configurar `.env`
4. ¡Funciona!

---

**El sistema está 100% preparado para backend real. Solo implementa los endpoints y conecta!** 🚀
