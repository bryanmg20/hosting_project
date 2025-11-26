## Como iniciar el programa
### Para iniciar la web 
1. docker network create app-network 
2. docker-compose up

# 1. Enlace a los repositorios con los templates dockerizados funcionales.


# 2. Enlace al video en youtube de demostración mostrando:


# 3. Documento tecnico

## ARQUITECTURA CLIENTE-SERVIDOR
 ![alt text](<Diagrama_arq_PC2.jpg>)

## Descripcion de componentes

### 1. Navegador del Usuario

El navegador es donde el usuario interactúa con la aplicación. Accede a tres dominios diferentes:
ui.localhost: Es la interfaz principal donde el usuario ve el Dashboard, crea proyectos y gestiona su cuenta. Aquí se ejecuta toda la aplicación React.
api.localhost: Es el dominio por el que se comunica la UI con el backend. Todas las solicitudes de autenticación, creación de proyectos y obtención de datos pasan por este dominio.
[proj_name].user.localhost: Cada proyecto creado por el usuario tiene su propio subdominio (como "miapp.localhost"). Cuando el usuario accede a cualquiera de estos dominios, se conecta directamente al contenedor Docker específico de ese proyecto.

### 2. Nginx (Proxy Inverso)
Nginx es un servidor web que actúa como intermediario entre el navegador y los servicios internos. Sus funciones principales son:
Enrutamiento: Recibe todas las solicitudes que vienen del puerto 80 y las direcciona al servicio correcto según el dominio. Si es ui.localhost, enruta a la UI. Si es api.localhost, enruta al backend. Si es un dominio de proyecto, enruta al contenedor correspondiente.
Rate Limiting: Implementa un límite de velocidad configurado en 150 solicitudes por minuto por dirección IP. Esto protege el backend de ataques DDoS y uso abusivo.
Headers HTTP: Añade información como la dirección IP real del cliente, protocolo utilizado y configuraciones para WebSocket y SSE (Server-Sent Events).
Manejo de conexiones: Configura timeouts y buffering para mantener conexiones de larga duración como SSE activas sin interrupciones.

### 3. Frontend (UI) - Aplicación React
La interfaz de usuario es una aplicación React compilada con Vite que corre en el puerto 3000 dentro de Docker. Sus componentes principales son:
Auth Context: Este componente gestiona todo lo relacionado con autenticación. Almacena el JWT token en localStorage, mantiene los datos del usuario en memoria, maneja el login y logout, y verifica automáticamente si la sesión es válida cuando el usuario recarga la página. También emite eventos cuando el usuario se autentica para notificar a otros módulos de la aplicación.
SSE Context: Este componente gestiona la conexión con el servidor para recibir actualizaciones en tiempo real. Mantiene una conexión abierta con el endpoint /sse/events del backend que envía eventos constantemente sobre cambios en los contenedores (estado, métricas, errores). Cuando recibe estos eventos, los distribuye a los componentes que los necesitan.
Pages y Components: La aplicación tiene varias páginas diferentes. LoginPage permite al usuario iniciar sesión o cambiar a registro. RegisterPage permite crear una nueva cuenta. DashboardPage muestra la lista de proyectos del usuario con tarjetas mostrando nombre, estado, URL y fecha de creación. CreateProjectPage es un formulario para crear nuevos proyectos. ProjectDetailsPage muestra información detallada de un proyecto con opciones para controlarlo.

### 4. Backend (API) - Servidor Flask
El backend es un servidor Flask que corre en el puerto 5000 dentro de Docker. Gestiona toda la lógica de negocio y tiene varios módulos:
Auth Module: Maneja el registro e inicio de sesión de usuarios. Cuando alguien se registra, valida los datos, crea la cuenta en Roble Auth (servicio externo de autenticación), genera tokens JWT propios con expiración de 15 minutos para acceso y 7 días para refresh, y almacena estos tokens. Cuando alguien inicia sesión, verifica las credenciales contra Roble Auth y genera nuevamente los tokens.
Project Module: Gestiona todo lo relacionado con proyectos. Permite obtener la lista de proyectos del usuario autenticado, crear nuevos proyectos (que automáticamente crean contenedores Docker), obtener detalles de un proyecto específico y eliminar proyectos (que también elimina el contenedor Docker asociado).
Container Module: Proporciona endpoints para controlar contenedores Docker. Permite iniciar un contenedor detenido, detenerlo si está corriendo, reiniciarlo y crear nuevos contenedores. Estos endpoints están protegidos con autenticación JWT.
SSE Module: Mantiene una conexión abierta con el cliente frontend. Constantemente monitorea el estado de los contenedores Docker del usuario, obtiene métricas de uso (CPU, memoria, requests), detecta cambios de estado y envía estos eventos al cliente. El cliente recibe estos eventos y actualiza la UI en tiempo real sin necesidad de hacer polling.
Docker Service: Es un módulo que se comunica directamente con el Docker Engine. Obtiene lista de contenedores, consulta su estado actual, inicia/detiene/reinicia contenedores, crea nuevas imágenes, elimina contenedores e imágenes, y obtiene información de recursos utilizados.

### 5. Roble DB (Base de Datos)
Roble es una base de datos serverless donde se almacenan los datos de la aplicación. Tiene dos tablas principales:
Tabla user: Almacena información de los usuarios registrados. La clave primaria es el email del usuario (no puede repetirse). También guarda el nombre de usuario. Cada usuario es único en el sistema.
Tabla projects: Almacena información de los proyectos creados por usuarios. Tiene un ID auto-generado por la base de datos como clave primaria (único para cada proyecto). El email es una clave foránea que referencia al propietario del proyecto. El nombre del proyecto también debe ser único (no puede haber dos proyectos con el mismo nombre). Guarda la URL del proyecto (generada automáticamente del nombre), la URL del repositorio GitHub de donde se descarga el código, y la fecha de creación del proyecto.

### 6. Docker Engine
Es el motor de contenedores que ejecuta y gestiona todos los contenedores de los proyectos de usuarios. El backend se comunica con Docker Engine usando su API para:
-	Crear nuevas imágenes descargando código de GitHub
-	Crear contenedores basados en esas imágenes
-	Iniciar, detener y reiniciar contenedores
-	Monitorear el estado y recursos de cada contenedor
-	Eliminar contenedores e imágenes cuando se elimina un proyecto
-	Obtener logs de los contenedores para debugging
Docker utiliza la configuración definida en docker-compose.yml para saber cómo ejecutar cada servicio (UI, Backend, Nginx).

## Flujo de trabajo

### 1. Autenticación
Registro/Login → Usuario se autentica en /auth/register o /auth/login
JWT Tokens → Backend genera tokens de acceso (15 min) y refresh (7 días)
Protected Routes → Todas las rutas de proyectos requieren JWT válido

### 2. Gestión de Proyectos
Usuario
GET /projects → Ver lista de proyectos
POST /projects → Crear nuevo proyecto
GET /projects/:id → Ver detalles del proyecto
DELETE /projects/:id → Eliminar proyecto

### 3. Gestión de Contenedores
Una vez creado un proyecto, se pueden manejar contenedores Docker:
POST /containers/:id/start → Iniciar contenedor
POST /containers/:id/stop → Detener contenedor
POST /containers/:id/restart → Reiniciar
POST /containers/:id/create → Crear contenedor

### 4. Monitoreo en Tiempo Real (Server-Sent Events)
WebSocket alternativo: /sse/events transmite actualizaciones de estado
Métrica de contenedores en vivo en el dashboard
La UI recibe eventos en tiempo real sin polling

### 5. Routing Dinámico
Proxy: Cualquier request a un subdomain se redirige al contenedor correspondiente
Ejemplo: proyecto1.localhost → Contenedor del Proyecto 1
Flujo Típico de Usuario
Usuario se registra/inicia sesión → Obtiene JWT
Navega al Dashboard → Ve sus proyectos
Crea nuevo proyecto → Backend genera contenedor Docker
Monitorea métricas → SSE actualiza estado en tiempo real
Accede a su proyecto → Nginx lo redirige al contenedor correcto
Controla contenedor → Start/Stop/Restart según sea necesario

## FLUJO DE AUTENTICACIÓN DETALLADO

### 1. Registro (Sign Up)
Cuando un usuario accede a la página de registro, ingresa su email, contraseña y nombre. El frontend envía estos datos mediante una solicitud POST a /auth/register.
En el backend, el endpoint register() en auth_bp.py recibe la solicitud. Primero valida que los datos sean correctos usando AuthValidatorService, verificando que el email tenga formato válido, la contraseña cumpla con requisitos de seguridad y el nombre no esté vacío.
Si la validación es exitosa, se invoca AuthCoreService.process_registration(). Este servicio ejecuta un proceso de varios pasos:
-	Paso 1: Llama a login_service.signup_direct() para registrar el usuario en Roble Auth (el servicio de autenticación externo). Si esto falla, retorna un error.
-	Paso 2: Después del registro exitoso, realiza un login automático llamando a login_service.login() con las credenciales del usuario. Esto retorna un access_token y refresh_token de Roble.
-	Paso 3: Almacena estos tokens de Roble en memoria usando user_service.store_roble_tokens(). Estos tokens se usan posteriormente para hacer llamadas autorizadas a la base de datos Roble.
-	Paso 4: Crea el usuario en la tabla de usuarios de Roble DB llamando user_service.create_user(), insertando el email, nombre y otros datos iniciales.
-	Paso 5: Genera los JWT tokens propios de la aplicación usando create_access_token() con expiración de 15 minutos y create_refresh_token() con expiración de 7 días. Incluye claims adicionales como el nombre y email del usuario.
La respuesta contiene los tokens JWT, email, nombre y un array vacío de contenedores. El frontend recibe esta respuesta y almacena los tokens en localStorage. También guarda los datos del usuario en un cache local para acceso inmediato. Se emite un evento auth:login que notifica a otros componentes que el usuario se ha autenticado, especialmente al sistema de SSE para que inicie la conexión.

### 2. Login
El flujo de login es similar pero más corto. El usuario envía email y contraseña a /auth/login. El backend valida los datos y luego llama a AuthCoreService.process_login().
Este servicio llama directamente a login_service.login() para autenticar con Roble. Si las credenciales son inválidas, retorna un error 401. Si son correctas, obtiene los tokens de Roble y los almacena igual que en el registro.
Luego obtiene los datos del usuario desde la base de datos usando user_service.get_user_data_with_retry(). Genera nuevamente los JWT tokens con los datos actualizados y retorna la respuesta al frontend.
El frontend nuevamente almacena los tokens en localStorage y cachea los datos del usuario.

### 3. Acceso Protegido a Endpoints
Todos los endpoints protegidos como /projects utilizan el decorador @jwt_required(). Este decorador valida automáticamente que exista un token JWT válido en el header Authorization: Bearer <token>.
Si el token es válido, el decorador permite que la función continúe. Si es inválido o ha expirado, retorna un error 401. Dentro de la función, se puede obtener la identidad del usuario (su email) usando get_jwt_identity() y los claims adicionales usando get_jwt().

### 4. Refresh Token
Cuando el access token está a punto de expirar (después de 15 minutos), el cliente puede usar el refresh token para obtener un nuevo access token sin que el usuario tenga que iniciar sesión de nuevo.
Se envía una solicitud POST a /auth/refresh con el refresh token. El backend valida que el refresh token sea válido (tiene 7 días de duración). Si es válido, genera un nuevo access token con los mismos claims y lo retorna.

### 5. Logout
Al hacer logout, se envía una solicitud POST a /auth/logout con el JWT token actual. El backend valida el token, obtiene el email del usuario y llama a user_service.clear_user_tokens() para limpiar los tokens almacenados en memoria. El frontend elimina los tokens de localStorage y redirige al usuario a la página de login.

## FLUJO DE GESTIÓN DE PROYECTOS DETALLADO

### Base de Datos - Estructura
La aplicación utiliza Roble DB, una base de datos serverless con dos tablas principales. La tabla users almacena email (clave primaria), username. La tabla projects almacena un id auto-generado como clave primaria, email del propietario como clave foránea, nombre del proyecto (único), URL, URL de GitHub, fecha de creación y estado del proyecto.

### 1. Crear un Proyecto
El usuario accede a la página de creación de proyectos (CreateProjectPage.tsx) e ingresa el nombre del proyecto y la URL de su repositorio en GitHub. El frontend envía estos datos mediante POST a /projects incluyendo el JWT token en el header.
En el backend, el endpoint create_project() primero valida que el JWT sea válido usando @jwt_required(). Extrae el email del usuario de la identidad del token y el nombre completo de los claims.
Luego valida los datos del proyecto usando validate_create_project_data(), verificando que el nombre no esté vacío, que la URL de GitHub sea válida y que no falten campos requeridos.
Después, construye la estructura del proyecto usando create_new_project_data(). Esto genera una URL única para el proyecto combinando el nombre y el usuario, como "miapp.alvaro.localhost". Agrega también la fecha y hora actual en formato ISO.
Invoca project_service.create_project() con todos los datos. Este servicio primero obtiene un token de acceso válido de Roble usando get_valid_access_token(). Luego hace una solicitud POST a la API de Roble DB al endpoint /insert con la tabla "projects" y los datos del nuevo proyecto.
Roble DB inserta el proyecto y retorna la respuesta incluyendo el id auto-generado del proyecto. Si hay un error como un nombre duplicado, retorna un mensaje de error indicando que el proyecto ya existe.
El backend retorna la respuesta al frontend, que actualiza la lista de proyectos en el Dashboard automáticamente. El usuario puede ver su nuevo proyecto inmediatamente.

### 2. Obtener Lista de Proyectos
Cuando el usuario accede al Dashboard, se ejecuta una solicitud GET a /projects con el JWT token. El backend valida el token, extrae el email del usuario y llama a project_service.get_user_projects() pasando el email.
Este servicio obtiene un token válido de Roble y hace una solicitud GET a la API de Roble DB con un filtro que especifica la tabla "projects" y un filtro por email del usuario. Esto asegura que cada usuario solo vea sus propios proyectos.
Roble DB retorna un array de todos los proyectos del usuario. El backend procesa esta lista llamando a format_project_list(), que itera sobre cada proyecto y llama a format_project_response() para formatear cada uno.
En la formatación, se extrae el nombre del contenedor de la URL del proyecto y se llama a get_real_container_status() para obtener el estado actual del contenedor Docker. Esto asegura que la UI siempre muestre el estado real, no solo lo almacenado en la base de datos.
Se agrega también información de métricas iniciales (CPU, memoria, requests en cero). El backend retorna la lista completa al frontend, que renderiza cada proyecto como una tarjeta en el Dashboard mostrando nombre, estado, URL y fecha de creación.

### 3. Obtener Proyecto Específico
Cuando el usuario hace clic en un proyecto para ver sus detalles, se envía una solicitud GET a /projects/<project_id>. El backend valida el JWT, obtiene el email y llama a project_service.get_project_by_id() pasando el email y el id del proyecto.
Este servicio obtiene un token válido de Roble y hace una solicitud GET a /read en Roble DB filtrando por el id del proyecto. Esto retorna los detalles completos del proyecto.
El backend valida que el email del proyecto coincida con el email del usuario que hace la solicitud, asegurando que nadie pueda acceder a proyectos que no le pertenecen.
Luego formatea la respuesta agregando el estado actual del contenedor y retorna los detalles al frontend, que renderiza la página de detalles del proyecto.

### 4. Eliminar un Proyecto
Cuando el usuario decide eliminar un proyecto, se envía una solicitud DELETE a /projects/<project_id>. El backend valida el JWT y el acceso del usuario al proyecto.
Luego busca la entrada en el cache de nombres de contenedores usando el id del proyecto. Obtiene el nombre del contenedor (o lo genera por defecto si no está en cache).
Hace una llamada al cliente Docker para listar todos los contenedores con ese nombre. Si encuentra el contenedor, verifica si está ejecutándose. Si está corriendo, lo detiene con un timeout de 10 segundos. Luego elimina el contenedor de Docker.
Obtiene el id de la imagen Docker del contenedor y la elimina también de Docker de forma forzada.
Finalmente, hace una solicitud DELETE a la API de Roble DB para eliminar el registro del proyecto de la tabla projects.
El frontend recibe la confirmación de eliminación y refresca la lista de proyectos en el Dashboard, removiendo el proyecto de la vista.

### 5. Relación entre Proyectos y Contenedores Docker
Cada proyecto corresponde a un contenedor Docker. Cuando se crea un proyecto, el backend no solo inserta un registro en la base de datos sino que también se supone que debe construir y ejecutar un contenedor Docker (aunque el código actual parece incompleto en esta parte).
La URL del proyecto, como "nombre_proyecto.user.localhost", se usa para enrutar solicitudes HTTP hacia el contenedor específico. Cuando alguien accede a esa URL, Nginx intercepta la solicitud y la redirige a un endpoint del backend, el backend toma ese url y con el redirige al contenedor correspondiente.
El estado del proyecto en la UI siempre refleja el estado real del contenedor Docker, no solo lo almacenado en base de datos. El sistema consulta Docker constantemente para saber si el contenedor está corriendo, detenido u otro estado.
Estructura de los Tokens JWT
El access token es un JWT que contiene la identidad del usuario (su email), el nombre como claim personalizado, el email como otro claim, el tipo de token como "access" y una fecha de expiración configurada para 15 minutos después de la emisión.
El refresh token también es un JWT pero con expiración más larga de 7 días. Solo contiene la identidad del usuario y el tipo de token como "refresh".
Ambos tokens se firman usando una clave secreta configurada en variables de entorno. El cliente incluye el access token en cada solicitud protegida en el header Authorization con el formato "Bearer <token>".

## Almacenamiento en el Frontend

El frontend almacena los tokens en localStorage del navegador en tres claves: auth_token contiene el access token, refresh_token contiene el refresh token, y cached_user contiene un objeto JSON con email, nombre y array de contenedores del usuario.
Este cache local permite que la UI cargue inmediatamente sin esperar al backend. Cuando el usuario recarga la página, la interfaz muestra los datos cacheados mientras simultáneamente valida la sesión con el backend. Si el token ha expirado, se intenta refrescarlo. Si el refresh también falla, se limpia el cache y se redirige al usuario a login.

## Flujo Completo desde la Perspectiva del Usuario Final
El usuario abre la aplicación. El AuthProvider se inicializa y primero intenta cargar datos del cache en localStorage. Si encuentra un usuario cacheado, lo establece inmediatamente sin bloquear la UI.
Simultáneamente, el backend valida si el JWT es aún válido haciendo una solicitud GET a /auth/me. Si el token es válido, actualiza los datos del usuario. Si ha expirado, intenta refrescarlo con el refresh token. Si todo falla, limpia el cache y redirige a login.
Si la autenticación es exitosa, el usuario ve el Dashboard que contiene la lista de sus proyectos. Cada proyecto muestra nombre, estado actual del contenedor, URL y fecha de creación. El sistema hace una solicitud GET a /projects para obtener la lista completa.
Si el usuario quiere crear un proyecto, accede al formulario de creación, ingresa nombre y URL de GitHub, y hace submit. El frontend envía POST a /projects. El backend crea el registro en la base de datos y el contenedor Docker. La lista se actualiza automáticamente.
Si el usuario hace clic en un proyecto, se muestra la página de detalles con opciones para iniciar, detener o reiniciar el contenedor. También puede ver el estado en tiempo real gracias al sistema SSE.
Si el usuario quiere eliminar un proyecto, hace clic en delete, se detiene el contenedor Docker, se elimina de Docker, se elimina el registro de la base de datos y la UI se actualiza removiendo el proyecto.
Cuando el usuario decide salir, hace logout y sus tokens se limpian de localStorage, su sesión se cierra en el backend, y se redirige a la página de login.

