from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import get_db
from core.dependencies import get_current_active_user, RoleChecker
from core.constants import (
    ROLE_CEO,
    ROLE_CS_MANAGER,
    ROLE_FINANCE_MANAGER,
    ROLE_PROJECT_MANAGER,
    ROLE_SUPER_ADMIN,
)
from . import schemas, service

router = APIRouter()


# /qbr-trackers Endpoints
@router.get(
    "/qbr-trackers",
    response_model=List[schemas.QBRTrackerOut],
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def list_qbrtrackers(db: AsyncSession = Depends(get_db)):
    return await service.qbrtracker_service.get_all(db)


@router.get(
    "/qbr-trackers/{item_id}",
    response_model=schemas.QBRTrackerOut,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def get_qbrtracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.qbrtracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="QBRTracker not found")
    return obj


@router.post(
    "/qbr-trackers",
    response_model=schemas.QBRTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def create_qbrtracker(
    payload: schemas.QBRTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.qbrtracker_service.create(db, payload)


@router.put(
    "/qbr-trackers/{item_id}",
    response_model=schemas.QBRTrackerOut,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def update_qbrtracker(
    item_id: int, payload: schemas.QBRTrackerUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.qbrtracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="QBRTracker not found")
    return await service.qbrtracker_service.update(db, db_obj, payload)


@router.delete(
    "/qbr-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def delete_qbrtracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.qbrtracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="QBRTracker not found")
    return None


# /escalation-trackers Endpoints
@router.get(
    "/escalation-trackers",
    response_model=List[schemas.EscalationTrackerOut],
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def list_escalationtrackers(db: AsyncSession = Depends(get_db)):
    return await service.escalationtracker_service.get_all(db)


@router.get(
    "/escalation-trackers/{item_id}",
    response_model=schemas.EscalationTrackerOut,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def get_escalationtracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.escalationtracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EscalationTracker not found")
    return obj


@router.post(
    "/escalation-trackers",
    response_model=schemas.EscalationTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def create_escalationtracker(
    payload: schemas.EscalationTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.escalationtracker_service.create(db, payload)


@router.put(
    "/escalation-trackers/{item_id}",
    response_model=schemas.EscalationTrackerOut,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def update_escalationtracker(
    item_id: int,
    payload: schemas.EscalationTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.escalationtracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="EscalationTracker not found")
    return await service.escalationtracker_service.update(db, db_obj, payload)


@router.delete(
    "/escalation-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def delete_escalationtracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.escalationtracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EscalationTracker not found")
    return None


# /executive-connect-trackers Endpoints
@router.get(
    "/executive-connect-trackers",
    response_model=List[schemas.ExecutiveContentTrackerOut],
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER])),
    ],
)
async def list_executivecontenttrackers(db: AsyncSession = Depends(get_db)):
    return await service.executivecontenttracker_service.get_all(db)


@router.get(
    "/executive-connect-trackers/{item_id}",
    response_model=schemas.ExecutiveContentTrackerOut,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER])),
    ],
)
async def get_executivecontenttracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.executivecontenttracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ExecutiveContentTracker not found")
    return obj


@router.post(
    "/executive-connect-trackers",
    response_model=schemas.ExecutiveContentTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER])),
    ],
)
async def create_executivecontenttracker(
    payload: schemas.ExecutiveContentTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.executivecontenttracker_service.create(db, payload)


@router.put(
    "/executive-connect-trackers/{item_id}",
    response_model=schemas.ExecutiveContentTrackerOut,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER])),
    ],
)
async def update_executivecontenttracker(
    item_id: int,
    payload: schemas.ExecutiveContentTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.executivecontenttracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ExecutiveContentTracker not found")
    return await service.executivecontenttracker_service.update(db, db_obj, payload)


@router.delete(
    "/executive-connect-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER])),
    ],
)
async def delete_executivecontenttracker(
    item_id: int, db: AsyncSession = Depends(get_db)
):
    obj = await service.executivecontenttracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ExecutiveContentTracker not found")
    return None


# /customer-masters Endpoints
@router.get(
    "/customer-masters",
    response_model=List[schemas.CustomerMasterOut],
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def list_customermasters(db: AsyncSession = Depends(get_db)):
    return await service.customermaster_service.get_all(db)


@router.get(
    "/customer-masters/{item_id}",
    response_model=schemas.CustomerMasterOut,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def get_customermaster(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.customermaster_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CustomerMaster not found")
    return obj


@router.post(
    "/customer-masters",
    response_model=schemas.CustomerMasterOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def create_customermaster(
    payload: schemas.CustomerMasterCreate, db: AsyncSession = Depends(get_db)
):
    return await service.customermaster_service.create(db, payload)


@router.put(
    "/customer-masters/{item_id}",
    response_model=schemas.CustomerMasterOut,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def update_customermaster(
    item_id: int,
    payload: schemas.CustomerMasterUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.customermaster_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="CustomerMaster not found")
    return await service.customermaster_service.update(db, db_obj, payload)


@router.delete(
    "/customer-masters/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Customer Success"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_CS_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def delete_customermaster(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.customermaster_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CustomerMaster not found")
    return None
