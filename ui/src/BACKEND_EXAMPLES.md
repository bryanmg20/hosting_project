# 🔧 Backend Implementation Examples

Ejemplos de implementación de los endpoints del backend usando Express.js + TypeScript.

---

## 🏗️ Setup Base

### 1. Instalar dependencias

```bash
npm install express cors jsonwebtoken bcrypt dotenv
npm install -D @types/express @types/cors @types/jsonwebtoken @types/bcrypt
```

### 2. Configuración `.env`

```bash
# Backend .env
PORT=3000
JWT_SECRET=tu_super_secreto_seguro_cambiar_en_produccion
JWT_EXPIRES_IN=7d
DATABASE_URL=postgresql://user:pass@localhost:5432/hosting_db
FRONTEND_URL=http://localhost:5173
```

### 3. Server Setup (`src/server.ts`)

```typescript
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL,
  credentials: true
}));
app.use(express.json());

// Routes
import authRoutes from './routes/auth';
import projectRoutes from './routes/projects';
import containerRoutes from './routes/containers';

app.use('/api/auth', authRoutes);
app.use('/api/projects', projectRoutes);
app.use('/api/containers', containerRoutes);

// Error handler
app.use((err: any, req: any, res: any, next: any) => {
  console.error(err);
  res.status(err.statusCode || 500).json({
    error: err.name || 'Error',
    message: err.message || 'Internal server error',
    statusCode: err.statusCode || 500
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
```

---

## 🔐 Authentication Middleware

### `src/middleware/auth.ts`

```typescript
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

interface JwtPayload {
  userId: string;
  email: string;
}

// Extender Request para incluir user
declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
    }
  }
}

export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'No token provided',
        statusCode: 401
      });
    }

    const token = authHeader.substring(7); // Remove 'Bearer '
    
    const decoded = jwt.verify(
      token,
      process.env.JWT_SECRET!
    ) as JwtPayload;
    
    req.user = decoded;
    next();
  } catch (error: any) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        error: 'TokenExpired',
        message: 'Token has expired',
        statusCode: 401
      });
    }
    
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid token',
      statusCode: 401
    });
  }
};
```

---

## 🔑 Auth Routes

### `src/routes/auth.ts`

```typescript
import express from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { authenticate } from '../middleware/auth';

const router = express.Router();

// Mock database (reemplazar con tu DB real)
interface User {
  id: string;
  email: string;
  password: string;
  name: string;
}

const users: User[] = [];

// Helper: Generar JWT
const generateToken = (userId: string, email: string): string => {
  return jwt.sign(
    { userId, email },
    process.env.JWT_SECRET!,
    { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
  );
};

// POST /api/auth/register
router.post('/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;

    // Validaciones
    if (!email || !password || !name) {
      return res.status(400).json({
        error: 'ValidationError',
        message: 'Email, password and name are required',
        statusCode: 400
      });
    }

    if (password.length < 6) {
      return res.status(400).json({
        error: 'ValidationError',
        message: 'Password must be at least 6 characters',
        statusCode: 400
      });
    }

    // Verificar si el email ya existe
    const existingUser = users.find(u => u.email === email);
    if (existingUser) {
      return res.status(409).json({
        error: 'ConflictError',
        message: 'Email already registered',
        statusCode: 409
      });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Crear usuario
    const newUser: User = {
      id: Date.now().toString(),
      email,
      password: hashedPassword,
      name
    };

    users.push(newUser);

    // Generar token
    const token = generateToken(newUser.id, newUser.email);

    // Response
    res.status(201).json({
      user: {
        id: newUser.id,
        email: newUser.email,
        name: newUser.name
      },
      token
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        error: 'ValidationError',
        message: 'Email and password are required',
        statusCode: 400
      });
    }

    // Buscar usuario
    const user = users.find(u => u.email === email);
    if (!user) {
      return res.status(401).json({
        error: 'AuthError',
        message: 'Invalid email or password',
        statusCode: 401
      });
    }

    // Verificar password
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(401).json({
        error: 'AuthError',
        message: 'Invalid email or password',
        statusCode: 401
      });
    }

    // Generar token
    const token = generateToken(user.id, user.email);

    res.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      },
      token
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// GET /api/auth/me
router.get('/me', authenticate, async (req, res) => {
  try {
    const user = users.find(u => u.id === req.user!.userId);
    
    if (!user) {
      return res.status(404).json({
        error: 'NotFound',
        message: 'User not found',
        statusCode: 404
      });
    }

    res.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// POST /api/auth/logout
router.post('/logout', authenticate, async (req, res) => {
  // En implementación con JWT stateless, logout es solo client-side
  // Opcionalmente puedes implementar blacklist de tokens
  res.json({ message: 'Logged out successfully' });
});

export default router;
```

---

## 📦 Projects Routes

### `src/routes/projects.ts`

```typescript
import express from 'express';
import { authenticate } from '../middleware/auth';

const router = express.Router();

interface Project {
  id: string;
  userId: string;
  name: string;
  status: 'running' | 'stopped' | 'deploying' | 'error';
  url: string;
  template: 'static' | 'react' | 'flask' | 'nodejs';
  github_url: string;
  created_at: string;
  metrics: {
    cpu: number;
    memory: number;
    requests: number;
  };
}

const projects: Project[] = [];

// Todos los endpoints requieren autenticación
router.use(authenticate);

// GET /api/projects
router.get('/', async (req, res) => {
  try {
    const userProjects = projects.filter(p => p.userId === req.user!.userId);
    
    res.json({
      projects: userProjects
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// POST /api/projects
router.post('/', async (req, res) => {
  try {
    const { name, github_url, template } = req.body;

    // Validaciones
    if (!name || !github_url || !template) {
      return res.status(400).json({
        error: 'ValidationError',
        message: 'Name, github_url and template are required',
        statusCode: 400
      });
    }

    // Verificar nombre duplicado para el usuario
    const existingProject = projects.find(
      p => p.userId === req.user!.userId && p.name === name
    );
    
    if (existingProject) {
      return res.status(409).json({
        error: 'ConflictError',
        message: 'Project name already exists',
        statusCode: 409
      });
    }

    // Crear proyecto
    const newProject: Project = {
      id: Date.now().toString(),
      userId: req.user!.userId,
      name,
      status: 'deploying',
      url: `http://${name}.${req.user!.email.split('@')[0]}.localhost`,
      template,
      github_url,
      created_at: new Date().toISOString(),
      metrics: {
        cpu: 0,
        memory: 0,
        requests: 0
      }
    };

    projects.push(newProject);

    // Simular deploy asíncrono (en producción: queue job, Docker API, etc.)
    setTimeout(() => {
      const project = projects.find(p => p.id === newProject.id);
      if (project) {
        project.status = 'running';
        project.metrics = {
          cpu: 10,
          memory: 128,
          requests: 0
        };
      }
    }, 5000);

    res.status(201).json({
      project: newProject
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// GET /api/projects/:id
router.get('/:id', async (req, res) => {
  try {
    const project = projects.find(
      p => p.id === req.params.id && p.userId === req.user!.userId
    );

    if (!project) {
      return res.status(404).json({
        error: 'NotFound',
        message: 'Project not found',
        statusCode: 404
      });
    }

    res.json({
      project
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// DELETE /api/projects/:id
router.delete('/:id', async (req, res) => {
  try {
    const projectIndex = projects.findIndex(
      p => p.id === req.params.id && p.userId === req.user!.userId
    );

    if (projectIndex === -1) {
      return res.status(404).json({
        error: 'NotFound',
        message: 'Project not found',
        statusCode: 404
      });
    }

    projects.splice(projectIndex, 1);

    res.json({
      message: 'Project deleted successfully'
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// PATCH /api/projects/:id/status
router.patch('/:id/status', async (req, res) => {
  try {
    const { status } = req.body;

    const project = projects.find(
      p => p.id === req.params.id && p.userId === req.user!.userId
    );

    if (!project) {
      return res.status(404).json({
        error: 'NotFound',
        message: 'Project not found',
        statusCode: 404
      });
    }

    project.status = status;

    res.json({
      project
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

export default router;
```

---

## 🐳 Containers Routes

### `src/routes/containers.ts`

```typescript
import express from 'express';
import { authenticate } from '../middleware/auth';

const router = express.Router();

// Importar projects mock (en producción sería desde DB)
import { projects } from './projects'; // Compartir estado

router.use(authenticate);

// GET /api/containers/:id/status
router.get('/:id/status', async (req, res) => {
  try {
    const project = projects.find(
      p => p.id === req.params.id && p.userId === req.user!.userId
    );

    if (!project) {
      return res.status(404).json({
        error: 'NotFound',
        message: 'Container not found',
        statusCode: 404
      });
    }

    res.json({
      status: project.status
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// POST /api/containers/:id/start
router.post('/:id/start', async (req, res) => {
  try {
    const project = projects.find(
      p => p.id === req.params.id && p.userId === req.user!.userId
    );

    if (!project) {
      return res.status(404).json({
        error: 'NotFound',
        message: 'Container not found',
        statusCode: 404
      });
    }

    // Simular start (en producción: Docker API)
    project.status = 'running';
    project.metrics = {
      cpu: 10,
      memory: 128,
      requests: 0
    };

    res.json({
      message: 'Container started successfully'
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// POST /api/containers/:id/stop
router.post('/:id/stop', async (req, res) => {
  try {
    const project = projects.find(
      p => p.id === req.params.id && p.userId === req.user!.userId
    );

    if (!project) {
      return res.status(404).json({
        error: 'NotFound',
        message: 'Container not found',
        statusCode: 404
      });
    }

    project.status = 'stopped';
    project.metrics = { cpu: 0, memory: 0, requests: 0 };

    res.json({
      message: 'Container stopped successfully'
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

// POST /api/containers/:id/restart
router.post('/:id/restart', async (req, res) => {
  try {
    const project = projects.find(
      p => p.id === req.params.id && p.userId === req.user!.userId
    );

    if (!project) {
      return res.status(404).json({
        error: 'NotFound',
        message: 'Container not found',
        statusCode: 404
      });
    }

    project.status = 'deploying';
    
    setTimeout(() => {
      project.status = 'running';
    }, 2000);

    res.json({
      message: 'Container restarted successfully'
    });
  } catch (error: any) {
    res.status(500).json({
      error: 'ServerError',
      message: error.message,
      statusCode: 500
    });
  }
});

export default router;
```

---

## 📡 SSE Endpoint

### `src/routes/containers.ts` (agregar)

```typescript
// GET /api/containers/events (SSE)
router.get('/events', authenticate, async (req, res) => {
  // Headers para SSE
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  // Función helper para enviar eventos
  const sendEvent = (event: string, data: any) => {
    res.write(`event: ${event}\n`);
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  // Enviar evento de conexión
  sendEvent('connected', { message: 'SSE connection established' });

  // Intervalo para enviar métricas
  const metricsInterval = setInterval(() => {
    const userProjects = projects.filter(p => p.userId === req.user!.userId);
    
    userProjects.forEach(project => {
      if (project.status === 'running') {
        // Actualizar métricas (mock)
        project.metrics.cpu = Math.min(100, Math.max(0, 
          project.metrics.cpu + (Math.random() - 0.5) * 10
        ));
        project.metrics.memory = Math.min(512, Math.max(50, 
          project.metrics.memory + (Math.random() - 0.5) * 20
        ));
        project.metrics.requests += Math.floor(Math.random() * 5);

        // Enviar evento
        sendEvent('metrics_updated', {
          projectId: project.id,
          metrics: project.metrics
        });
      }
    });
  }, 4000);

  // Cleanup al cerrar conexión
  req.on('close', () => {
    clearInterval(metricsInterval);
    res.end();
  });
});
```

---

## 🗄️ Database Integration (Prisma Example)

### Schema (`prisma/schema.prisma`)

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        String    @id @default(cuid())
  email     String    @unique
  password  String
  name      String
  projects  Project[]
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
}

model Project {
  id         String   @id @default(cuid())
  userId     String
  user       User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  name       String
  status     String   @default("deploying")
  url        String
  template   String
  githubUrl  String
  metricsCpu Int      @default(0)
  metricsMem Int      @default(0)
  metricsReq Int      @default(0)
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  @@unique([userId, name])
}
```

### Usage

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Crear usuario
const user = await prisma.user.create({
  data: {
    email: 'user@example.com',
    password: hashedPassword,
    name: 'User Name'
  }
});

// Obtener proyectos
const projects = await prisma.project.findMany({
  where: { userId: req.user!.userId }
});
```

---

## ✅ Testing

### Unit Test Example

```typescript
import request from 'supertest';
import app from '../src/server';

describe('Auth API', () => {
  it('should register a new user', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        password: 'password123',
        name: 'Test User'
      });

    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('token');
    expect(res.body.user.email).toBe('test@example.com');
  });

  it('should login with valid credentials', async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'password123'
      });

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('token');
  });
});
```

---

## 🚀 Quick Start

```bash
# 1. Clonar/crear proyecto backend
mkdir hosting-backend
cd hosting-backend
npm init -y

# 2. Instalar dependencias
npm install express cors jsonwebtoken bcrypt dotenv
npm install -D typescript @types/node @types/express @types/cors ts-node-dev

# 3. Configurar TypeScript
npx tsc --init

# 4. Crear archivos según ejemplos arriba

# 5. Agregar scripts a package.json
{
  "scripts": {
    "dev": "ts-node-dev --respawn src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js"
  }
}

# 6. Crear .env

# 7. Ejecutar
npm run dev
```

---

## 📝 Notas Importantes

1. **Seguridad:**
   - Los ejemplos usan arrays en memoria. En producción usa base de datos real.
   - Cambia `JWT_SECRET` a un valor seguro y aleatorio.
   - Implementa rate limiting (express-rate-limit).
   - Valida y sanitiza todos los inputs.

2. **Producción:**
   - Usa Prisma, TypeORM o similar para DB.
   - Implementa logging (Winston, Pino).
   - Agrega monitoring (Sentry, DataDog).
   - Implementa tests comprehensivos.

3. **Docker:**
   - Integra con Docker API para gestión real de contenedores.
   - Usa docker-compose para desarrollo.
   - Implementa health checks.

4. **Deployment:**
   - Deploy en Railway, Render, DigitalOcean, AWS, etc.
   - Configura variables de entorno correctamente.
   - Usa HTTPS en producción.
