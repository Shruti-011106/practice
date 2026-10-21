from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import get_db
from core.dependencies import get_current_active_user, RoleChecker
from core.constants import (
    ROLE_PRESALES_MANAGER,
    ROLE_SALES_MANAGER,
)
from . import schemas, service
from auth.models import User

router = APIRouter()


# /proposal-trackers Endpoints
@router.get(
    "/proposal-trackers",
    response_model=schemas.ProposalTrackerListResponse,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def list_proposaltrackers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    data = await service.proposaltracker_service.get_all_by_user(db, current_user)
    
    total = len(data)
    won = sum(1 for p in data if p.status and p.status.lower() == "accepted")
    active = sum(1 for p in data if p.status and p.status.lower() in ["in progress", "active", "drafting"])
    approved = sum(1 for p in data if p.internal_approval and p.internal_approval.lower() == "approved")
    
    kpis = schemas.ProposalTrackerKPIs(
        total_proposals=total,
        proposals_won=won,
        active_drafting=active,
        proposals_approved=approved
    )
    
    return schemas.ProposalTrackerListResponse(kpis=kpis, data=data)


@router.get(
    "/proposal-trackers/{item_id}",
    response_model=schemas.ProposalTrackerOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def get_proposaltracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.proposaltracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ProposalTracker not found")
    return obj


@router.post(
    "/proposal-trackers",
    response_model=schemas.ProposalTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def create_proposaltracker(
    payload: schemas.ProposalTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.proposaltracker_service.create(db, payload)


@router.put(
    "/proposal-trackers/{item_id}",
    response_model=schemas.ProposalTrackerOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def update_proposaltracker(
    item_id: int,
    payload: schemas.ProposalTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.proposaltracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ProposalTracker not found")
    return await service.proposaltracker_service.update(db, db_obj, payload)


@router.patch(
    "/proposal-trackers/{item_id}/reject",
    response_model=schemas.ProposalTrackerOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def reject_proposaltracker(item_id: int, db: AsyncSession = Depends(get_db)):
    db_obj = await service.proposaltracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ProposalTracker not found")
    return await service.proposaltracker_service.reject_proposal(db, db_obj)


@router.delete(
    "/proposal-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def delete_proposaltracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.proposaltracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ProposalTracker not found")
    return None


# /rfp-trackers Endpoints
@router.get(
    "/rfp-trackers",
    response_model=schemas.RFPTrackerListResponse,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def list_rfptrackers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    data = await service.rfptracker_service.get_all_by_user(db, current_user)
    
    total = len(data)
    open_rfp = sum(1 for x in data if x.status and x.status.lower() in ["open", "active"])
    submitted = sum(1 for x in data if x.status and x.status.lower() == "submitted")
    won = sum(1 for x in data if x.status and x.status.lower() == "won")
    lost = sum(1 for x in data if x.status and x.status.lower() == "lost")
    
    from datetime import date, datetime
    today = date.today()
    
    def get_date(val):
        if isinstance(val, datetime): return val.date()
        if isinstance(val, date): return val
        if isinstance(val, str):
            try: return datetime.strptime(val.split("T")[0], "%Y-%m-%d").date()
            except: return date.min
        return date.min

    deadline_count = sum(1 for x in data if x.bid_closing_date and get_date(x.bid_closing_date) >= today and (x.status or "").lower() not in ["won", "lost", "rejected"])
    
    kpis = schemas.RFPTrackerKPIs(
        total_rfp=total,
        open_rfp=open_rfp,
        submitted_rfp=submitted,
        won_rfp=won,
        lost_rfp=lost,
        deadline_rfp=deadline_count
    )
    return schemas.RFPTrackerListResponse(kpis=kpis, data=data)


@router.get(
    "/rfp-trackers/{item_id}",
    response_model=schemas.RFPTrackerOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def get_rfptracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.rfptracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RFPTracker not found")
    return obj


@router.post(
    "/rfp-trackers",
    response_model=schemas.RFPTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def create_rfptracker(
    payload: schemas.RFPTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.rfptracker_service.create(db, payload)


@router.put(
    "/rfp-trackers/{item_id}",
    response_model=schemas.RFPTrackerOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def update_rfptracker(
    item_id: int, payload: schemas.RFPTrackerUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.rfptracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="RFPTracker not found")
    obj = await service.rfptracker_service.update(db, db_obj, payload)
    return obj


@router.patch(
    "/rfp-trackers/{item_id}/reject",
    response_model=schemas.RFPTrackerOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def reject_rfptracker(item_id: int, db: AsyncSession = Depends(get_db)):
    db_obj = await service.rfptracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="RFPTracker not found")
    return await service.rfptracker_service.reject_rfp(db, db_obj)


@router.delete(
    "/rfp-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def delete_rfptracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.rfptracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RFPTracker not found")
    return None


# /poc-trackers Endpoints
@router.get(
    "/poc-trackers",
    response_model=schemas.POCTrackerListResponse,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def list_poctrackers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    data = await service.poctracker_service.get_all_by_user(db, current_user)
    
    total = len(data)
    active = sum(1 for poc in data if poc.status and poc.status.lower() in ["in progress", "active"])
    successful = sum(1 for poc in data if poc.status and poc.status.lower() in ["successful", "completed", "won"])
    failed = sum(1 for poc in data if poc.status and poc.status.lower() in ["failed", "cancelled"])
    
    kpis = schemas.POCTrackerKPIs(
        total_pocs=total,
        active_pocs=active,
        successful_pocs=successful,
        failed_cancelled_pocs=failed
    )
    
    return schemas.POCTrackerListResponse(kpis=kpis, data=data)


@router.get(
    "/poc-trackers/{item_id}",
    response_model=schemas.POCTrackerOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def get_poctracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.poctracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="POCTracker not found")
    return obj


@router.post(
    "/poc-trackers",
    response_model=schemas.POCTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def create_poctracker(
    payload: schemas.POCTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.poctracker_service.create(db, payload)


@router.put(
    "/poc-trackers/{item_id}",
    response_model=schemas.POCTrackerOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def update_poctracker(
    item_id: int, payload: schemas.POCTrackerUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.poctracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="POCTracker not found")
    return await service.poctracker_service.update(db, db_obj, payload)

@router.patch(
    "/poc-trackers/{item_id}/fail",
    response_model=schemas.POCTrackerOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def fail_poctracker(item_id: int, db: AsyncSession = Depends(get_db)):
    db_obj = await service.poctracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="POCTracker not found")
    return await service.poctracker_service.fail_poc(db, db_obj)


@router.delete(
    "/poc-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def delete_poctracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.poctracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="POCTracker not found")
    return None


# /presales-bids Endpoints
@router.get(
    "/presales-bids",
    response_model=schemas.PresalesBIDListResponse,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def list_presalesbids(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    bids = await service.presalesbid_service.get_all_by_user(db, current_user)
    
    pending_bids = sum(1 for bid in bids if bid.status and bid.status.lower() == "pending")
    approved_bids = sum(1 for bid in bids if bid.status and bid.status.lower() == "approved")
    rejected_bids = sum(1 for bid in bids if bid.status and bid.status.lower() == "rejected")
    
    # Calculate revenue potential from pending and approved bids
    revenue_potential = sum(bid.estimate_revenue or 0 for bid in bids if bid.status and bid.status.lower() in ["pending", "approved"])
    
    kpis = schemas.PresalesBIDKPIs(
        pending_bids=pending_bids,
        approved_bids=approved_bids,
        rejected_bids=rejected_bids,
        revenue_potential=revenue_potential
    )
    
    return schemas.PresalesBIDListResponse(kpis=kpis, data=bids)


@router.get(
    "/presales-bids/{item_id}",
    response_model=schemas.PresalesBIDOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def get_presalesbid(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.presalesbid_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PresalesBID not found")
    return obj


@router.post(
    "/presales-bids",
    response_model=schemas.PresalesBIDOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def create_presalesbid(
    payload: schemas.PresalesBIDCreate, db: AsyncSession = Depends(get_db)
):
    return await service.presalesbid_service.create(db, payload)


@router.put(
    "/presales-bids/{item_id}",
    response_model=schemas.PresalesBIDOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def update_presalesbid(
    item_id: int, payload: schemas.PresalesBIDUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.presalesbid_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PresalesBID not found")
    return await service.presalesbid_service.update(db, db_obj, payload)


@router.patch(
    "/presales-bids/{item_id}/reject",
    response_model=schemas.PresalesBIDOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def reject_presalesbid(item_id: int, db: AsyncSession = Depends(get_db)):
    db_obj = await service.presalesbid_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PresalesBID not found")
    return await service.presalesbid_service.reject_bid(db, db_obj)


@router.delete(
    "/presales-bids/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def delete_presalesbid(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.presalesbid_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PresalesBID not found")
    return None


# /presales-demos Endpoints
@router.get(
    "/presales-demos",
    response_model=schemas.PresalesDemoListResponse,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def list_presalesdemos(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    data = await service.presalesdemo_service.get_all_by_user(db, current_user)
    
    total = len(data)
    scheduled = sum(1 for d in data if d.status and d.status.lower() == "scheduled")
    completed = sum(1 for d in data if d.status and d.status.lower() == "completed")
    upcoming = sum(1 for d in data if d.status and d.status.lower() == "upcoming")
    
    kpis = schemas.PresalesDemoKPIs(
        total_demos=total,
        scheduled_demos=scheduled,
        completed_demos=completed,
        upcoming_demos=upcoming
    )
    
    return schemas.PresalesDemoListResponse(kpis=kpis, data=data)


@router.get(
    "/presales-demos/{item_id}",
    response_model=schemas.PresalesDemoOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def get_presalesdemo(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.presalesdemo_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PresalesDemo not found")
    return obj


@router.post(
    "/presales-demos",
    response_model=schemas.PresalesDemoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def create_presalesdemo(
    payload: schemas.PresalesDemoCreate, db: AsyncSession = Depends(get_db)
):
    return await service.presalesdemo_service.create(db, payload)


@router.put(
    "/presales-demos/{item_id}",
    response_model=schemas.PresalesDemoOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def update_presalesdemo(
    item_id: int,
    payload: schemas.PresalesDemoUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.presalesdemo_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PresalesDemo not found")
    return await service.presalesdemo_service.update(db, db_obj, payload)


@router.delete(
    "/presales-demos/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def delete_presalesdemo(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.presalesdemo_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PresalesDemo not found")
    return None


# /presales-governances Endpoints
@router.get(
    "/presales-governances",
    response_model=List[schemas.PresalesGovernanceOut],
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def list_presalesgovernances(db: AsyncSession = Depends(get_db)):
    return await service.presalesgovernance_service.get_all(db)


@router.get(
    "/presales-governances/{item_id}",
    response_model=schemas.PresalesGovernanceOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def get_presalesgovernance(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.presalesgovernance_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PresalesGovernance not found")
    return obj


@router.post(
    "/presales-governances",
    response_model=schemas.PresalesGovernanceOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def create_presalesgovernance(
    payload: schemas.PresalesGovernanceCreate, db: AsyncSession = Depends(get_db)
):
    return await service.presalesgovernance_service.create(db, payload)


@router.put(
    "/presales-governances/{item_id}",
    response_model=schemas.PresalesGovernanceOut,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def update_presalesgovernance(
    item_id: int,
    payload: schemas.PresalesGovernanceUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.presalesgovernance_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PresalesGovernance not found")
    return await service.presalesgovernance_service.update(db, db_obj, payload)


@router.delete(
    "/presales-governances/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Presales"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER])),
    ],
)
async def delete_presalesgovernance(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.presalesgovernance_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PresalesGovernance not found")
    return None
