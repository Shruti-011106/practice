from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SystemLookupBase(BaseModel):
    type: str
    code: str
    label: str
    is_active: bool = True
    sort_order: int = 0


class SystemLookupCreate(SystemLookupBase):
    pass


class SystemLookupUpdate(BaseModel):
    label: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class SystemLookupOut(SystemLookupBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
