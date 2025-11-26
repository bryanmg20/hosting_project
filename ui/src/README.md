# CloudDeploy - Plataforma de Hosting en Contenedores

Una plataforma completa de hosting basada en contenedores que permite a los usuarios autenticarse y desplegar sitios web desde repositorios de GitHub usando templates predefinidos.

## 📋 Descripción del Proyecto

Esta es una **aplicación frontend completa** construida con React, TypeScript y Tailwind CSS. 

### ⚠️ Estado Actual

**El sistema está PREPARADO para backend real con autenticación JWT.**

- ✅ Sistema de tokens JWT implementado
- ✅ API Client con headers Authorization automáticos
- ✅ Manejo de errores 401 y auto-logout
- ✅ Todos los endpoints preparados con fetch real
- ✅ SSE listo para conexión real


**Para usar con backend real:**
1. Configurar `VITE_API_URL` en `.env`
2. Implementar endpoints en backend (ver `MIGRATION_TO_BACKEND.md`)
3. ¡Listo! El frontend ya está preparado.

## 🎨 Características Principales

### 1. Sistema de Autenticación
- **Login**: Autenticación con email y contraseña
- **Registro**: Creación de nuevas cuentas
- **Logout**: Cierre de sesión seguro
- **Gestión de estado**: Contexto de autenticación global

### 2. Dashboard Principal
- Vista general de todos los proyectos
- Tarjetas de proyecto con información clave:
  - Nombre del proyecto
  - Estado del contenedor (running, stopped, deploying, error)
  - URL de acceso
  - Template utilizado
  - Métricas de recursos (CPU, memoria, requests)
- Estadísticas globales:
  - Total de proyectos
  - Contenedores activos
  - Contenedores detenidos
  - Proyectos en despliegue
- Controles rápidos: Iniciar, detener, eliminar proyectos

### 3. Creación de Proyectos
- Selección de template:
  - **Static Website**: Sitios HTML/CSS/JS estáticos
  - **React Application**: Apps React con Node.js
  - **Node.js Backend**: Express, Fastify o custom Node.js
- Formulario de configuración:
  - Nombre del proyecto
  - URL del repositorio de GitHub
  - Preview de URL generada
- Proceso de deploy con:
  - Estados de loading
  - Barra de progreso
  - Estados de éxito/error
  - Redirección automática

### 4. Detalles de Proyecto
- Información completa del proyecto
- Métricas en tiempo real:
  - Uso de CPU (con barra de progreso)
  - Uso de memoria (con indicador visual)
  - Total de requests
- Controles de contenedor:
  - Iniciar contenedor
  - Detener contenedor
  - Eliminar proyecto
- Logs de deployment
- Enlaces rápidos:
  - Visitar sitio web
  - Ver en GitHub
- Estados visuales del contenedor

### 5. Documentación de API
- Referencia completa de endpoints
- Ejemplos de request/response
- Flujos de usuario documentados
- Integración con backend explicada

## 🏗️ Arquitectura de Componentes

### Páginas (`/components/pages/`)
- **LoginPage**: Pantalla de inicio de sesión
- **RegisterPage**: Pantalla de registro
- **DashboardPage**: Panel principal con lista de proyectos
- **CreateProjectPage**: Formulario de creación de proyectos
- **ProjectDetailsPage**: Vista detallada de un proyecto
- **DocumentationPage**: Documentación de API

### Componentes de Hosting (`/components/hosting/`)
- **Header**: Navegación principal y logout
- **ProjectCard**: Tarjeta de proyecto con controles

### Sistema de UI (`/components/ui/`)
Más de 40 componentes reutilizables incluyendo:
- Buttons, Cards, Alerts, Badges
- Forms (Input, Label, Select, Textarea)
- Overlays (Dialog, Sheet, Popover)
- Data Display (Tables, Charts, Progress)
- Y muchos más...

### Lógica de Negocio (`/lib/`)
- **auth-context.tsx**: Contexto de autenticación con JWT
- **theme-context.tsx**: Gestión de tema dark/light
- **sse-context.tsx**: Conexión SSE para real-time updates
- **api/**: Módulos de API (auth, projects, containers, storage)
  - `api-client.ts`: Cliente HTTP con autenticación automática
  - `auth.ts`: Endpoints de autenticación
  - `projects.ts`: Endpoints de proyectos
  - `containers.ts`: Endpoints de contenedores
  - `storage.ts`: Gestión de tokens en localStorage
  - `types.ts`: Interfaces TypeScript

## 🔌 Backend Integration

### 📖 Documentación Completa

- **`MIGRATION_TO_BACKEND.md`**: Guía completa de todos los endpoints esperados
- **`BACKEND_EXAMPLES.md`**: Ejemplos de implementación con Express.js
- **`ARCHITECTURE.md`**: Arquitectura técnica del sistema

### ⚡ Quick Start

#### 1. Configurar Variables de Entorno

```bash
# .env
VITE_API_URL=http://localhost:3000/api
```

#### 2. Backend Debe Implementar

```typescript
// Autenticación (sin token)
POST   /api/auth/register  → { user, token }
POST   /api/auth/login     → { user, token }

// Recursos (con token en Authorization header)
GET    /api/auth/me
POST   /api/auth/logout
GET    /api/projects
POST   /api/projects
GET    /api/projects/:id
DELETE /api/projects/:id
PATCH  /api/projects/:id/status
GET    /api/containers/:id/status
POST   /api/containers/:id/start
POST   /api/containers/:id/stop
POST   /api/containers/:id/restart
GET    /api/containers/events (SSE)
```

#### 3. Sistema de Autenticación

**Flujo:**
1. Login → Backend genera JWT
2. Frontend guarda en `localStorage['auth_token']`
3. Todas las requests incluyen `Authorization: Bearer {token}`
4. Backend valida token en cada request
5. Si token expira → 401 → Frontend hace auto-logout

**Estructura del Token:**
```typescript
// Response de login/register
{
  "user": {
    "id": "123",
    "email": "user@example.com",
    "name": "User Name"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 📊 Estructura de Datos

### User
```typescript
interface User {
  id: string;
  email: string;
  name: string;
}
```

### Project
```typescript
interface Project {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'deploying' | 'error';
  url: string;
  template: 'static' | 'react' | 'flask' | 'nodejs';
  github_url: string;
  created_at: string;
  metrics: {
    cpu: number;      // Porcentaje 0-100
    memory: number;   // MB
    requests: number; // Total de requests
  };
}
```

## 🎯 Flujos de Usuario

### Flow 1: Nuevo Usuario
1. Usuario accede a la página de registro
2. Completa el formulario (nombre, email, contraseña)
3. Frontend valida los datos
4. Se envía `POST /api/auth/register`
5. Backend crea la cuenta y retorna JWT
6. Frontend guarda token y usuario
7. Redirección al dashboard

### Flow 2: Deploy de Proyecto
1. Usuario hace clic en "New Project"
2. Selecciona template
3. Ingresa nombre y URL de GitHub
4. Frontend muestra preview de URL
5. Usuario hace clic en "Deploy Project"
6. Se envía `POST /api/projects`
7. Frontend muestra progreso de deployment
8. Backend clona repo, construye y despliega
9. Estado cambia a "running"
10. Usuario ve detalles del proyecto

### Flow 3: Gestión de Contenedor
1. Usuario navega a detalles del proyecto
2. Frontend carga datos con `GET /api/projects/:id`
3. Usuario hace clic en "Stop"
4. Se envía `POST /api/containers/:id/stop`
5. UI actualiza a estado "stopped"
6. Usuario hace clic en "Start"
7. Se envía `POST /api/containers/:id/start`
8. UI actualiza a estado "running"

### Flow 4: Eliminar Proyecto
1. Usuario hace clic en "Delete"
2. Frontend muestra confirmación
3. Usuario confirma
4. Se envía `DELETE /api/projects/:id`
5. Backend detiene contenedor y elimina datos
6. Frontend remueve proyecto de la lista
7. Redirección al dashboard

## 🎨 Sistema de Diseño

### Paleta de Colores

#### Colores Principales
- **Azul Tecnológico**: `#2563eb` - Confianza y profesionalismo
- **Índigo**: `#4f46e5` - Acento secundario

#### Colores de Estado
- **Verde**: `#10b981` - Éxito, running
- **Rojo**: `#ef4444` - Error, danger
- **Amarillo**: `#f59e0b` - Advertencia, deploying
- **Gris**: `#6b7280` - Stopped, neutral

#### Colores de Templates
- **Static**: Azul `#3b82f6`
- **React**: Cyan `#06b6d4`
- **Node.js**: Verde `#10b981`
- **Flask**: Púrpura `#a855f7`

### Tipografía
- Sistema de fuentes sans-serif modernas
- Jerarquía clara: h1, h2, h3, h4, p, label
- Tamaños predefinidos en `globals.css`

### Componentes Base

#### Botones
- **Primary**: Acción principal (azul)
- **Secondary**: Acción secundaria (gris claro)
- **Outline**: Borde con fondo transparente
- **Destructive**: Acciones peligrosas (rojo)
- **Ghost**: Sin fondo

#### Badges
- Estados de contenedor con colores distintivos
- Templates con colores de categoría
- Bordes y fondos personalizables

#### Cards
- Sombra suave en hover
- Bordes redondeados
- Padding consistente

## 📱 Diseño Responsive

### Breakpoints
- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px+

### Adaptaciones
- Grid de proyectos: 1 columna (mobile) → 2 columnas (tablet) → 3 columnas (desktop)
- Estadísticas: Stack vertical (mobile) → Grid (desktop)
- Navegación: Iconos compactos (mobile) → Texto completo (desktop)

## 🚀 Cómo Ejecutar

Esta aplicación está construida para Figma Make y se ejecuta automáticamente en el entorno.

### Para desarrollo local:
```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev
```

## 🔐 Consideraciones de Seguridad

### Frontend (Implementado ✅)

- ✅ Solo guarda tokens JWT en localStorage (no contraseñas)
- ✅ Auto-logout en token expirado (401)
- ✅ Timeout de requests (30s por defecto)
- ✅ Headers Authorization en todas las requests autenticadas
- ✅ Validación de inputs en formularios

### Backend (Por Implementar 🔧)

⚠️ **IMPORTANTE**: El backend debe implementar:

1. **JWT Validation**: Validar firma y expiración en cada request
2. **HTTPS**: Solo producción con SSL/TLS
3. **CORS**: Configurar origins permitidos
4. **Rate Limiting**: Prevenir abuso de API
5. **Input Validation**: Sanitizar y validar todos los inputs
6. **Secrets Management**: Variables de entorno para JWT_SECRET
7. **Password Hashing**: bcrypt con salt rounds >= 10
8. **SQL Injection Prevention**: Usar ORMs o prepared statements
9. **No PII Collection**: No recolectar datos personales sin consentimiento

## 📚 Tecnologías Utilizadas

- **React 18**: Framework UI
- **TypeScript**: Type safety
- **Tailwind CSS 4.0**: Styling
- **Lucide React**: Iconografía
- **Sonner**: Notificaciones toast
- **Recharts**: Gráficos (disponible si se necesita)
- **React Hook Form**: Formularios avanzados

## 📖 Documentación Adicional

Para más información sobre la integración con backend, consulta la página de "API Documentation" dentro de la aplicación.

## 🎯 Estados de UI Implementados

### Loading States
- ✅ Carga inicial de autenticación
- ✅ Carga de proyectos
- ✅ Deployment en progreso
- ✅ Acciones de contenedor (start/stop)

### Empty States
- ✅ Dashboard sin proyectos
- ✅ Mensaje motivacional para crear primer proyecto

### Success States
- ✅ Deploy exitoso
- ✅ Contenedor iniciado
- ✅ Proyecto eliminado

### Error States
- ✅ Error de autenticación
- ✅ Error al cargar proyectos
- ✅ Error de deployment
- ✅ Error de conexión

## 🔄 Estado del Proyecto

### ✅ Completado

- ✅ Sistema de autenticación completo (login/register/logout)
- ✅ Dashboard con gestión de proyectos
- ✅ Creación de proyectos con templates
- ✅ Detalles de proyecto con métricas
- ✅ Control de contenedores (start/stop/delete)
- ✅ SSE para actualizaciones en tiempo real
- ✅ Modo dark/light persistente
- ✅ Diseño responsive mobile-first
- ✅ **Migración completa a backend real con JWT** ⭐

### 💡 Features Futuras (Sugerencias)

1. **Historial de deployments** con rollback capability
2. **Variables de entorno** por proyecto
3. **Dominios personalizados**
4. **Dashboard de billing y uso**
5. **GitHub OAuth** integration
6. **Email notifications** de eventos importantes
7. **Team collaboration** y permisos
8. **CI/CD pipelines** configurables
9. **Auto-scaling** de contenedores
10. **Monitoring avanzado** con alertas
