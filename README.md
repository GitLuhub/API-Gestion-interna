# 🏢 API Gestión Interna

![Build Status](https://img.shields.io/github/actions/workflow/status/tu-usuario/api-gestion-interna/ci.yml?branch=main)
![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-00a393.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

API de Gestión Interna lista para producción. Desarrollada en Python 3.9+ usando FastAPI y SQLAlchemy 2.0 (async). Destaca por su arquitectura limpia por capas, seguridad avanzada (HttpOnly cookies, Rate Limiting), migraciones con Alembic y despliegue dockerizado.

---

## 🎯 ¿Qué hace? (MVP)

Provee un módulo central de **Gestión de Usuarios y Roles** preparado para entornos de producción. Destaca por:

*   **Seguridad:** Autenticación de doble token (Access JWT + Refresh Token en Cookie `HttpOnly`), Rate Limiting y encriptación de contraseñas.
*   **Rendimiento:** Backend completamente asíncrono usando `asyncpg` (PostgreSQL) y FastAPI.
*   **Arquitectura Limpia:** Separación estricta por capas (Routers, Servicios, Repositorios) garantizando alta mantenibilidad.
*   **Observabilidad:** Logging estructurado con Request IDs para facilitar auditorías y debugging.

---

## 🏗️ Arquitectura y Tecnologías

*   **Framework:** FastAPI + Python 3.9+
*   **Base de Datos:** PostgreSQL 14 (Motor asíncrono)
*   **ORM y Migraciones:** SQLAlchemy 2.0 (Async) + Alembic
*   **Infraestructura:** Docker & Docker Compose (Uvicorn bajo Gunicorn)
*   **Tests:** Pytest + pytest-asyncio

---

## 🚀 Cómo arrancar (Quickstart)

Levantar la API es tan sencillo como usar Docker. No necesitas instalar dependencias de Python localmente.

### 1. Clonar y Configurar Entorno
```bash
git clone https://github.com/tu-usuario/API-Gestion-interna.git
cd API-Gestion-interna
cp .env.example .env
```

### 2. Levantar los servicios con Docker Compose
```bash
docker-compose up -d --build
```
> Esto levantará el contenedor de la API (en el puerto 8000) y la Base de Datos PostgreSQL.

### 3. Ejecutar Migraciones y Poblado Inicial (Seed)
Abre una terminal dentro del contenedor web para aplicar el esquema de base de datos e insertar los usuarios por defecto:
```bash
docker-compose exec web alembic upgrade head
docker-compose exec web python seed.py
```

---

## 🧪 Demo / Credenciales de Prueba

Una vez ejecutado el script de `seed.py`, la base de datos se poblará con datos de ejemplo. 

Puedes acceder a la **Documentación Interactiva (Swagger)** en:
👉 `http://localhost:8000/docs`

**Credenciales de acceso predeterminadas:**
*   **Email:** `admin@example.com`
*   **Password:** `Admin123!`
*   **Rol:** Administrador del Sistema

*(Con estas credenciales puedes autenticarte en el endpoint `/api/v1/auth/login` para obtener tu Token).*

---

## ✅ Ejecución de Tests

Para comprobar que todo el sistema funciona y asegurar la calidad del código, puedes correr la suite de tests (Pytest) dentro del contenedor:

```bash
docker-compose exec web pytest
```

---

## 📝 Documentación Adicional
*   Revisa el archivo [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md) para conocer el roadmap completo y las decisiones técnicas.
*   Para detalles granulares de la capa de backend, revisa los manuales ubicados en el directorio `/docs`.