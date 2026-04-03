# Guía para Levantar y Probar el Backend (API de Gestión Interna)

Este documento detalla los pasos exactos para inicializar el proyecto desde cero utilizando Docker, ejecutar las migraciones de base de datos, poblar datos iniciales y probar los endpoints a través de la interfaz interactiva.

## Requisitos Previos
- Docker y Docker Compose instalados en tu sistema.
- Puertos disponibles: `8001` (API), `5433` (PostgreSQL) y `6380` (Redis).

---

## Paso 1: Levantar los contenedores (Docker)

Asegúrate de estar en el directorio raíz del proyecto (`/home/devx/Documentos/Proyectos/API-Gestion-interna`) y ejecuta:

```bash
# Detiene contenedores antiguos y reconstruye la imagen de la API
docker-compose down
docker-compose up --build -d
```

Esto levantará 3 servicios en segundo plano (`-d`):
1. **db:** PostgreSQL en el puerto `5433`.
2. **redis:** Caché Redis en el puerto `6380`.
3. **api:** La aplicación FastAPI corriendo bajo Gunicorn en el puerto `8001`.

---

## Paso 2: Ejecutar las Migraciones y Poblado Inicial (Seed)

Para crear las tablas en la base de datos y generar al usuario administrador, ejecuta estos dos comandos *dentro* del contenedor de la API:

```bash
# 1. Aplica las migraciones de base de datos (crea tablas y columnas)
docker-compose exec api alembic upgrade head

# 2. Ejecuta el seed para crear los roles y el usuario "Admin"
docker-compose exec api python seed.py
```

*Nota: El script creará los roles ("Admin", "Manager", "User") y un usuario administrador por defecto con:*
- **Email:** `admin@example.com`
- **Contraseña:** `admin123`

---

## Paso 3: Probar la API usando Swagger UI

FastAPI proporciona una interfaz gráfica interactiva (Swagger) para probar todos los endpoints sin necesidad de herramientas externas como Postman.

1. Abre tu navegador web y ve a: **http://localhost:8001/docs**
2. **Verificar el Healthcheck:**
   - Busca el endpoint `GET /health` (en la sección *System*).
   - Haz clic en *Try it out* y luego en *Execute*.
   - Deberías recibir una respuesta HTTP 200 indicando que tanto la base de datos como Redis están "ok".
3. **Iniciar Sesión (Login):**
   - Ve a la parte superior de la página y haz clic en el botón verde **"Authorize"**.
   - Ingresa las credenciales del seed:
     - **Username:** `admin@example.com`
     - **Password:** `admin123`
   - Haz clic en *Authorize* y luego en *Close*. (Esto inyecta automáticamente el token Bearer en las cabeceras de tus futuras peticiones).
4. **Probar Endpoints Protegidos:**
   - Ahora puedes probar endpoints como `GET /users/` o `GET /roles/`.
   - Haz clic en *Try it out* -> *Execute* y verás la respuesta paginada con la nueva estructura estándar (`data`, `meta`).

---

## Paso 4 (Opcional): Ver los Logs Estructurados en JSON

Para comprobar cómo se ven los nuevos logs profesionales configurados para observabilidad, puedes inspeccionar el contenedor en tiempo real:

```bash
docker logs -f api_gestion_interna_app
```

Verás que cada petición que hagas en Swagger genera una línea de log en formato JSON en la consola, conteniendo el `request_id`, nivel, mensaje y timestamp, lo cual es ideal para indexar en herramientas de monitoreo en producción.
