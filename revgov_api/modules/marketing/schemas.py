from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import date, datetime
import datetime as dt
from core.schemas import OrmBase


class EventWebinarBase(BaseModel):
    event_name: str
    date: Optional[dt.date] = None
    owner_id: int
    participants: int = 0
    leads_generated: int = 0
    followup_status: str


class EventWebinarCreate(EventWebinarBase):
    pass


class EventWebinarUpdate(EventWebinarBase):
    pass


class EventWebinarOut(OrmBase, EventWebinarBase):
    id: int
    owner_name: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- KPI Schemas ---

class EventWebinarKPIs(BaseModel):
    total_events: int = 0
    total_participants: int = 0
    leads_generated: int = 0
    planned_events: int = 0


class EventWebinarListWithKPIs(BaseModel):
    kpis: EventWebinarKPIs
    data: List[EventWebinarOut]


class ContentBrandingBase(BaseModel):
    asset_name: str
    type: str
    owner_id: int
    approval_status: str
    reusability: Optional[Union[str, bool]] = None
    last_updated: Optional[date] = None


class ContentBrandingCreate(ContentBrandingBase):
    pass


class ContentBrandingUpdate(ContentBrandingBase):
    pass


class ContentBrandingOut(OrmBase, ContentBrandingBase):
    id: int
    owner_name: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CampaignBase(BaseModel):
    campaign_name: str
    campaign_owner_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: float = 0
    leads_generated: int = 0
    roi: float = 0
    target_audience: Optional[str] = None
    status: str


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(CampaignBase):
    pass


class CampaignOut(OrmBase, CampaignBase):
    id: int
    campaign_owner_name: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContentBrandingKPIs(BaseModel):
    total_assets: int = 0
    approved_assets: int = 0
    pending_review: int = 0
    high_reusability: int = 0


class ContentBrandingListWithKPIs(BaseModel):
    kpis: ContentBrandingKPIs
    data: List[ContentBrandingOut]


class CampaignKPIs(BaseModel):
    total_campaigns: int = 0
    active_campaigns: int = 0
    high_roi: int = 0
    planned_campaigns: int = 0


class CampaignListWithKPIs(BaseModel):
    kpis: CampaignKPIs
    data: List[CampaignOut]
