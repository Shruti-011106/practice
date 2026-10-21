
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# 14/10/26
from core.dependencies import get_current_active_user

from core.database import get_db
from modules.inventory.models import InventoryItem
from modules.inventory.schemas import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
)

router = APIRouter(
    prefix="/inventory/items",
    tags=["Inventory Management"],
)


@router.post(
    "",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
):
    item = InventoryItem(**item_data.model_dump())

    db.add(item)

    try:
        await db.commit()
        await db.refresh(item)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Asset tag already exists or a database constraint was violated.",
        )

    return item


@router.put(
    "/{item_id}",
    response_model=InventoryItemResponse,
    dependencies=[Depends(get_current_active_user)],
)
async def update_inventory_item(
    item_id: int,
    item_data: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found.",
        )

    update_data = item_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(item, field, value)

    try:
        await db.commit()
        await db.refresh(item)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Asset tag already exists or a database constraint was violated.",
        )

    return item
