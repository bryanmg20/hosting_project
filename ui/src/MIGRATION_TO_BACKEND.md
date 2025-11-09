# Migración a Backend Real - Guía Completa

## 🎯 Resumen

El sistema ha sido **completamente refactorizado** para trabajar con un backend real usando tokens JWT y fetch API. Ya no usa localStorage para simular datos.

---

## 🔄 Cambios Principales

### ✅ Sistema de Autenticación con Tokens

**ANTES (Mock):**
```javascript
// Guardaba usuario completo en localStorage
localStorage.setItem('hosting_user', JSON.stringify(user))
```

**AHORA (Real):**
```javascript
// Guarda solo el token JWT
localStorage.setItem('auth_token', 'eyJhbGciOiJIUzI1...')

// Todas las requests incluyen header:
Authorization: Bearer eyJhbGciOiJIUzI1...
```

### ✅ Proyectos desde Backend

**ANTES (Mock):**
```javascript
// Leía proyectos de localStorage
const projects = JSON.parse(localStorage.getItem('hosting_projects'))
```

**AHORA (Real):**
```javascript
// Hace fetch al backend
const response = await fetch('/api/projects', {
  headers: { Authorization: `Bearer ${token}` }
})
const { projects } = await response.json()
```

---

## 📋 Endpoints del Backend

### **Autenticación**

#### POST `/api/auth/login`
**Request:**
```json
{
  "email": "usuario@example.com",
  "password": "mipassword"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "123",
    "email": "usuario@example.com",
    "name": "Usuario"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "opcional_refresh_token"
}
```

**Errores:**
- `400` - Credenciales inválidas
- `401` - Email o contraseña incorrectos

---

#### POST `/api/auth/register`
**Request:**
```json
{
  "email": "nuevo@example.com",
  "password": "password123",
  "name": "Nuevo Usuario"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "456",
    "email": "nuevo@example.com",
    "name": "Nuevo Usuario"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "opcional_refresh_token"
}
```

**Errores:**
- `400` - Datos inválidos
- `409` - Email ya registrado

---

#### GET `/api/auth/me`
**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "123",
    "email": "usuario@example.com",
    "name": "Usuario"
  }
}
```

**Errores:**
- `401` - Token inválido/expirado

---

#### POST `/api/auth/logout`
**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

### **Proyectos**

#### GET `/api/projects`
**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "projects": [
    {
      "id": "1",
      "name": "mi-portafolio",
      "status": "running",
      "url": "http://miportafolio.usuario.localhost",
      "template": "react",
      "github_url": "https://github.com/usuario/mi-portafolio",
      "created_at": "2025-11-01T10:30:00Z",
      "metrics": {
        "cpu": 45,
        "memory": 512,
        "requests": 1250
      }
    }
  ]
}
```

---

#### POST `/api/projects`
**Headers:**
```
Authorization: Bearer {token}
```

**Request:**
```json
{
  "name": "nuevo-proyecto",
  "github_url": "https://github.com/usuario/repo",
  "template": "react"
}
```

**Response (201 Created):**
```json
{
  "project": {
    "id": "789",
    "name": "nuevo-proyecto",
    "status": "deploying",
    "url": "http://nuevo-proyecto.usuario.localhost",
    "template": "react",
    "github_url": "https://github.com/usuario/repo",
    "created_at": "2025-11-08T12:00:00Z",
    "metrics": {
      "cpu": 0,
      "memory": 0,
      "requests": 0
    }
  }
}
```

**Errores:**
- `400` - Datos inválidos
- `409` - Nombre de proyecto duplicado

---

#### GET `/api/projects/:id`
**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "project": {
    "id": "1",
    "name": "mi-portafolio",
    ...
  }
}
```

**Errores:**
- `404` - Proyecto no encontrado

---

#### DELETE `/api/projects/:id`
**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "Project deleted successfully"
}
```

**Errores:**
- `404` - Proyecto no encontrado

---

#### PATCH `/api/projects/:id/status`
**Headers:**
```
Authorization: Bearer {token}
```

**Request:**
```json
{
  "status": "running"
}
```

**Response (200 OK):**
```json
{
  "project": {
    "id": "1",
    "status": "running",
    ...
  }
}
```

---

### **Contenedores**

#### GET `/api/containers/:id/status`
**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "status": "running"
}
```

---

#### POST `/api/containers/:id/start`
**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "Container started successfully"
}
```

---

#### POST `/api/containers/:id/stop`
**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "Container stopped successfully"
}
```

---

#### POST `/api/containers/:id/restart`
**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "Container restarted successfully"
}
```

---

## 🔧 Configuración

### 1. Variables de Entorno

Crear archivo `.env` en la raíz:

```bash
VITE_API_URL=http://localhost:3000/api
```

**Opciones:**
- Desarrollo: `http://localhost:3000/api`
- Producción: `https://api.tudominio.com/api`

### 2. CORS en el Backend

El backend debe permitir requests desde el frontend:

```javascript
// Express.js ejemplo
app.use(cors({
  origin: 'http://localhost:5173', // URL del frontend
  credentials: true
}))
```

---

## 🎨 Estructura de Archivos

```
lib/api/
├── api-client.ts      ← Cliente HTTP con auth automático
├── auth.ts            ← Endpoints de autenticación
├── projects.ts        ← Endpoints de proyectos
├── containers.ts      ← Endpoints de contenedores
├── storage.ts         ← Gestión de tokens en localStorage
├── types.ts           ← Tipos TypeScript
└── index.ts           ← Exports centralizados
```

---

## 🔐 Flujo de Autenticación

### 1. Login
```
Usuario → Login Form → POST /api/auth/login
                            ↓
                    { user, token }
                            ↓
        localStorage.setItem('auth_token', token)
                            ↓
                    Redirect a /dashboard
```

### 2. Request Autenticado
```
Component → getProjects() → apiClient.get('/projects')
                                    ↓
                    Headers: { Authorization: Bearer {token} }
                                    ↓
                            Backend valida token
                                    ↓
                            Response { projects }
```

### 3. Token Expirado
```
Backend → 401 Unauthorized → apiClient detecta
                                    ↓
                    clearAuthTokens()
                                    ↓
                Event('auth:unauthorized')
                                    ↓
            AuthContext → setUser(null)
                                    ↓
                Redirect a /login
```

---

## 🚀 Migración desde Mock

### Cambios Necesarios en el Backend:

#### ✅ NO requiere cambios en componentes React
Los componentes siguen usando las mismas funciones:
```javascript
import { getProjects, createProject } from './lib/api'
```

#### ✅ Solo configurar variable de entorno
```bash
VITE_API_URL=http://tu-backend.com/api
```

#### ✅ Implementar endpoints en el backend
Ver sección "Endpoints del Backend" arriba.

---

## 🧪 Testing

### Modo Mock (opcional)
Para testing sin backend real, puedes crear un mock server:

```javascript
// mock-server.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('/api/auth/login', () => {
    return HttpResponse.json({
      user: { id: '1', email: 'test@test.com', name: 'Test' },
      token: 'mock_token_123'
    })
  })
]
```

---

## ⚠️ Manejo de Errores

### Errores de Red
```javascript
try {
  await getProjects()
} catch (error) {
  if (isNetworkError(error)) {
    // Mostrar "No se puede conectar al servidor"
  }
}
```

### Token Expirado
```javascript
// Auto-manejado por apiClient
// Dispara evento 'auth:unauthorized'
// AuthContext hace auto-logout
```

### Errores del Backend
```javascript
try {
  await createProject(...)
} catch (error) {
  if (error.statusCode === 409) {
    // Proyecto duplicado
  }
}
```

---

## 📊 localStorage Actual

### Antes (Mock):
```
hosting_user       → { id, email, name }
hosting_projects   → [ {...}, {...} ]
theme              → "dark" | "light"
```

### Ahora (Real):
```
auth_token         → "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
refresh_token      → "opcional_refresh_token" (futuro)
user_data          → { id, email, name } (cache UI, opcional)
theme              → "dark" | "light"
```

---

## 🎯 Checklist de Implementación Backend

- [ ] Implementar POST `/api/auth/login`
- [ ] Implementar POST `/api/auth/register`
- [ ] Implementar GET `/api/auth/me`
- [ ] Implementar POST `/api/auth/logout`
- [ ] Implementar GET `/api/projects`
- [ ] Implementar POST `/api/projects`
- [ ] Implementar GET `/api/projects/:id`
- [ ] Implementar DELETE `/api/projects/:id`
- [ ] Implementar PATCH `/api/projects/:id/status`
- [ ] Implementar GET `/api/containers/:id/status`
- [ ] Implementar POST `/api/containers/:id/start`
- [ ] Implementar POST `/api/containers/:id/stop`
- [ ] Implementar POST `/api/containers/:id/restart`
- [ ] Configurar CORS
- [ ] Implementar middleware de autenticación JWT
- [ ] Configurar SSE para `/api/containers/events`
- [ ] Agregar validaciones de datos
- [ ] Manejar errores correctamente
- [ ] Documentar API con Swagger/OpenAPI (opcional)

---

## 📞 Soporte

Si tienes dudas sobre algún endpoint o necesitas ajustar la estructura de las responses, revisa los tipos en `/lib/api/types.ts`.

Todos los endpoints siguen el formato:
- Request: Objeto con datos necesarios
- Response: Objeto con `{ user }`, `{ project }`, `{ projects }`, etc.
- Errores: Objeto con `{ error, message, statusCode }`
