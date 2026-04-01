from fastapi import FastAPI, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid
import time
from app.core.database import get_db_session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.logging import setup_logging, request_id_ctx_var
from app.core.cache import init_redis, close_redis
import logging

# Setup Logger
setup_logging()
logger = logging.getLogger("app")

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

@app.on_event("startup")
async def startup_event():
    from app.core.cache import init_redis
    await init_redis()

@app.on_event("shutdown")
async def shutdown_event():
    from app.core.cache import close_redis
    await close_redis()

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
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_ctx_var.set(req_id)
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path}", exc_info=True)
        raise e
        
    process_time = time.time() - start_time
    logger.info(f"Handled {request.method} {request.url.path} in {process_time:.4f}s")
    
    response.headers["X-Request-ID"] = req_id
    # Add Strict-Transport-Security if in production (assuming proxy handles HTTPS but adds header just in case)
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

from app.core.exceptions import AppException
from fastapi.exceptions import RequestValidationError
from app.schemas.response import StandardResponse

# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardResponse(data=None, message=exc.detail).model_dump(exclude_none=True)
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=StandardResponse(data=exc.errors(), message="Validation Error").model_dump(exclude_none=True)
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=StandardResponse(data=None, message="Internal Server Error").model_dump(exclude_none=True)
    )

# Root/Healthcheck
@app.get("/health", tags=["System"])
@limiter.limit("10/minute")
async def health_check(request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Endpoint para verificar la salud y estado de la API, incluyendo la Base de Datos y Redis.
    """
    from app.core.cache import redis_client
    
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"

    redis_status = "ok"
    if redis_client:
        try:
            await redis_client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            redis_status = "error"
    else:
        redis_status = "not_configured"
        
    status_code = 200 if db_status == "ok" and redis_status in ("ok", "not_configured") else 503
    return JSONResponse(
        status_code=status_code,
        content=StandardResponse(
            data={
                "database": db_status, 
                "redis": redis_status,
                "environment": settings.ENVIRONMENT,
                "project": settings.PROJECT_NAME
            },
            message="System Health Status"
        ).model_dump()
    )

# TODO: Include API Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(roles_router, prefix="/api/v1")
