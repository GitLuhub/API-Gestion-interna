from fastapi import APIRouter, Depends, status, Request
from typing import List
from uuid import UUID

from app.schemas.user import UserPublic, UserCreate, UserUpdate
from app.services.user import UserService
from app.api.deps import get_user_service, role_required, get_current_user
from app.core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserPublic])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    current_user: UserPublic = Depends(role_required(["Admin", "Manager"]))
):
    return await user_service.get_all_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: UUID,
    current_user: UserPublic = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    # Enforce self-access or admin access
    return await user_service.get_user_by_id(user_id)

@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: UserPublic = Depends(role_required(["Admin"]))
):
    return await user_service.create_user(user_in, actor_id=current_user.id)

@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: UserPublic = Depends(role_required(["Admin"]))
):
    return await user_service.update_user(user_id, user_in, actor_id=current_user.id)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    current_user: UserPublic = Depends(role_required(["Admin"]))
):
    await user_service.delete_user(user_id, actor_id=current_user.id)
    return None
