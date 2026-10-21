from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from sqlalchemy import select, join

from auth import models, schemas
from core.database import get_db
from core.dependencies import get_current_active_user
from core.security import get_password_hash
from core.constants import ROLE_SUPER_ADMIN, ROLE_CEO

router = APIRouter(prefix="/users", tags=["User Management"])


async def check_admin_or_ceo(user: models.User = Depends(get_current_active_user)):
    """Allow only super_admin (full) and ceo (read+write) to manage users."""
    user_roles = [role.name for role in user.roles]
    if ROLE_SUPER_ADMIN in user_roles or ROLE_CEO in user_roles:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only Super Admin or CEO can manage users.",
    )


@router.get("/", response_model=List[schemas.UserResponse])
async def list_users(db: AsyncSession = Depends(get_db), _=Depends(check_admin_or_ceo)):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .order_by(models.User.id)
    )
    return result.scalars().all()


@router.get("/by-role", response_model=List[schemas.UserResponse])
async def get_users_by_role(
    role_name: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    """Fetch all users having a specific role (Useful for UI Dropdowns)."""
    query = (
        select(models.User)
        .join(models.User.roles)
        .where(models.Role.name == role_name)
        .options(selectinload(models.User.roles))
        .order_by(models.User.id)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int, db: AsyncSession = Depends(get_db), _=Depends(check_admin_or_ceo)
):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post(
    "/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    payload: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(check_admin_or_ceo),
):
    result = await db.execute(
        select(models.User).where(models.User.email == payload.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = get_password_hash(payload.password)
    user = models.User(
        email=payload.email,
        hashed_password=hashed_password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        designation=payload.designation,
        is_active=True,
    )
    if payload.role_ids:
        role_result = await db.execute(
            select(models.Role).where(models.Role.id.in_(payload.role_ids))
        )
        roles = role_result.scalars().all()
        user.roles = list(roles)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    if payload.employee_id:
        from modules.hr.models import Employee
        emp_result = await db.execute(select(Employee).where(Employee.id == payload.employee_id))
        employee = emp_result.scalar_one_or_none()
        if employee:
            employee.user_id = user.id
            await db.commit()
    # Reload with roles for response
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.id == user.id)
    )
    user = result.scalar_one()
    return user


@router.patch("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(check_admin_or_ceo),
):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if payload.email is not None:
        email_result = await db.execute(
            select(models.User).where(
                models.User.email == payload.email, models.User.id != user_id
            )
        )
        if email_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        user.email = payload.email

    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.designation is not None:
        user.designation = payload.designation
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password is not None:
        user.hashed_password = get_password_hash(payload.password)

    if payload.role_ids is not None:
        role_result = await db.execute(
            select(models.Role).where(models.Role.id.in_(payload.role_ids))
        )
        roles = role_result.scalars().all()
        user.roles = list(roles)

    await db.commit()
    # Reload with roles for response
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.id == user_id)
    )
    return result.scalar_one()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, db: AsyncSession = Depends(get_db), _=Depends(check_admin_or_ceo)
):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        await db.delete(user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete this user because they are linked to an active Employee Profile or other records. Please unlink or delete those records first."
        )
