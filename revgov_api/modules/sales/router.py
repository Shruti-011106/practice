from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
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


# /lead-trackers Endpoints
@router.get(
    "/lead-trackers",
    response_model=schemas.LeadTrackerListResponse,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def list_leadtrackers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    leads = await service.leadtracker_service.get_all_by_user(db, current_user, skip=skip, limit=limit)
    
    total_leads = len(leads)
    total_qualified = sum(1 for lead in leads if lead.lead_status and lead.lead_status.lower() == "qualified")
    total_closed = sum(1 for lead in leads if lead.lead_status and lead.lead_status.lower() in ["closed", "rejected", "lost"])
    total_active = total_leads - (total_qualified + total_closed)
    
    kpis = schemas.LeadTrackerKPIs(
        total_leads=total_leads,
        total_active_leads=total_active,
        total_qualified_leads=total_qualified,
        total_closed_leads=total_closed
    )
    
    return schemas.LeadTrackerListResponse(kpis=kpis, data=leads)


@router.get(
    "/lead-trackers/{item_id}",
    response_model=schemas.LeadTrackerOut,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def get_leadtracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.leadtracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="LeadTracker not found")
    return obj


@router.post(
    "/lead-trackers",
    response_model=schemas.LeadTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def create_leadtracker(
    payload: schemas.LeadTrackerCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await service.leadtracker_service.create(db, payload, user_id=current_user.id)


@router.put(
    "/lead-trackers/{item_id}",
    response_model=schemas.LeadTrackerOut,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def update_leadtracker(
    item_id: int, 
    payload: schemas.LeadTrackerUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_obj = await service.leadtracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="LeadTracker not found")
    return await service.leadtracker_service.update(db, db_obj, payload, user_id=current_user.id)


@router.delete(
    "/lead-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def delete_leadtracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.leadtracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="LeadTracker not found")
    return None




@router.patch(
    "/lead-trackers/{item_id}/reject",
    response_model=schemas.LeadTrackerOut,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER]
            )
        ),
    ],
)
async def reject_leadtracker(item_id: int, db: AsyncSession = Depends(get_db)):
    db_obj = await service.leadtracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="LeadTracker not found")
    return await service.leadtracker_service.reject_lead(db, db_obj)





# /sales-revenue-trackers Endpoints
@router.get(
    "/sales-revenue-trackers",
    response_model=List[schemas.SalesRevenueTrackerOut],
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def list_salesrevenuetrackers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.salesrevenuetracker_service.get_all_by_user(db, current_user, skip=skip, limit=limit)


@router.get(
    "/sales-revenue-trackers/{item_id}",
    response_model=schemas.SalesRevenueTrackerOut,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def get_salesrevenuetracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.salesrevenuetracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SalesRevenueTracker not found")
    return obj


@router.post(
    "/sales-revenue-trackers",
    response_model=schemas.SalesRevenueTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def create_salesrevenuetracker(
    payload: schemas.SalesRevenueTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.salesrevenuetracker_service.create(db, payload)


@router.put(
    "/sales-revenue-trackers/{item_id}",
    response_model=schemas.SalesRevenueTrackerOut,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def update_salesrevenuetracker(
    item_id: int,
    payload: schemas.SalesRevenueTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.salesrevenuetracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="SalesRevenueTracker not found")
    return await service.salesrevenuetracker_service.update(db, db_obj, payload)


@router.delete(
    "/sales-revenue-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def delete_salesrevenuetracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.salesrevenuetracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SalesRevenueTracker not found")
    return None


@router.patch(
    "/sales-revenue-trackers/{item_id}/reject",
    response_model=schemas.SalesRevenueTrackerOut,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def reject_salesrevenuetracker(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.salesrevenuetracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="SalesRevenueTracker not found")
    return await service.salesrevenuetracker_service.reject_revenue(db, db_obj)


# /sales-pipelines Endpoints
@router.get(
    "/sales-pipelines",
    response_model=List[schemas.SalesPipelineOut],
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def list_salespipelines(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.salespipeline_service.get_all_by_user(db, current_user, skip=skip, limit=limit)


@router.get(
    "/sales-pipelines/{item_id}",
    response_model=schemas.SalesPipelineOut,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def get_salespipeline(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.salespipeline_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SalesPipeline not found")
    return obj


@router.post(
    "/sales-pipelines",
    response_model=schemas.SalesPipelineOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def create_salespipeline(
    payload: schemas.SalesPipelineCreate, db: AsyncSession = Depends(get_db)
):
    return await service.salespipeline_service.create(db, payload)


@router.put(
    "/sales-pipelines/{item_id}",
    response_model=schemas.SalesPipelineOut,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def update_salespipeline(
    item_id: int,
    payload: schemas.SalesPipelineUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.salespipeline_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="SalesPipeline not found")
    return await service.salespipeline_service.update(db, db_obj, payload)


@router.delete(
    "/sales-pipelines/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def delete_salespipeline(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.salespipeline_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SalesPipeline not found")
    return None


@router.get(
    "/sales-pipelines/{item_id}/action-history",
    response_model=List[schemas.SalesPipelineActionHistoryOut],
    tags=["Sales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def list_salespipeline_actionhistory(item_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from .models import SalesPipelineActionHistory
    
    # Verify pipeline exists
    obj = await service.salespipeline_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="SalesPipeline not found")
        
    query = select(SalesPipelineActionHistory).where(
        SalesPipelineActionHistory.pipeline_id == item_id
    ).order_by(SalesPipelineActionHistory.created_at.desc())
    
    result = await db.execute(query)
    return list(result.scalars().all())
