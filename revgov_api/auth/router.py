from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from auth import schemas, models, service
from core.database import get_db
from core.dependencies import get_current_active_user
from core.security import create_access_token, create_refresh_token
from core.config import settings
from core.constants import (
    TOKEN_TYPE,
    TOKEN_TYPE_REFRESH,
    ERR_INVALID_TOKEN,
    MODULES_LIST,
    ROLE_SUPER_ADMIN,
    ROLE_CEO,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

limiter = Limiter(key_func=get_remote_address)


@router.post("/tokens", response_model=schemas.TokenResponse)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    login_req: schemas.LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await service.authenticate_user(db, login_req)
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    # Fetch the assigned role automatically from the user profile
    logged_in_role = user.roles[0].name if user.roles else "unknown"
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": TOKEN_TYPE,
        "message": f"You have successfully logged in as {logged_in_role}.",
        "user": user,
    }


@router.post("/refresh", response_model=schemas.TokenResponse)
@limiter.limit("10/minute")
async def refresh_access_token(
    request: Request,
    req: schemas.RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ERR_INVALID_TOKEN,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            req.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != TOKEN_TYPE_REFRESH:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception

    access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    logged_in_role = user.roles[0].name if user.roles else "unknown"
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": TOKEN_TYPE,
        "message": f"Token refreshed successfully for {logged_in_role}.",
        "user": user,
    }


@router.get("/users/me", response_model=schemas.UserMeResponse)
async def read_users_me(
    request: Request,
    current_user: models.User = Depends(get_current_active_user),
):
    user_roles = [role.name for role in current_user.roles]
    active_role = request.headers.get("X-Active-Role")

    # If X-Active-Role is passed and valid, evaluate module access only for that role
    if active_role and active_role in user_roles:
        eval_roles = [role for role in current_user.roles if role.name == active_role]
        eval_role_names = [active_role]
    else:
        eval_roles = current_user.roles
        eval_role_names = user_roles

    accessible_modules = []

    if ROLE_SUPER_ADMIN in eval_role_names or ROLE_CEO in eval_role_names:
        accessible_modules = MODULES_LIST
    else:
        for module in MODULES_LIST:
            has_access = False
            for role in eval_roles:
                if role.permissions is not None:
                    access = role.permissions.get(module, "—")
                    if access != "—":
                        has_access = True
                        break
            if has_access:
                accessible_modules.append(module)

    setattr(current_user, "accessible_modules", accessible_modules)
    return current_user


@router.put("/passwords", response_model=schemas.MessageResponse)
async def change_password(
    req: schemas.ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    return await service.change_password(db=db, user=current_user, req=req)


@router.get("/roles", response_model=List[schemas.RoleResponse])
async def get_roles(db: AsyncSession = Depends(get_db)):
    return await service.get_all_roles(db=db)


@router.post("/teams-sso", response_model=schemas.TokenResponse)
async def teams_sso_login(
    req: schemas.TeamsSSORequest, db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user via Microsoft Teams / Entra ID token or authorization code.
    Verifies user exists in database and issues standard access/refresh tokens.
    """
    user = await service.authenticate_teams_sso(
        db,
        token=req.token,
        code=req.code,
        redirect_uri=req.redirect_uri,
        code_verifier=req.code_verifier,
    )
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    logged_in_role = user.roles[0].name if user.roles else "Employee"
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": TOKEN_TYPE,
        "message": f"Login successful via Microsoft Teams as {logged_in_role}.",
        "user": user,
    }


@router.get("/sso-config")
async def get_sso_config(db: AsyncSession = Depends(get_db)):
    """Public endpoint returning enabled SSO providers for the login page."""
    from modules.administration import models as admin_models
    res_cfg = await db.execute(
        select(admin_models.MicrosoftEntraConfig)
        .where(admin_models.MicrosoftEntraConfig.is_active.is_(True))
        .order_by(admin_models.MicrosoftEntraConfig.id.desc())
    )
    entra = res_cfg.scalars().first()
    return {
        "teams": {
            "enabled": bool(entra and entra.is_active),
            "tenant_id": entra.tenant_id if entra else None,
            "client_id": entra.client_id if entra else None,
        },
        "slack": {
            "enabled": False,
        },
    }
