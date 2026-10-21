from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrmBase(BaseModel):
    model_config = {"from_attributes": True}


class CommonOut(OrmBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DashboardResponse(BaseModel):
    role: str
    kpis: dict
    charts: dict

