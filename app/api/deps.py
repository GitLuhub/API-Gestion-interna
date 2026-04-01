from fastapi import Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from uuid import UUID

from app.core.config import settings
from app.core.database import get_db_session
from app.core.security import verify_token, ALGORITHM
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.services.user import UserService
from app.services.role import RoleService
from app.services.audit import AuditService
from app.schemas.user import UserPublic

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)

async def get_role_repository(db: AsyncSession = Depends(get_db_session)) -> RoleRepository:
    return RoleRepository(db)

async def get_audit_service(db: AsyncSession = Depends(get_db_session)) -> AuditService:
    return AuditService(db)

async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    audit_service: AuditService = Depends(get_audit_service)
) -> UserService:
    return UserService(user_repo, audit_service)

async def get_role_service(
    role_repo: RoleRepository = Depends(get_role_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    audit_service: AuditService = Depends(get_audit_service)
) -> RoleService:
    return RoleService(role_repo, user_repo, audit_service)

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserPublic:
    # First, try to get the token from the Authorization header
    if not token:
        # If not, try to get it from the cookies
        token = request.cookies.get("access_token")
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
            
    if not token:
        raise UnauthorizedException("No token provided")

    payload = verify_token(token)
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise UnauthorizedException("Could not validate credentials")
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid token payload")

    user = await user_repo.get_with_roles(user_id_str)
    if user is None or user.is_deleted:
        raise UnauthorizedException("User not found or deleted")
    if not user.is_active:
        raise ForbiddenException("Inactive user")

    # In a real app we might pass the full object, or map roles manually to UserPublic if needed
    # For now, let's create a UserPublic and attach roles manually if needed by RBAC
    user_public = UserPublic.model_validate(user)
    # We can inject roles into request state for RBAC checks
    request.state.user_roles = [r.name for r in user.roles]
    return user_public

def role_required(required_roles: list[str]):
    async def role_checker(request: Request, current_user: UserPublic = Depends(get_current_user)):
        user_roles = getattr(request.state, "user_roles", [])
        if not any(role in user_roles for role in required_roles):
            raise ForbiddenException(f"User does not have required roles: {', '.join(required_roles)}")
        return current_user
    return role_checker

def admin_required():
    async def admin_checker(request: Request, current_user: UserPublic = Depends(get_current_user)):
        user_roles = getattr(request.state, "user_roles", [])
        if "Admin" not in user_roles or not getattr(current_user, "is_superuser", False):
            raise ForbiddenException("Access denied. Admin role and superuser privileges required.")
        return current_user
    return admin_checker
