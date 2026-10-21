from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db
from core.dependencies import get_current_active_user
from auth.models import User
from . import schemas, service

router = APIRouter(prefix="/api/v1/activities", tags=["Activities"])


@router.post(
    "/comments",
    response_model=schemas.SystemCommentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def add_comment(
    payload: schemas.SystemCommentCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    return await service.activity_service.add_comment(db, payload, current_user)


@router.get(
    "/comments",
    response_model=List[schemas.SystemCommentOut],
    dependencies=[Depends(get_current_active_user)],
)
async def get_comments(
    entity_type: str, 
    entity_id: int, 
    db: AsyncSession = Depends(get_db)
):
    return await service.activity_service.get_comments(db, entity_type, entity_id)


@router.get(
    "/audit-logs",
    response_model=List[schemas.SystemAuditLogOut],
    dependencies=[Depends(get_current_active_user)],
)
async def get_audit_logs(
    entity_type: str, 
    entity_id: int, 
    db: AsyncSession = Depends(get_db)
):
    return await service.activity_service.get_audit_logs(db, entity_type, entity_id)
