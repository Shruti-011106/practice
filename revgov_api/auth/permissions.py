from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import models
from auth.users import check_admin_or_ceo
from core.database import get_db
from core.constants import MODULES_LIST, get_default_permissions_for_role, ROLE_SUPER_ADMIN, ROLE_CEO

router = APIRouter()


async def fetch_matrix(db: AsyncSession):
    # Helper to fetch current matrix
    result = await db.execute(select(models.Role).order_by(models.Role.id))
    roles = result.scalars().all()
    matrix = {}
    for role in roles:
        matrix[role.name] = role.permissions or {}
        
    # Generate the complete nested tree structure for the UI to render checkboxes
    full_structure = get_default_permissions_for_role(ROLE_SUPER_ADMIN)
    
    return {
        "roles": matrix, 
        "modules": MODULES_LIST,
        "structure": full_structure
    }


@router.get("")
async def get_permissions_matrix(
    db: AsyncSession = Depends(get_db), _=Depends(check_admin_or_ceo)
):
    return await fetch_matrix(db)



@router.put("")
async def save_permissions_matrix(
    payload: dict[str, dict[str, Any]],
    db: AsyncSession = Depends(get_db),
    _=Depends(check_admin_or_ceo),
):
    # payload is: { "Role Name": { "module_slug": { "permission": "...", "children": ... }, ... }, ... }
    for role_name, perms in payload.items():
        if role_name == ROLE_SUPER_ADMIN:
            continue # Ignore attempts to modify Super Admin role instead of throwing an error
            
        result = await db.execute(
            select(models.Role).where(models.Role.name == role_name)
        )
        role = result.scalar_one_or_none()
        if role:
            # We must assign a new copy of the dict to trigger SQLAlchemy change tracking
            role.permissions = dict(perms)

    await db.commit()
    return await fetch_matrix(db)


@router.post("/reset")
async def reset_permissions_matrix(
    db: AsyncSession = Depends(get_db), _=Depends(check_admin_or_ceo)
):
    """
    Resets the permissions matrix to default values.
    """
    result = await db.execute(select(models.Role))
    roles = result.scalars().all()

    for role in roles:
        role.permissions = get_default_permissions_for_role(role.name)

    await db.commit()
    return await fetch_matrix(db)
