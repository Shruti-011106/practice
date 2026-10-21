from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from core.schemas import OrmBase

class SystemCommentCreate(BaseModel):
    entity_type: str
    entity_id: int
    comment_text: str

class SystemCommentOut(OrmBase):
    id: int
    entity_type: str
    entity_id: int
    comment_text: str
    user_name: Optional[str] = None
    created_at: datetime


class SystemAuditLogOut(OrmBase):
    id: int
    entity_type: str
    entity_id: int
    action: str
    details: Optional[str] = None
    user_name: Optional[str] = None
    created_at: datetime
