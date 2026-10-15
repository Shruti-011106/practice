"""
Generic CRUD router factory.
Usage:
    router = make_router(Employee, EmployeeCreate, EmployeeUpdate, EmployeeOut, "/employees", ["HR"])
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List, Type, Callable
from pydantic import BaseModel

from app.db.session import get_db
from core.dependencies import get_current_active_user, RoleChecker


def make_router(
    model,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    out_schema: Type[BaseModel],
    prefix: str,
    tags: list,
    allowed_roles: List[str] = None,
    before_create: Callable = None,
) -> APIRouter:

    deps = [Depends(get_current_active_user)]
    if allowed_roles is not None:
        deps.append(Depends(RoleChecker(allowed_roles)))
    else:
        # Default: only super admin if no roles specified
        deps.append(Depends(RoleChecker([])))

    router = APIRouter(prefix=prefix, tags=tags, dependencies=deps)

    @router.get("/", response_model=List[out_schema])
    async def list_all(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(model))
        return result.scalars().all()

    @router.get("/{item_id}", response_model=out_schema)
    async def get_one(item_id: int, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(model).where(model.id == item_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return obj

    @router.post("/", response_model=out_schema, status_code=status.HTTP_201_CREATED)
    async def create(payload: create_schema, db: AsyncSession = Depends(get_db)):
        obj = model(**payload.model_dump())
        if before_create:
            await before_create(obj, db)
        db.add(obj)
        try:
            await db.commit()
            await db.refresh(obj)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Record already exists or violates database constraints. Please check for duplicates.")
        return obj

    @router.put("/{item_id}", response_model=out_schema)
    async def update(
        item_id: int, payload: update_schema, db: AsyncSession = Depends(get_db)
    ):
        result = await db.execute(select(model).where(model.id == item_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        for key, value in payload.model_dump().items():
            setattr(obj, key, value)
        try:
            await db.commit()
            await db.refresh(obj)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Update failed: Record already exists or violates database constraints. Please check for duplicates.")
        return obj

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete(item_id: int, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(model).where(model.id == item_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        await db.delete(obj)
        await db.commit()

    return router
