from typing import Generic, TypeVar, Type, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: CreateSchemaType | dict) -> ModelType:
        obj_in_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType | dict) -> ModelType:
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> bool:
        query = delete(self.model).where(self.model.id == id)
        await self.db_session.execute(query)
        await self.db_session.commit()
        return True
