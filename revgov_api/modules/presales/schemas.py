from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from core.schemas import OrmBase


class ProposalTrackerBase(BaseModel):
    proposal_id: str
    presales_bid_id: Optional[int] = None
    proposal_name: str
    customer_submission_date: Optional[date] = None
    proposal_version: Optional[str] = None
    pricing: Optional[float] = None
    timeline: Optional[str] = None
    assumptions: Optional[str] = None
    attachments: Optional[str] = None
    internal_approval: Optional[str] = None
    status: Optional[str] = None
    approver_id: Optional[int] = None
    remarks_and_scope: Optional[str] = None


class ProposalTrackerCreate(ProposalTrackerBase):
    pass


class ProposalTrackerUpdate(ProposalTrackerBase):
    pass


class ProposalTrackerOut(OrmBase, ProposalTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    bid_no: Optional[str] = None
    client_name: Optional[str] = None
    approver_name: Optional[str] = None


class ProposalTrackerKPIs(BaseModel):
    total_proposals: int = 0
    proposals_won: int = 0
    active_drafting: int = 0
    proposals_approved: int = 0


class ProposalTrackerListResponse(BaseModel):
    kpis: ProposalTrackerKPIs
    data: list[ProposalTrackerOut]


class RFPTrackerBase(BaseModel):
    rfp_id: str
    lead_id: Optional[int] = None
    submission_date: Optional[date] = None
    bid_closing_date: Optional[date] = None
    presales_owner_id: Optional[int] = None
    solution_type: str
    document_url: Optional[str] = None
    status: Optional[str] = None
    win_probability: Optional[float] = 0
    priority: Optional[str] = None
    remarks: Optional[str] = None


class RFPTrackerCreate(RFPTrackerBase):
    pass


class RFPTrackerUpdate(RFPTrackerBase):
    pass


class RFPTrackerOut(OrmBase, RFPTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    client_name: Optional[str] = None
    presales_owner: Optional[str] = None


class RFPTrackerKPIs(BaseModel):
    total_rfp: int = 0
    open_rfp: int = 0
    submitted_rfp: int = 0
    won_rfp: int = 0
    lost_rfp: int = 0
    deadline_rfp: int = 0


class RFPTrackerListResponse(BaseModel):
    kpis: RFPTrackerKPIs
    data: list[RFPTrackerOut]


class POCTrackerBase(BaseModel):
    poc_id: str
    poc_name: Optional[str] = None
    proposal_tracker_id: Optional[int] = None
    technology: str
    environment: Optional[str] = None
    owner_id: Optional[int] = None
    poc_start_date: Optional[date] = None
    poc_end_date: Optional[date] = None
    status: Optional[str] = None
    outcome: Optional[str] = None
    success_percentage: Optional[float] = None
    remarks: Optional[str] = None


class POCTrackerCreate(POCTrackerBase):
    pass


class POCTrackerUpdate(POCTrackerBase):
    pass


class POCTrackerOut(OrmBase, POCTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    client: Optional[str] = None


class POCTrackerKPIs(BaseModel):
    total_pocs: int = 0
    active_pocs: int = 0
    successful_pocs: int = 0
    failed_cancelled_pocs: int = 0


class POCTrackerListResponse(BaseModel):
    kpis: POCTrackerKPIs
    data: list[POCTrackerOut]


class PresalesBIDBase(BaseModel):
    bid_id: str
    rfp_tracker_id: Optional[int] = None
    bid_submission_date: Optional[date] = None
    bid_decision: Optional[str] = None
    reason: Optional[str] = None
    estimate_revenue: Optional[float] = 0
    estimate_cost: Optional[float] = 0
    win_probability: Optional[float] = 0
    risks: Optional[str] = None
    competitors: Optional[str] = None
    approver_id: Optional[int] = None
    status: Optional[str] = None


class PresalesBIDCreate(PresalesBIDBase):
    pass


class PresalesBIDUpdate(PresalesBIDBase):
    pass


class PresalesBIDOut(OrmBase, PresalesBIDBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    rfp_no: Optional[str] = None
    client_name: Optional[str] = None
    approver_name: Optional[str] = None


class PresalesBIDKPIs(BaseModel):
    pending_bids: int = 0
    approved_bids: int = 0
    rejected_bids: int = 0
    revenue_potential: float = 0.0


class PresalesBIDListResponse(BaseModel):
    kpis: PresalesBIDKPIs
    data: list[PresalesBIDOut]


class PresalesDemoBase(BaseModel):
    demo_name: str
    poc_tracker_id: Optional[int] = None
    technology: str
    business_use_case: Optional[str] = None
    demo_owner_id: Optional[int] = None
    status: Optional[str] = None
    demo_url: Optional[str] = None
    credentials: Optional[str] = None
    reusable_for: Optional[str] = None
    last_updated: Optional[date] = None
    demo_date: Optional[date] = None
    attendees: Optional[str] = None
    feedback: Optional[str] = None
    questions: Optional[str] = None
    outcome: Optional[str] = None
    next_step: Optional[str] = None


class PresalesDemoCreate(PresalesDemoBase):
    pass


class PresalesDemoUpdate(PresalesDemoBase):
    pass


class PresalesDemoOut(OrmBase, PresalesDemoBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    demo_owner: Optional[str] = None


class PresalesDemoKPIs(BaseModel):
    total_demos: int = 0
    scheduled_demos: int = 0
    completed_demos: int = 0
    upcoming_demos: int = 0


class PresalesDemoListResponse(BaseModel):
    kpis: PresalesDemoKPIs
    data: list[PresalesDemoOut]


class PresalesGovernanceBase(BaseModel):
    asset_name: str
    category: str
    technology: str
    demo_ready: bool = False
    reusable: bool = False
    last_used: Optional[date] = None
    business_impact: Optional[str] = None


class PresalesGovernanceCreate(PresalesGovernanceBase):
    pass


class PresalesGovernanceUpdate(PresalesGovernanceBase):
    pass


class PresalesGovernanceOut(OrmBase, PresalesGovernanceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
