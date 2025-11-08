# 📊 Sistema de Monitoreo en Tiempo Real - CloudDeploy

## 🎯 Descripción General

CloudDeploy cuenta con un sistema completo de monitoreo en tiempo real utilizando **Server-Sent Events (SSE)** que permite a los usuarios supervisar el estado de sus contenedores sin necesidad de recargar la página.

## 🔌 Conexión SSE (Simulada)

### Endpoint SSE
```
GET /api/containers/events → Stream de eventos de estado
```

### Ventajas de SSE vs WebSocket
- ✅ Conexión unidireccional eficiente (servidor → cliente)
- ✅ Reconexión automática integrada
- ✅ Protocolo HTTP estándar
- ✅ Menor overhead para actualizaciones en tiempo real
- ✅ Ideal para streams de datos del servidor

### Estados de Conexión SSE
- 🔵 **Conectando...** - Estableciendo conexión SSE
- ✅ **Conectado (actualizaciones automáticas)** - Stream activo recibiendo eventos
- 🔴 **Desconectado** - Sin conexión, reconectando automáticamente

## 📡 Eventos SSE

El backend envía automáticamente los siguientes eventos:

### 1. `container_status_changed`
- **Cuándo**: Estado del contenedor cambia (running ↔ stopped)
- **Datos**: `{ projectId, oldStatus, newStatus, timestamp }`
- **UI**: Actualiza badge de estado + notificación toast

### 2. `metrics_updated`
- **Cuándo**: Cada X segundos (definido por el backend internamente)
- **Datos**: `{ projectId, cpu, memory, requests, uptime }`
- **UI**: Actualiza gráficos y métricas en tiempo real

### 3. `deployment_progress`
- **Cuándo**: Durante el proceso de deployment
- **Datos**: `{ projectId, step, progress, message, level }`
- **UI**: Logs en tiempo real + barra de progreso

### 4. `auto_shutdown`
- **Cuándo**: Contenedor se pausa por inactividad
- **Datos**: `{ projectId, reason, inactiveTime }`
- **UI**: Badge cambia a "Inactive" + alerta amarilla

## 📦 Estados de Contenedores

### ✅ Running (Activo)
- Badge verde con animación pulsante
- Métricas actualizándose automáticamente vía SSE
- Botones disponibles: Stop, Refresh, Open
- Gráfico en tiempo real de CPU y Memoria

### 🟡 Deploying (Desplegando)
- Badge amarillo con spinner animado
- Logs en tiempo real vía evento `deployment_progress`
- Progress bar animada
- Auto-scroll en los logs

### 🔴 Stopped (Detenido)
- Badge gris estático
- Métricas no disponibles
- Botón disponible: Start

### ⚫ Inactive (Inactivo por inactividad)
- Badge gris con mensaje informativo
- Alert amarillo explicando el motivo (vía evento `auto_shutdown`)
- Botón disponible: Reactivate

### ❌ Error (Error de Deployment)
- Badge rojo
- Alert de error con descripción
- Logs mostrando el error
- Botón disponible: Retry

## 🔧 Componentes Implementados

### 1. SSEProvider (`/lib/sse-context.tsx`)
Context global que maneja:
- Estado de conexión SSE
- Reconexión automática
- Estados de contenedores
- Métricas en tiempo real
- Logs de deployment
- Procesamiento de eventos SSE

**Sin controles de usuario para frecuencia** - El backend decide cuándo enviar eventos.

### 2. LiveStatusBadge (`/components/hosting/LiveStatusBadge.tsx`)
- Badge animado según el estado
- Animación pulsante para estados activos (running, deploying)
- Colores dinámicos según el estado

### 3. SSEIndicator (`/components/hosting/SSEIndicator.tsx`)
- Muestra estado de conexión SSE con emojis (🔵/✅/🔴)
- Info de descripción de conexión
- Popover con información de eventos SSE
- Endpoint display: `GET /api/containers/events`

**Características:**
- No incluye controles de frecuencia (manejado internamente por el backend)
- Solo muestra estado de conexión
- Información educativa sobre tipos de eventos

### 4. LiveMetricsChart (`/components/hosting/LiveMetricsChart.tsx`)
- Cards con métricas actuales: CPU, Memoria, Requests
- Gráfico de líneas en tiempo real (recharts)
- Historial de últimos 10 puntos de datos
- Solo visible cuando el contenedor está running
- Actualizado automáticamente vía evento `metrics_updated`

### 5. LiveLogsViewer (`/components/hosting/LiveLogsViewer.tsx`)
- Visor de logs con scroll automático
- Color-coding según nivel: info, success, warning, error
- Badge "Streaming" cuando hay nuevos logs
- Timestamps para cada entrada
- Contador de entradas
- Recibe logs vía evento `deployment_progress`

## 📱 Ubicación en la UI

### Dashboard (`/components/pages/DashboardPage.tsx`)
- SSEIndicator en la parte superior
- LiveStatusBadge en cada ProjectCard
- Sin contadores de stats (eliminados)

### Project Details (`/components/pages/ProjectDetailsPage.tsx`)
- SSEIndicator en la parte superior
- Alerts según estado (inactive, error, deploying)
- LiveMetricsChart (solo si está running)
- LiveLogsViewer con logs del proyecto
- Controles mejorados con feedback visual

## 🎨 Características de UX

### Notificaciones Toast
- ✅ Conexión SSE establecida
- ⚠️ Contenedor pausado por inactividad (evento `auto_shutdown`)
- ✅ Operaciones exitosas (start, stop, delete)
- ❌ Errores de operaciones

### Auto-scroll en Logs
- Scroll automático al final cuando llegan nuevos logs
- Desactivable si el usuario hace scroll manual
- Indicador visual "Streaming" cuando hay actividad

### Animaciones
- Pulsación en badges de estado activo
- Spinner para operaciones en progreso
- Fade-in para nuevos logs
- Progress bars animadas

## 🔄 Flujo de Actualización SSE

```
1. Usuario autenticado → SSEProvider se inicializa
2. SSE conecta a GET /api/containers/events → Toast: "Conexión SSE establecida"
3. Backend envía evento metrics_updated → UI actualiza gráficos automáticamente
4. Usuario hace clic en "Start" → Backend envía deployment_progress
5. Logs aparecen en tiempo real según eventos recibidos
6. Container cambia a "running" → Evento container_status_changed
7. Métricas siguen llegando automáticamente cada X segundos (backend decide)
8. Inactividad detectada → Evento auto_shutdown + Toast + Badge "Inactive"
9. Si se pierde conexión → Reconexión automática transparente
```

## 🛠️ Simulación de Datos (Mock)

### Estructura de Eventos SSE
```typescript
// Evento: metrics_updated
{
  event: "metrics_updated",
  data: {
    projectId: string,
    cpu: number,           // 0-100%
    memory: number,        // MB
    requests: number,      // Total requests
    uptime: string,        // "2h 15m"
    lastActivity: string   // ISO timestamp
  }
}

// Evento: container_status_changed
{
  event: "container_status_changed",
  data: {
    projectId: string,
    oldStatus: ContainerStatus,
    newStatus: ContainerStatus,
    timestamp: string
  }
}

// Evento: deployment_progress
{
  event: "deployment_progress",
  data: {
    projectId: string,
    message: string,
    level: 'info' | 'success' | 'warning' | 'error',
    timestamp: string
  }
}

// Evento: auto_shutdown
{
  event: "auto_shutdown",
  data: {
    projectId: string,
    reason: string,
    inactiveTime: string
  }
}
```

## 📋 Endpoints Mock API

```typescript
GET    /api/projects              → Lista de proyectos
GET    /api/projects/:id          → Detalles de proyecto
POST   /api/containers/:id/start  → Iniciar contenedor
POST   /api/containers/:id/stop   → Detener contenedor
DELETE /api/projects/:id          → Eliminar proyecto

// SSE Endpoint
GET    /api/containers/events     → Stream SSE (text/event-stream)
```

## 🎯 Casos de Uso

1. **Monitorear despliegue**: Usuario ve logs en tiempo real vía `deployment_progress`
2. **Supervisar recursos**: Gráficos actualizados automáticamente vía `metrics_updated`
3. **Detectar problemas**: Alertas automáticas cuando llega evento `auto_shutdown`
4. **Reactivar contenedor**: Click en "Reactivate" cuando está inactive
5. **Reconexión transparente**: SSE reconecta automáticamente si se pierde conexión

## 🚀 Próximas Mejoras Posibles

- [ ] Notificaciones de escritorio usando Notifications API
- [ ] Sonido para eventos importantes
- [ ] Exportar logs a archivo
- [ ] Filtros de logs por nivel
- [ ] Métricas históricas (24h, 7d, 30d)
- [ ] Comparación entre proyectos
- [ ] Webhooks para eventos críticos
- [ ] Rate limiting indicators del backend

## 📊 Diferencias Clave: SSE vs WebSocket Anterior

| Aspecto | WebSocket (Anterior) | SSE (Actual) |
|---------|---------------------|--------------|
| Dirección | Bidireccional | Unidireccional (servidor → cliente) |
| Protocolo | ws:// | HTTP (GET) |
| Reconexión | Manual | Automática integrada |
| Complejidad | Mayor | Menor |
| Uso ideal | Chat, gaming | Streams de datos, monitoring |
| Control frecuencia | Usuario (toggle) | Backend (automático) |
| Overhead | Mayor | Menor |

---

**Nota**: Este sistema está completamente mockeado para propósitos de demostración. En producción, se conectaría a un endpoint SSE real del backend que enviaría eventos en formato `text/event-stream`.
