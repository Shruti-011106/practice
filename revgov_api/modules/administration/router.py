import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import get_current_active_user, RoleChecker
from core.constants import ROLE_SUPER_ADMIN, ROLE_CEO
from . import schemas, service

router = APIRouter(prefix="/administration", tags=["Administration"])

ALLOWED_IMAGE_EXTENSIONS = {".png", ".svg", ".jpg", ".jpeg", ".webp"}
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB limit


def _save_logo_file(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in upload.",
        )

    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image format '{ext}'. Allowed formats: PNG, SVG, JPG, JPEG, WEBP.",
        )

    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 1MB limit.",
        )

    upload_dir = os.path.join("uploads", "logos")
    os.makedirs(upload_dir, exist_ok=True)

    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(upload_dir, unique_filename).replace("\\", "/")

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path


@router.get(
    "/org-settings",
    response_model=List[schemas.OrgSettingOut],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def list_org_settings(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await service.org_setting_service.get_all(db, skip=skip, limit=limit)


@router.get(
    "/org-settings/{setting_id}",
    response_model=schemas.OrgSettingOut,
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def get_org_setting(setting_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.org_setting_service.get(db, setting_id)
    if not obj:
        raise HTTPException(status_code=404, detail="OrgSetting not found")
    return obj


@router.get(
    "/org-settings/{setting_id}/logo",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def get_org_setting_logo(setting_id: int, db: AsyncSession = Depends(get_db)):
    """Fetch/download organization logo file by OrgSetting ID from database."""
    obj = await service.org_setting_service.get(db, setting_id)
    if not obj:
        raise HTTPException(status_code=404, detail="OrgSetting not found")

    if not obj.company_logo:
        raise HTTPException(status_code=404, detail="No logo found for this organization setting")

    if not os.path.exists(obj.company_logo):
        raise HTTPException(status_code=404, detail="Logo file not found on server disk")

    return FileResponse(obj.company_logo)


@router.post(
    "/org-settings",
    response_model=schemas.OrgSettingOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def create_org_setting(
    organization_name: str = Form(...),
    admin_email: str = Form(...),
    legal_name: Optional[str] = Form(None),
    alias_name: Optional[str] = Form(None),
    primary_domain: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    company_size: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    support_email: Optional[str] = Form(None),
    billing_contact_email: Optional[str] = Form(None),
    company_logo: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    logo_path = None
    if company_logo is not None and company_logo.filename:
        logo_path = _save_logo_file(company_logo)

    payload = schemas.OrgSettingCreate(
        organization_name=organization_name,
        legal_name=legal_name,
        alias_name=alias_name,
        primary_domain=primary_domain,
        industry=industry,
        company_size=company_size,
        country=country,
        company_logo=logo_path,
        admin_email=admin_email,
        support_email=support_email,
        billing_contact_email=billing_contact_email,
    )
    return await service.org_setting_service.create(db, payload)


@router.put(
    "/org-settings/{setting_id}",
    response_model=schemas.OrgSettingOut,
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def update_org_setting(
    setting_id: int,
    organization_name: Optional[str] = Form(None),
    legal_name: Optional[str] = Form(None),
    alias_name: Optional[str] = Form(None),
    primary_domain: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    company_size: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    admin_email: Optional[str] = Form(None),
    support_email: Optional[str] = Form(None),
    billing_contact_email: Optional[str] = Form(None),
    company_logo: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    obj = await service.org_setting_service.get(db, setting_id)
    if not obj:
        raise HTTPException(status_code=404, detail="OrgSetting not found")

    logo_path = obj.company_logo
    if company_logo is not None and company_logo.filename:
        logo_path = _save_logo_file(company_logo)

    payload = schemas.OrgSettingUpdate(
        organization_name=organization_name if organization_name is not None else obj.organization_name,
        legal_name=legal_name if legal_name is not None else obj.legal_name,
        alias_name=alias_name if alias_name is not None else obj.alias_name,
        primary_domain=primary_domain if primary_domain is not None else obj.primary_domain,
        industry=industry if industry is not None else obj.industry,
        company_size=company_size if company_size is not None else obj.company_size,
        country=country if country is not None else obj.country,
        company_logo=logo_path,
        admin_email=admin_email if admin_email is not None else obj.admin_email,
        support_email=support_email if support_email is not None else obj.support_email,
        billing_contact_email=billing_contact_email if billing_contact_email is not None else obj.billing_contact_email,
    )
    return await service.org_setting_service.update(db, obj, payload)


@router.delete(
    "/org-settings/{setting_id}",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def delete_org_setting(setting_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.org_setting_service.delete(db, setting_id)
    if not obj:
        raise HTTPException(status_code=404, detail="OrgSetting not found")
    return {"message": "OrgSetting deleted successfully"}


# ── Microsoft Entra ID (Teams) Configuration Endpoints ─────────────────────────

@router.post(
    "/microsoft-entra",
    response_model=schemas.MicrosoftEntraConfigOut,
    status_code=status.HTTP_201_CREATED,
    summary="Save Microsoft Entra ID (Teams) Credentials",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def create_or_update_microsoft_entra_config(
    req: schemas.MicrosoftEntraConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Stores Microsoft Entra ID (Tenant ID, Client ID, Client Secret) in database.
    Optionally validates credentials against Microsoft OAuth endpoint before persisting.
    """
    from datetime import datetime, timezone
    from sqlalchemy import select
    from . import models

    connection_status = "UNVERIFIED"
    last_tested_at = None

    if req.verify_connection:
        test_res = await service.test_microsoft_entra_credentials(
            req.tenant_id, req.client_id, req.client_secret
        )
        if test_res["success"]:
            connection_status = "CONNECTED"
            last_tested_at = datetime.now(timezone.utc)
        else:
            connection_status = "FAILED"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to authenticate with Microsoft Entra ID: {test_res['message']}",
            )

    result = await db.execute(
        select(models.MicrosoftEntraConfig).order_by(models.MicrosoftEntraConfig.id.desc())
    )
    existing = result.scalars().first()

    if existing:
        existing.tenant_id = req.tenant_id
        existing.client_id = req.client_id
        existing.client_secret = req.client_secret
        existing.organization_id = req.organization_id
        existing.is_active = req.is_active if req.is_active is not None else True
        existing.connection_status = connection_status
        existing.last_tested_at = last_tested_at
        await db.commit()
        await db.refresh(existing)
        target_obj = existing
    else:
        new_config = models.MicrosoftEntraConfig(
            tenant_id=req.tenant_id,
            client_id=req.client_id,
            client_secret=req.client_secret,
            organization_id=req.organization_id,
            is_active=req.is_active if req.is_active is not None else True,
            connection_status=connection_status,
            last_tested_at=last_tested_at,
        )
        db.add(new_config)
        await db.commit()
        await db.refresh(new_config)
        target_obj = new_config

    return schemas.MicrosoftEntraConfigOut(
        id=target_obj.id,
        tenant_id=target_obj.tenant_id,
        client_id=target_obj.client_id,
        organization_id=target_obj.organization_id,
        is_active=target_obj.is_active,
        connection_status=target_obj.connection_status,
        last_tested_at=target_obj.last_tested_at,
        last_synced_at=target_obj.last_synced_at,
        synced_users_count=target_obj.synced_users_count or 0,
        client_secret_masked=service.mask_client_secret(target_obj.client_secret),
        created_at=target_obj.created_at,
        updated_at=target_obj.updated_at,
    )


@router.get(
    "/microsoft-entra",
    response_model=Optional[schemas.MicrosoftEntraConfigOut],
    summary="Get Microsoft Entra ID (Teams) Configuration",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def get_microsoft_entra_config(db: AsyncSession = Depends(get_db)):
    """Fetches the active Microsoft Entra configuration with masked client secret."""
    from sqlalchemy import select
    from . import models

    result = await db.execute(
        select(models.MicrosoftEntraConfig).order_by(models.MicrosoftEntraConfig.id.desc())
    )
    config = result.scalars().first()
    if not config:
        return None

    return schemas.MicrosoftEntraConfigOut(
        id=config.id,
        tenant_id=config.tenant_id,
        client_id=config.client_id,
        organization_id=config.organization_id,
        is_active=config.is_active,
        connection_status=config.connection_status,
        last_tested_at=config.last_tested_at,
        last_synced_at=config.last_synced_at,
        synced_users_count=config.synced_users_count or 0,
        client_secret_masked=service.mask_client_secret(config.client_secret),
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.get(
    "/microsoft-entra/users",
    response_model=schemas.MicrosoftEntraUsersResponse,
    summary="List Organization Users from Microsoft Entra ID",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def list_microsoft_entra_organization_users(
    top: int = 100,
    search: Optional[str] = None,
    filter: Optional[str] = None,
    next_link: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetches all organization users directly from Microsoft Entra ID / Microsoft 365
    using the credentials saved in the database.
    """
    return await service.fetch_microsoft_entra_users(
        db=db,
        top=top,
        search=search,
        filter_str=filter,
        next_link=next_link,
    )


@router.post(
    "/microsoft-entra/sync-users",
    response_model=schemas.MicrosoftEntraSyncResponse,
    summary="Sync all Microsoft Entra ID users into Organization DB",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def sync_microsoft_entra_users(db: AsyncSession = Depends(get_db)):
    """
    Fetches all users from Microsoft Entra ID (Teams) via Microsoft Graph API,
    and creates or updates them in the application's users and employees database tables.
    """
    res = await service.sync_microsoft_entra_users_to_db(db)
    return schemas.MicrosoftEntraSyncResponse(**res)


@router.patch(
    "/microsoft-entra/{config_id}",
    response_model=schemas.MicrosoftEntraConfigOut,
    summary="Update Microsoft Entra ID Configuration",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def update_microsoft_entra_config(
    config_id: int,
    req: schemas.MicrosoftEntraConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Updates existing Microsoft Entra configuration details."""
    from datetime import datetime, timezone
    from sqlalchemy import select
    from . import models

    result = await db.execute(
        select(models.MicrosoftEntraConfig).where(models.MicrosoftEntraConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Microsoft Entra configuration not found")

    tenant_id = req.tenant_id or config.tenant_id
    client_id = req.client_id or config.client_id
    client_secret = req.client_secret or config.client_secret

    if req.verify_connection:
        test_res = await service.test_microsoft_entra_credentials(tenant_id, client_id, client_secret)
        if test_res["success"]:
            config.connection_status = "CONNECTED"
            config.last_tested_at = datetime.now(timezone.utc)
        else:
            config.connection_status = "FAILED"
            raise HTTPException(
                status_code=400,
                detail=f"Verification failed: {test_res['message']}",
            )

    if req.tenant_id is not None:
        config.tenant_id = req.tenant_id
    if req.client_id is not None:
        config.client_id = req.client_id
    if req.client_secret is not None:
        config.client_secret = req.client_secret
    if req.organization_id is not None:
        config.organization_id = req.organization_id
    if req.is_active is not None:
        config.is_active = req.is_active

    await db.commit()
    await db.refresh(config)

    return schemas.MicrosoftEntraConfigOut(
        id=config.id,
        tenant_id=config.tenant_id,
        client_id=config.client_id,
        organization_id=config.organization_id,
        is_active=config.is_active,
        connection_status=config.connection_status,
        last_tested_at=config.last_tested_at,
        last_synced_at=config.last_synced_at,
        synced_users_count=config.synced_users_count or 0,
        client_secret_masked=service.mask_client_secret(config.client_secret),
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.post(
    "/microsoft-entra/test-connection",
    response_model=schemas.MicrosoftEntraTestResponse,
    summary="Test Microsoft Entra ID Connection",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def test_microsoft_entra_connection(
    req: Optional[schemas.MicrosoftEntraTestRequest] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Tests OAuth token acquisition with Microsoft Entra ID.
    Can test with credentials passed directly in request body or saved in database.
    """
    from datetime import datetime, timezone
    from sqlalchemy import select
    from . import models

    tenant_id = req.tenant_id if req and req.tenant_id else None
    client_id = req.client_id if req and req.client_id else None
    client_secret = req.client_secret if req and req.client_secret else None

    if not (tenant_id and client_id and client_secret):
        result = await db.execute(
            select(models.MicrosoftEntraConfig).order_by(models.MicrosoftEntraConfig.id.desc())
        )
        saved = result.scalars().first()
        if not saved:
            raise HTTPException(
                status_code=400,
                detail="No Microsoft Entra credentials provided in request and none found in database.",
            )
        tenant_id = saved.tenant_id
        client_id = saved.client_id
        client_secret = saved.client_secret

    test_res = await service.test_microsoft_entra_credentials(tenant_id, client_id, client_secret)

    result = await db.execute(
        select(models.MicrosoftEntraConfig).where(
            models.MicrosoftEntraConfig.tenant_id == tenant_id,
            models.MicrosoftEntraConfig.client_id == client_id,
        )
    )
    saved_obj = result.scalars().first()
    if saved_obj:
        saved_obj.connection_status = "CONNECTED" if test_res["success"] else "FAILED"
        saved_obj.last_tested_at = datetime.now(timezone.utc)
        await db.commit()

    if test_res["success"]:
        return schemas.MicrosoftEntraTestResponse(
            status="success",
            message=test_res["message"],
            token_type=test_res.get("token_type"),
            expires_in=test_res.get("expires_in"),
        )
    else:
        return schemas.MicrosoftEntraTestResponse(
            status="failed",
            message=test_res["message"],
        )


@router.delete(
    "/microsoft-entra/{config_id}",
    summary="Delete Microsoft Entra ID Configuration",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def delete_microsoft_entra_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """Deletes a Microsoft Entra ID configuration."""
    from sqlalchemy import select
    from . import models

    result = await db.execute(
        select(models.MicrosoftEntraConfig).where(models.MicrosoftEntraConfig.id == config_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    await db.delete(config)
    await db.commit()
    return {"message": "Microsoft Entra configuration deleted successfully"}
