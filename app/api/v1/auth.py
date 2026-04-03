from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import Token, Message, LoginRequest
from app.api.deps import get_user_repository
from app.repositories.user import UserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedException
from app.core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Token)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    user = await user_repo.get_by_email_with_roles(login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise UnauthorizedException("Email o contraseña incorrectos")

    roles = [r.name for r in user.roles] if hasattr(user, 'roles') else []
    
    access_token = create_access_token({"sub": str(user.id), "roles": roles})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    # Set httpOnly cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    user_repo: UserRepository = Depends(get_user_repository)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("No refresh token provided")

    from app.core.security import verify_token
    payload = verify_token(refresh_token)
    
    user_id = payload.get("sub")
    if not user_id or payload.get("type") != "refresh":
        raise UnauthorizedException("Invalid refresh token")

    user = await user_repo.get_with_roles(user_id)
    if not user:
        raise UnauthorizedException("User not found")

    roles = [r.name for r in user.roles]
    new_access_token = create_access_token({"sub": str(user.id), "roles": roles})
    
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout", response_model=Message)
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"detail": "Successfully logged out"}
