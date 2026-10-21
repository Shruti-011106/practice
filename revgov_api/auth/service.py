from typing import Optional
import re
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from auth import models, schemas
from core.security import get_password_hash, verify_password
from core.constants import (
    ERR_INVALID_CREDENTIALS,
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


async def authenticate_teams_sso(
    db: AsyncSession,
    token: Optional[str] = None,
    code: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    code_verifier: Optional[str] = None,
) -> models.User:
    """
    Authenticates an employee using their verified Microsoft authorization code or token.
    Exchanges code for access token via Microsoft OAuth if code is provided (with PKCE verifier support),
    validates the identity with Microsoft Graph / claims,
    and matches against the organization's synced database.
    """
    import httpx
    import time
    from jose import jwt
    from modules.administration import models as admin_models

    res_cfg = await db.execute(
        select(admin_models.MicrosoftEntraConfig)
        .where(admin_models.MicrosoftEntraConfig.is_active.is_(True))
        .order_by(admin_models.MicrosoftEntraConfig.id.desc())
    )
    config = res_cfg.scalars().first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Microsoft Teams integration is not configured on this server. Please contact your administrator.",
        )

    clean_token = token.strip() if token else ""

    if code and code.strip():
        token_url = f"https://login.microsoftonline.com/{config.tenant_id}/oauth2/v2.0/token"
        token_data = {
            "client_id": config.client_id,
            "grant_type": "authorization_code",
            "code": code.strip(),
            "redirect_uri": redirect_uri or "http://localhost:5173/",
        }
        if code_verifier and code_verifier.strip():
            token_data["code_verifier"] = code_verifier.strip()
        elif config.client_secret:
            token_data["client_secret"] = config.client_secret

        async with httpx.AsyncClient(timeout=10.0) as client:
            code_resp = await client.post(token_url, data=token_data)
            if code_resp.status_code != 200:
                err_data = (
                    code_resp.json()
                    if code_resp.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                err_msg = err_data.get("error_description", err_data.get("error", code_resp.text))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Microsoft authorization failed: {err_msg}",
                )
            code_json = code_resp.json()
            clean_token = code_json.get("access_token") or code_json.get("id_token") or ""

    if not clean_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: A valid Microsoft token or authorization code is required. Please sign in via Microsoft Teams.",
        )

    email = ""

    # Attempt 1: Microsoft Graph /me
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            me_resp = await client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {clean_token}"},
            )
            if me_resp.status_code == 200:
                me_data = me_resp.json()
                email = (
                    me_data.get("mail") or me_data.get("userPrincipalName") or ""
                ).strip().lower()
    except Exception:
        pass

    # Attempt 2: Decode JWT claims
    if not email:
        try:
            claims = jwt.get_unverified_claims(clean_token)
            exp = claims.get("exp")
            if exp and time.time() > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Your Microsoft session has expired. Please sign in again.",
                )
            tid = claims.get("tid")
            if tid and config.tenant_id and tid.lower() != config.tenant_id.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You do not belong to this organization's Microsoft 365 tenant.",
                )
            email = (
                claims.get("preferred_username")
                or claims.get("email")
                or claims.get("upn")
                or ""
            ).strip().lower()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to decode Microsoft identity token: {str(e)}",
            )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to determine user email from Microsoft Teams token.",
        )

    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account '{email}' is authenticated with Microsoft, but does not exist in the RevGov system. Please ask an administrator to synchronize users.",     )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your RevGov account has been deactivated. Please contact your administrator.",
        )

    return user
