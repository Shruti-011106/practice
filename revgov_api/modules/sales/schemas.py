from datetime import date, datetime

from pydantic import BaseModel

from core.schemas import OrmBase


class LeadTrackerBase(BaseModel):
    lead_id: str
    client_name: str
    industry: str | None = None
    lead_source: str | None = None
    sales_owner_id: int | None = None
    presales_engineer_id: int | None = None
    country: str | None = None
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    priority: str | None = None
    expected_budget: float | None = 0
    expected_timeline: str | None = None
    lead_status: str
    expected_revenue: float | None = 0
    next_followup: date | None = None
    remarks: str | None = None


class LeadTrackerCreate(LeadTrackerBase):
    pass


class LeadTrackerUpdate(LeadTrackerBase):
    pass


class LeadTrackerOut(OrmBase, LeadTrackerBase):
    id: int
    sales_owner: str | None = None
    assigned_presales_engineer: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LeadTrackerKPIs(BaseModel):
    total_leads: int = 0
    total_active_leads: int = 0
    total_qualified_leads: int = 0
    total_closed_leads: int = 0


class LeadTrackerListResponse(BaseModel):
    kpis: LeadTrackerKPIs
    data: list[LeadTrackerOut]


class SalesRevenueTrackerBase(BaseModel):
    month: str
    pipeline_id: int | None = None
    revenue_owner_id: int | None = None
    deal_value: float | None = 0.0
    invoice: float | None = 0.0
    collected: float | None = 0.0
    pending: float | None = 0.0
    forecast: float | None = 0.0
    quarter: str | None = None
    status: str | None = None
    remarks: str | None = None


class SalesRevenueTrackerCreate(SalesRevenueTrackerBase):
    pass


class SalesRevenueTrackerUpdate(SalesRevenueTrackerBase):
    pass


class SalesRevenueTrackerOut(OrmBase, SalesRevenueTrackerBase):
    id: int
    revenue_owner: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SalesPipelineBase(BaseModel):
    opportunity_id: str
    account_name: str
    vertical: str | None = None
    opportunity_name: str
    opportunity_owner: str | None = None
    revdau_owner_id: int | None = None
    lead_id: int | None = None
    demo_tracker_id: int | None = None
    lead_source: str | None = None
    country: str | None = None
    region: str | None = None
    deal_value: float | None = 0.0
    probability_pct: float | None = 0
    expected_closure_quarter: str | None = None
    expected_closure_date: date | None = None
    pipeline_stage: str | None = None
    risks: str | None = None
    next_action: str | None = None
    year: int | None = None


class SalesPipelineCreate(SalesPipelineBase):
    pass


class SalesPipelineUpdate(SalesPipelineBase):
    pass


class SalesPipelineOut(OrmBase, SalesPipelineBase):
    id: int
    client_name: str | None = None
    revdau_owner: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SalesPipelineActionHistoryOut(OrmBase):
    id: int
    pipeline_id: int
    action_text: str
    created_at: datetime | None = None

