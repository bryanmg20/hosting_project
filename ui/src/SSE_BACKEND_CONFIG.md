# Configuración SSE - Backend Real

## 🎯 Cambios Realizados

El sistema SSE ha sido completamente configurado para funcionar con un backend real. Los cambios incluyen:

### ✅ Archivos Modificados:

1. **`/lib/sse-context.tsx`**
   - ✅ Activada implementación real de SSE (líneas 84-113 descomentadas)
   - ✅ Eliminada conexión mock
   - ✅ Eliminada inicialización de proyectos fake
   - ✅ Sistema de notificaciones mejorado para eventos SSE
   - ✅ Manejo de errores y reconexión automática

2. **`/components/hosting/ProjectCard.tsx`**
   - ✅ Ahora consume `containerStatus` del SSE en lugar de `project.status`
   - ✅ Usa `containerMetrics` del SSE para métricas en tiempo real
   - ✅ Fallback a datos de la API si SSE no tiene datos aún

3. **`/components/pages/DashboardPage.tsx`**
   - ✅ Sincroniza estados iniciales con SSE al cargar proyectos
   - ✅ Eliminado refetch completo después de start/stop
   - ✅ Actualización optimista de estados (deploying → running via SSE)

4. **`/components/pages/ProjectDetailsPage.tsx`**
   - ✅ Usa `currentStatus` del SSE para alertas y badges
   - ✅ Eliminado refetch después de acciones
   - ✅ Updates automáticos vía SSE

---

## 🔌 Configuración del Backend

### 1. Variable de Entorno

Configurar la URL del backend en `.env`:

```bash
VITE_API_URL=http://localhost:3000/api
# O en producción:
# VITE_API_URL=https://api.tudominio.com/api
```

### 2. Endpoint SSE Requerido

El backend debe implementar:

**Endpoint:** `GET /api/containers/events?token={jwt}`

**Headers:**
- `Content-Type: text/event-stream`
- `Cache-Control: no-cache`
- `Connection: keep-alive`

**Autenticación:**
- Token JWT pasado como query param: `?token={jwt}`
- EventSource no soporta headers personalizados nativamente

---

## 📡 Eventos SSE que el Backend Debe Enviar

### 1. `metrics_updated` - Métricas de contenedores

Enviar cada 3-5 segundos para contenedores en estado `running`:

```javascript
event: metrics_updated
data: {"projectId":"proj-123","metrics":{"cpu":45.2,"memory":256,"requests":1523,"uptime":"2h 15m","lastActivity":"2025-11-09T10:30:00Z"}}
```

**Estructura de datos:**
```typescript
{
  projectId: string;
  metrics: {
    cpu: number;          // Porcentaje 0-100
    memory: number;       // MB usados
    requests: number;     // Total de requests
    uptime: string;       // Formato: "2h 15m"
    lastActivity: string; // ISO 8601 timestamp
  }
}
```

---

### 2. `container_status_changed` - Cambio de estado

Enviar cuando cambia el estado de un contenedor:

```javascript
event: container_status_changed
data: {"projectId":"proj-123","status":"running","notify":true}
```

**Estructura de datos:**
```typescript
{
  projectId: string;
  status: 'running' | 'stopped' | 'deploying' | 'error' | 'inactive';
  notify?: boolean; // Si es false, no muestra toast (opcional)
}
```

**Estados posibles:**
- `running` - Contenedor activo
- `stopped` - Contenedor detenido
- `deploying` - Desplegando/iniciando
- `error` - Error en deployment
- `inactive` - Pausado por inactividad

**Cuándo enviar:**
- Después de `POST /api/containers/:id/start` → `deploying` → `running`
- Después de `POST /api/containers/:id/stop` → `stopped`
- Cuando auto-shutdown detecta inactividad → `inactive`
- Si falla el deployment → `error`

---

### 3. `auto_shutdown` - Pausa automática

Enviar cuando un contenedor se pausa por inactividad:

```javascript
event: auto_shutdown
data: {"projectId":"proj-123","projectName":"Mi Proyecto"}
```

**Estructura de datos:**
```typescript
{
  projectId: string;
  projectName?: string; // Opcional, para mostrar en notificación
}
```

**Cuándo enviar:**
- Cuando el sistema detecta X minutos sin tráfico
- Antes de pausar el contenedor para ahorrar recursos

---

## 🔄 Flujo Completo Start/Stop

### Al presionar START:

1. **Frontend:**
   ```
   updateContainerStatus('proj-123', 'deploying') // Optimista
   POST /api/containers/proj-123/start
   ```

2. **Backend:**
   ```
   Recibe POST /api/containers/proj-123/start
   → Inicia contenedor Docker
   → Envía SSE: container_status_changed { status: 'deploying' }
   → Contenedor listo
   → Envía SSE: container_status_changed { status: 'running' }
   → Cada 4s envía: metrics_updated { cpu, memory, requests... }
   ```

3. **Frontend:**
   ```
   SSE actualiza containerStatus['proj-123'] = 'running'
   → ProjectCard se re-renderiza automáticamente
   → Muestra badge verde "Running"
   → Muestra botón "Stop" en lugar de "Start"
   ```

### Al presionar STOP:

1. **Frontend:**
   ```
   POST /api/containers/proj-123/stop
   ```

2. **Backend:**
   ```
   Recibe POST /api/containers/proj-123/stop
   → Detiene contenedor
   → Envía SSE: container_status_changed { status: 'stopped' }
   → Deja de enviar metrics_updated
   ```

3. **Frontend:**
   ```
   SSE actualiza containerStatus['proj-123'] = 'stopped'
   → ProjectCard se re-renderiza
   → Badge gris "Stopped"
   → Muestra botón "Start"
   ```

---

## 🧪 Testing sin Backend

Si necesitas probar el frontend sin backend real:

1. Descomentar las simulaciones en `/lib/sse-context.tsx` líneas 156-184
2. Descomentar la inicialización mock de proyectos (opcional)
3. El SSE seguirá usando mock data en lugar de EventSource real

---

## 🚀 Ventajas del Nuevo Sistema

### Antes (con refetch):
```
Usuario presiona Start
→ POST /api/containers/:id/start (200ms)
→ GET /api/projects (300ms)
→ Total: ~500ms + re-render completo
```

### Ahora (con SSE):
```
Usuario presiona Start
→ POST /api/containers/:id/start (200ms)
→ SSE envía evento (0ms, ya conectado)
→ Total: ~200ms + re-render solo del componente afectado
```

**Beneficios:**
- ✅ 60% más rápido
- ✅ Updates automáticos sin polling
- ✅ Menos carga en el servidor
- ✅ UI reactiva en tiempo real
- ✅ Notificaciones de auto-shutdown
- ✅ Métricas en vivo sin refetch

---

## 📊 Estructura de Datos Completa

### Estado Inicial (al cargar proyectos):

```typescript
// GET /api/projects → Response
{
  projects: [
    {
      id: "proj-123",
      name: "Mi App",
      status: "running",
      url: "https://mi-app.com",
      template: "react",
      github_url: "https://github.com/user/repo",
      created_at: "2025-11-01T10:00:00Z",
      metrics: {
        cpu: 45,
        memory: 256,
        requests: 1000
      }
    }
  ]
}
```

### Sincronización SSE:

```typescript
// Frontend sincroniza:
containerStatus['proj-123'] = 'running'
containerMetrics['proj-123'] = { cpu: 45, memory: 256, requests: 1000, uptime: '2h', lastActivity: '...' }

// SSE toma el control:
Cada 4s → metrics_updated actualiza containerMetrics
En cambios → container_status_changed actualiza containerStatus
```

---

## ⚠️ Notas Importantes

1. **EventSource y CORS:**
   - El backend debe tener CORS configurado para el origen del frontend
   - Incluir `Access-Control-Allow-Origin` en headers SSE

2. **Reconexión Automática:**
   - Si se pierde conexión SSE, reintenta cada 3 segundos
   - Solo si el usuario está autenticado (tiene token JWT)

3. **Desconexión al Logout:**
   - El SSE se desconecta automáticamente cuando `getAuthToken()` retorna null
   - Al hacer login, se reconecta automáticamente

4. **Estados Optimistas:**
   - Start/Stop usan estados optimistas para feedback inmediato
   - Si la API falla, el estado se revierte
   - SSE siempre envía el estado real como confirmación

5. **Fallback a API:**
   - Si SSE no tiene datos de un proyecto, usa `project.status` y `project.metrics`
   - Esto permite que la UI funcione incluso si SSE está desconectado

---

## ✅ Checklist de Implementación Backend

- [ ] Endpoint `/api/containers/events?token={jwt}` con SSE
- [ ] Autenticación por query param `?token=...`
- [ ] Headers SSE correctos (`text/event-stream`, `no-cache`)
- [ ] Evento `metrics_updated` cada 3-5s para contenedores running
- [ ] Evento `container_status_changed` en cambios de estado
- [ ] Evento `auto_shutdown` cuando se pausa por inactividad
- [ ] Enviar `container_status_changed` después de POST start/stop
- [ ] CORS configurado para el origen del frontend
- [ ] Manejo de desconexión de clientes
- [ ] Logging de conexiones SSE activas

---

## 🎉 Sistema Listo

El frontend está **100% preparado** para conectarse con el backend real. Solo necesitas:

1. Configurar `VITE_API_URL` en `.env`
2. Implementar el endpoint SSE en el backend siguiendo esta documentación
3. El sistema funcionará automáticamente

**Sin cambios adicionales en el código del frontend.**
