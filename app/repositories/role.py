from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.user import Role
from app.schemas.role import RoleCreate, RoleUpdate

class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(model=Role, db_session=db_session)

    async def get_by_name(self, name: str) -> Role | None:
        query = select(self.model).where(self.model.name == name)
        result = await self.db_session.execute(query)
        return result.scalars().first()
