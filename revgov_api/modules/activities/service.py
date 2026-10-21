from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schemas
from auth.models import User

class ActivityService:
    async def add_comment(
        self, db: AsyncSession, obj_in: schemas.SystemCommentCreate, current_user: User
    ) -> models.SystemComment:
        db_obj = models.SystemComment(
            entity_type=obj_in.entity_type,
            entity_id=obj_in.entity_id,
            user_id=current_user.id,
            comment_text=obj_in.comment_text
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_comments(
        self, db: AsyncSession, entity_type: str, entity_id: int
    ) -> List[models.SystemComment]:
        query = select(models.SystemComment).where(
            models.SystemComment.entity_type == entity_type,
            models.SystemComment.entity_id == entity_id
        ).order_by(models.SystemComment.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()

    async def add_audit_log(
        self, db: AsyncSession, entity_type: str, entity_id: int, action: str, details: Optional[str] = None, user_id: Optional[int] = None
    ) -> models.SystemAuditLog:
        db_obj = models.SystemAuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            action=action,
            details=details
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_audit_logs(
        self, db: AsyncSession, entity_type: str, entity_id: int
    ) -> List[models.SystemAuditLog]:
        query = select(models.SystemAuditLog).where(
            models.SystemAuditLog.entity_type == entity_type,
            models.SystemAuditLog.entity_id == entity_id
        ).order_by(models.SystemAuditLog.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()

activity_service = ActivityService()
