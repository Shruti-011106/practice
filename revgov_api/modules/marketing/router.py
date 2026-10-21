from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import get_current_active_user, RoleChecker
from core.constants import (
    ROLE_MARKETING_MANAGER,
    ROLE_PRESALES_MANAGER,
    ROLE_SALES_MANAGER,
)
from . import schemas, service
from auth.models import User

router = APIRouter()


# /event-webinars Endpoints
@router.get(
    "/event-webinars",
    response_model=schemas.EventWebinarListWithKPIs,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def list_eventwebinars(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.eventwebinar_service.get_all_with_kpis_by_user(db, current_user)


@router.get(
    "/event-webinars/{item_id}",
    response_model=schemas.EventWebinarOut,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def get_eventwebinar(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.eventwebinar_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EventWebinar not found")
    return obj


@router.post(
    "/event-webinars",
    response_model=schemas.EventWebinarOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def create_eventwebinar(
    payload: schemas.EventWebinarCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await service.eventwebinar_service.create_by_user(db, payload, current_user)


@router.put(
    "/event-webinars/{item_id}",
    response_model=schemas.EventWebinarOut,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def update_eventwebinar(
    item_id: int,
    payload: schemas.EventWebinarUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.eventwebinar_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="EventWebinar not found")
    return await service.eventwebinar_service.update(db, db_obj, payload)


@router.delete(
    "/event-webinars/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def delete_eventwebinar(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.eventwebinar_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EventWebinar not found")
    return None


# /content-brandings Endpoints
@router.get(
    "/content-brandings",
    response_model=schemas.ContentBrandingListWithKPIs,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def list_contentbrandings(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.contentbranding_service.get_all_with_kpis_by_user(db, current_user)


@router.get(
    "/content-brandings/{item_id}",
    response_model=schemas.ContentBrandingOut,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def get_contentbranding(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.contentbranding_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ContentBranding not found")
    return obj


@router.post(
    "/content-brandings",
    response_model=schemas.ContentBrandingOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def create_contentbranding(
    payload: schemas.ContentBrandingCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await service.contentbranding_service.create_by_user(db, payload, current_user)


@router.put(
    "/content-brandings/{item_id}",
    response_model=schemas.ContentBrandingOut,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def update_contentbranding(
    item_id: int,
    payload: schemas.ContentBrandingUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.contentbranding_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ContentBranding not found")
    return await service.contentbranding_service.update(db, db_obj, payload)


@router.delete(
    "/content-brandings/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def delete_contentbranding(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.contentbranding_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ContentBranding not found")
    return None


# /campaigns Endpoints
@router.get(
    "/campaigns",
    response_model=schemas.CampaignListWithKPIs,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def list_campaigns(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.campaign_service.get_all_with_kpis_by_user(db, current_user)


@router.get(
    "/campaigns/{item_id}",
    response_model=schemas.CampaignOut,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def get_campaign(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.campaign_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return obj


@router.post(
    "/campaigns",
    response_model=schemas.CampaignOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def create_campaign(
    payload: schemas.CampaignCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await service.campaign_service.create_by_user(db, payload, current_user)


@router.put(
    "/campaigns/{item_id}",
    response_model=schemas.CampaignOut,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def update_campaign(
    item_id: int, payload: schemas.CampaignUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.campaign_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return await service.campaign_service.update(db, db_obj, payload)


@router.delete(
    "/campaigns/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Marketing"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def delete_campaign(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.campaign_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return None
