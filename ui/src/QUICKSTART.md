# ⚡ Quick Start - Backend Real

## 🎯 TL;DR

**El frontend YA está listo para backend real con JWT.**

Solo necesitas:
1. Configurar `.env`
2. Implementar backend
3. ¡Funciona!

---

## 📋 Checklist de 3 Pasos

### 1️⃣ Frontend (YA HECHO ✅)

```bash
# Crear .env
echo "VITE_API_URL=http://localhost:3000/api" > .env

# Ejecutar frontend
npm install
npm run dev
```

✅ Frontend corriendo en `http://localhost:5173`

---

### 2️⃣ Backend (TU IMPLEMENTAS 🔧)

**Opción A: Usar ejemplos provistos**

```bash
# 1. Crear proyecto backend
mkdir hosting-backend
cd hosting-backend

# 2. Copiar código de BACKEND_EXAMPLES.md
# Implementar:
# - src/server.ts
# - src/middleware/auth.ts
# - src/routes/auth.ts
# - src/routes/projects.ts
# - src/routes/containers.ts

# 3. Instalar deps
npm install express cors jsonwebtoken bcrypt dotenv

# 4. Ejecutar
npm run dev
```

**Opción B: Tu propio backend**

Solo implementa estos endpoints (ver `MIGRATION_TO_BACKEND.md` para detalles):

```
POST   /api/auth/register
POST   /api/auth/login
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
GET    /api/containers/events (SSE, opcional)
```

✅ Backend corriendo en `http://localhost:3000`

---

### 3️⃣ Probar Integración

1. **Abrir frontend:** `http://localhost:5173`
2. **Hacer clic en "Register"**
3. **Crear cuenta:**
   - Email: `test@example.com`
   - Password: `password123`
   - Name: `Test User`
4. **Verificar que:**
   - ✅ Login funciona
   - ✅ Token se guarda en localStorage
   - ✅ Dashboard carga proyectos
   - ✅ Puedes crear proyectos
   - ✅ Puedes start/stop contenedores

---

## 🔍 Debugging

### Frontend no conecta con backend

```bash
# 1. Verificar .env
cat .env
# Debe mostrar: VITE_API_URL=http://localhost:3000/api

# 2. Reiniciar frontend después de cambiar .env
npm run dev
```

### CORS Error

```javascript
// Backend: Configurar CORS
app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}))
```

### 401 Unauthorized

```bash
# Ver token en browser console
localStorage.getItem('auth_token')

# Si es null → Login nuevamente
# Si existe → Backend no está validando correctamente
```

---

## 📚 Documentación

| Archivo | Qué Contiene |
|---------|--------------|
| `README.md` | Overview general del proyecto |
| `QUICKSTART.md` | Esta guía rápida |
| `MIGRATION_TO_BACKEND.md` | Specs completas de todos los endpoints |
| `BACKEND_EXAMPLES.md` | Código de ejemplo para implementar backend |
| `ARCHITECTURE.md` | Arquitectura técnica del sistema |
| `CHANGELOG_JWT.md` | Qué cambió en la migración a JWT |

---

## 🎯 Testing Sin Backend (Mock)

Si NO tienes backend aún, el frontend funciona en modo mock:

```bash
# NO crear .env
# O usar URL inexistente
echo "VITE_API_URL=http://mock.local/api" > .env

npm run dev
```

**Comportamiento:**
- ❌ Login/Register fallarán (error de red)
- ✅ Puedes ver la UI
- ✅ Puedes navegar entre páginas

**Para testing completo necesitas backend real.**

---

## 💡 Ejemplos de Respuestas Esperadas

### POST /api/auth/login

**Request:**
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "123",
    "email": "test@example.com",
    "name": "Test User"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "AuthError",
  "message": "Invalid email or password",
  "statusCode": 401
}
```

---

### GET /api/projects

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "projects": [
    {
      "id": "1",
      "name": "my-app",
      "status": "running",
      "url": "http://my-app.user.localhost",
      "template": "react",
      "github_url": "https://github.com/user/my-app",
      "created_at": "2025-11-08T12:00:00Z",
      "metrics": {
        "cpu": 45,
        "memory": 256,
        "requests": 1234
      }
    }
  ]
}
```

---

## ⚠️ Importante

### Variables de Entorno

**Frontend `.env`:**
```bash
VITE_API_URL=http://localhost:3000/api
```

**Backend `.env`:**
```bash
PORT=3000
JWT_SECRET=cambiar_esto_en_produccion_a_algo_super_seguro
JWT_EXPIRES_IN=7d
DATABASE_URL=postgresql://user:pass@localhost:5432/db
FRONTEND_URL=http://localhost:5173
```

### CORS

Backend DEBE permitir requests desde frontend:

```javascript
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
}))
```

### JWT Secret

**⚠️ CRÍTICO:** Cambiar `JWT_SECRET` a algo seguro:

```bash
# Generar secret seguro
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"

# Copiar output a .env
JWT_SECRET=a1b2c3d4e5f6...
```

---

## 🚀 Deploy a Producción

### Frontend

1. **Configurar variable de entorno:**
   ```bash
   VITE_API_URL=https://api.tudominio.com/api
   ```

2. **Build:**
   ```bash
   npm run build
   ```

3. **Deploy a Vercel/Netlify:**
   - Subir carpeta `dist/`
   - Configurar `VITE_API_URL` en dashboard

### Backend

1. **Deploy a Railway/Render/DigitalOcean**
2. **Configurar variables de entorno**
3. **Configurar CORS con URL de frontend en producción**
4. **Usar HTTPS obligatorio**

---

## ✅ Listo!

Con estos 3 pasos tienes:

- ✅ Frontend corriendo con UI completa
- ✅ Backend con autenticación JWT
- ✅ Integración completa frontend-backend
- ✅ Sistema real de tokens
- ✅ Manejo de errores
- ✅ Auto-logout en token expirado

**Next steps:**
- Conectar backend con Docker API
- Implementar SSE real para métricas
- Deploy a producción

---

## 📞 Ayuda

- **Error en login:** Ver `MIGRATION_TO_BACKEND.md` sección de autenticación
- **CORS issues:** Ver `BACKEND_EXAMPLES.md` sección de CORS
- **Arquitectura:** Ver `ARCHITECTURE.md`
- **Código de ejemplo:** Ver `BACKEND_EXAMPLES.md`

**Todo está listo para producción. Solo implementa el backend!** 🎉
