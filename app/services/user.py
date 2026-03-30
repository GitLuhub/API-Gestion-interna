from uuid import UUID
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserPublic
from app.core.security import get_password_hash
from app.core.exceptions import BadRequestException, NotFoundException
from app.services.audit import AuditService
from datetime import datetime, timezone

class UserService:
    def __init__(self, user_repo: UserRepository, audit_service: AuditService):
        self.user_repo = user_repo
        self.audit_service = audit_service

    async def create_user(self, user_in: UserCreate, actor_id: UUID | None = None) -> UserPublic:
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise BadRequestException("Email ya registrado")

        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hashed_password
        del user_data["password"]

        new_user = await self.user_repo.create(user_data)
        
        await self.audit_service.log_action(
            action="CREATE",
            entity="User",
            entity_id=new_user.id,
            user_id=actor_id,
            details={"email": new_user.email}
        )
        
        return UserPublic.model_validate(new_user)

    async def get_user_by_id(self, user_id: UUID) -> UserPublic:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.is_deleted:
            raise NotFoundException("Usuario no encontrado")
        return UserPublic.model_validate(user)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UserPublic]:
        users = await self.user_repo.get_all(skip=skip, limit=limit)
        return [UserPublic.model_validate(user) for user in users if not user.is_deleted]

    async def update_user(self, user_id: UUID, user_in: UserUpdate, actor_id: UUID | None = None) -> UserPublic:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.is_deleted:
            raise NotFoundException("Usuario no encontrado")
            
        if user_in.email and user_in.email != user.email:
            existing_user = await self.user_repo.get_by_email(user_in.email)
            if existing_user:
                raise BadRequestException("Email ya registrado")

        old_data = {k: getattr(user, k) for k in user_in.model_dump(exclude_unset=True).keys()}
        updated_user = await self.user_repo.update(user, user_in)
        
        await self.audit_service.log_action(
            action="UPDATE",
            entity="User",
            entity_id=user.id,
            user_id=actor_id,
            details={"old": old_data, "new": user_in.model_dump(exclude_unset=True)}
        )
        
        return UserPublic.model_validate(updated_user)

    async def delete_user(self, user_id: UUID, actor_id: UUID | None = None) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.is_deleted:
            raise NotFoundException("Usuario no encontrado")
            
        # Soft delete
        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False
        await self.user_repo.update(user, {"is_deleted": True, "deleted_at": user.deleted_at, "is_active": False})
        
        await self.audit_service.log_action(
            action="DELETE",
            entity="User",
            entity_id=user.id,
            user_id=actor_id,
            details={"soft_delete": True}
        )
        
        return True
