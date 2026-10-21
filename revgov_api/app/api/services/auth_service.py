from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
import re
from sqlalchemy.orm import selectinload

from app.db import models, schemas
from core.security import get_password_hash, verify_password
from core.constants import (
    ERR_INVALID_CREDENTIALS,
    ERR_USER_ALREADY_EXISTS,
    ERR_OLD_PASSWORD_WRONG,
    ERR_PASSWORD_SAME_AS_OLD,
    ERR_PASSWORD_MISMATCH,
    ERR_PASSWORD_WEAK,
    REGEX_PASSWORD,
    MSG_UPDATED,
)


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.email == email)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = await get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail=ERR_USER_ALREADY_EXISTS)

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=True,
    )

    # Assign single role to many-to-many relationship
    if user.role_id:
        result = await db.execute(
            select(models.Role).where(models.Role.id == user.role_id)
        )
        role = result.scalar_one_or_none()
        if role:
            db_user.roles = [role]

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, login_req: schemas.LoginRequest):
    user = await get_user_by_email(db, login_req.email)
    if not user:
        raise HTTPException(status_code=401, detail=ERR_INVALID_CREDENTIALS)
    if not verify_password(login_req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail=ERR_INVALID_CREDENTIALS)
    return user


async def change_password(
    db: AsyncSession, user: models.User, req: schemas.ChangePasswordRequest
):
    if req.new_password != req.confirm_password:
        raise HTTPException(status_code=400, detail=ERR_PASSWORD_MISMATCH)

    if not verify_password(req.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail=ERR_OLD_PASSWORD_WRONG)

    if verify_password(req.new_password, user.hashed_password):
        raise HTTPException(status_code=400, detail=ERR_PASSWORD_SAME_AS_OLD)

    if not re.match(REGEX_PASSWORD, req.new_password):
        raise HTTPException(status_code=400, detail=ERR_PASSWORD_WEAK)

    user.hashed_password = get_password_hash(req.new_password)
    await db.commit()
    return {"message": MSG_UPDATED}


async def get_all_roles(db: AsyncSession):
    result = await db.execute(select(models.Role).order_by(models.Role.id))
    return result.scalars().all()
