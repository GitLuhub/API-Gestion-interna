from uuid import UUID
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.role import RoleCreate, RoleUpdate, RolePublic
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.user import UserRole
from app.services.audit import AuditService
from app.core.cache import get_cache, set_cache, delete_cache_pattern

class RoleService:
    def __init__(self, role_repo: RoleRepository, user_repo: UserRepository, audit_service: AuditService):
        self.role_repo = role_repo
        self.user_repo = user_repo
        self.audit_service = audit_service

    async def create_role(self, role_in: RoleCreate, actor_id: UUID | None = None) -> RolePublic:
        existing_role = await self.role_repo.get_by_name(role_in.name)
        if existing_role:
            raise BadRequestException("El rol ya existe")

        new_role = await self.role_repo.create(role_in)
        
        await self.audit_service.log_action(
            action="CREATE",
            entity="Role",
            entity_id=new_role.id,
            user_id=actor_id,
            details={"name": new_role.name}
        )
        
        await delete_cache_pattern("roles:all*")
        return RolePublic.model_validate(new_role)

    async def get_role_by_id(self, role_id: UUID) -> RolePublic:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Rol no encontrado")
        return RolePublic.model_validate(role)

    async def get_all_roles(self, skip: int = 0, limit: int = 100) -> tuple[list[RolePublic], int]:
        roles = await self.role_repo.get_all(skip=skip, limit=limit)
        total = await self.role_repo.count()
        return [RolePublic.model_validate(role) for role in roles], total

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID, actor_id: UUID | None = None) -> bool:
        user = await self.user_repo.get_with_roles(user_id)
        if not user or user.is_deleted:
            raise NotFoundException("Usuario no encontrado")

        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Rol no encontrado")

        # Check if already assigned
        if any(r.id == role_id for r in user.roles):
            raise BadRequestException("El usuario ya tiene asignado este rol")

        # Assing role
        user_role = UserRole(user_id=user.id, role_id=role.id)
        self.role_repo.db_session.add(user_role)
        
        await self.audit_service.log_action(
            action="UPDATE",
            entity="UserRole",
            entity_id=user.id,
            user_id=actor_id,
            details={"action": "assign", "role_id": str(role.id), "role_name": role.name}
        )
        
        await self.role_repo.db_session.commit()
        return True

    async def revoke_role_from_user(self, user_id: UUID, role_id: UUID, actor_id: UUID | None = None) -> bool:
        user = await self.user_repo.get_with_roles(user_id)
        if not user or user.is_deleted:
            raise NotFoundException("Usuario no encontrado")

        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Rol no encontrado")

        # Remove role
        user.roles = [r for r in user.roles if r.id != role_id]
        self.role_repo.db_session.add(user)
        
        await self.audit_service.log_action(
            action="UPDATE",
            entity="UserRole",
            entity_id=user.id,
            user_id=actor_id,
            details={"action": "revoke", "role_id": str(role.id), "role_name": role.name}
        )
        
        await self.role_repo.db_session.commit()
        return True
user.roles = [r for r in user.roles if r.id != role_id]
        self.role_repo.db_session.add(user)
        
        await self.audit_service.log_action(
            action="UPDATE",
            entity="UserRole",
            entity_id=user.id,
            user_id=actor_id,
            details={"action": "revoke", "role_id": str(role.id), "role_name": role.name}
        )
        
        await self.role_repo.db_session.commit()
        return True
