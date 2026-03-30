from fastapi import FastAPI, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db_session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings

# Setup Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API centralizada para operaciones internas empresariales con seguridad avanzada y RBAC.",
    version="1.0.0",
    docs_url="/docs", # Consider disabling in prod depending on requirements
    redoc_url="/redoc"
)

# Bind Limiter to App
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Add Strict-Transport-Security if in production (assuming proxy handles HTTPS but adds header just in case)
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Root/Healthcheck
@app.get("/health", tags=["System"])
@limiter.limit("10/minute")
async def health_check(request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Endpoint para verificar la salud y estado de la API, incluyendo la Base de Datos.
    """
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "error"
        
    status_code = 200 if db_status == "ok" else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if db_status == "ok" else "error",
            "db_connection": db_status,
            "environment": settings.ENVIRONMENT,
            "project": settings.PROJECT_NAME
        }
    )

# TODO: Include API Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(roles_router, prefix="/api/v1")
