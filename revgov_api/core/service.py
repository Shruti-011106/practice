from typing import Generic, TypeVar, Type, Optional, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy.exc
from core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], load_options: Optional[List] = None):
        self.model = model
        self.load_options = load_options or []

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        query = select(self.model).filter(self.model.id == id)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        if self.load_options:
            query = query.options(*self.load_options)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType, **extra_data
    ) -> ModelType:
        from fastapi import HTTPException, status

        obj_in_data = obj_in.model_dump()
        for key, value in obj_in_data.items():
            if "Url" in type(value).__name__:
                obj_in_data[key] = str(value)
        db_obj = self.model(**obj_in_data, **extra_data)
        db.add(db_obj)
        try:
            await db.commit()
            return await self.get(db, getattr(db_obj, "id", None))
        except sqlalchemy.exc.IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Record already exists or violates database constraints. Please check for duplicates or invalid IDs.",
            )

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if "Url" in type(value).__name__:
                value = str(value)
            setattr(db_obj, field, value)
        db.add(db_obj)
        try:
            await db.commit()
            return await self.get(db, getattr(db_obj, "id", None))
        except sqlalchemy.exc.IntegrityError:
            from fastapi import HTTPException, status
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed: Record already exists or violates database constraints. Please check for duplicates or invalid IDs.",
            )

    async def delete(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
