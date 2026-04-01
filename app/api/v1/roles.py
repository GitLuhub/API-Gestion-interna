from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from app.schemas.role import RolePublic, RoleCreate, RoleUpdate
from app.schemas.auth import Message
from app.schemas.user import UserPublic
from app.schemas.response import StandardResponse, PaginationMeta
from app.services.role import RoleService
from app.api.deps import get_role_service, role_required, get_current_user, admin_required

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/", response_model=StandardResponse[List[RolePublic]])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    role_service: RoleService = Depends(get_role_service),
    current_user: UserPublic = Depends(role_required(["Admin"]))
):
    roles, total = await role_service.get_all_roles(skip=skip, limit=limit)
    return StandardResponse(
        data=roles,
        meta=PaginationMeta(total=total, skip=skip, limit=limit)
    )

@router.post("/", response_model=StandardResponse[RolePublic], status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    current_user: UserPublic = Depends(role_required(["Admin"]))
):
    role = await role_service.create_role(role_in, actor_id=current_user.id)
    return StandardResponse(data=role, message="Role created successfully")

@router.get("/{role_id}", response_model=StandardResponse[RolePublic])
async def get_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    current_user: UserPublic = Depends(role_required(["Admin"]))
):
    role = await role_service.get_role_by_id(role_id)
    return StandardResponse(data=role)

@router.post("/{role_id}/assign/{user_id}", response_model=Message)
async def assign_role(
    role_id: UUID,
    user_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    current_user: UserPublic = Depends(admin_required())
):
    await role_service.assign_role_to_user(user_id, role_id, actor_id=current_user.id)
    return Message(detail="Rol asignado exitosamente")

@router.delete("/{role_id}/revoke/{user_id}", response_model=Message)
async def revoke_role(
    role_id: UUID,
    user_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    current_user: UserPublic = Depends(role_required(["Admin"]))
):
    await role_service.revoke_role_from_user(user_id, role_id, actor_id=current_user.id)
    return Message(detail="Rol revocado exitosamente")
