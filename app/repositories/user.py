from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(model=User, db_session=db_session)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        query = select(self.model).where(self.model.is_deleted == False).offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def count(self) -> int:
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model).where(self.model.is_deleted == False)
        result = await self.db_session.execute(query)
        return result.scalar_one()

    async def get_by_email(self, email: str) -> User | None:
        query = select(self.model).where(self.model.email == email, self.model.is_deleted == False)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_by_email_with_roles(self, email: str) -> User | None:
        query = select(self.model).options(selectinload(self.model.roles)).where(self.model.email == email, self.model.is_deleted == False)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_with_roles(self, user_id: str) -> User | None:
        import uuid
        try:
            uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except ValueError:
            return None
        query = select(self.model).options(selectinload(self.model.roles)).where(self.model.id == uid, self.model.is_deleted == False)
        result = await self.db_session.execute(query)
        return result.scalars().first()
