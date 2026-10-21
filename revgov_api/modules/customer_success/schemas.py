from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from core.schemas import OrmBase


class QBRTrackerBase(BaseModel):
    qbr_id: str
    quarter: str
    customer_id: int
    account_owner_id: int
    qbr_date: Optional[date] = None
    review_type: str
    delivery_performance: str
    revenue_achievement: float = 0
    open_risks: Optional[str] = None
    escalations_discussed: Optional[str] = None
    csat_score: float = 0
    sla_compliance_pct: float = 0
    key_achievements: Optional[str] = None
    innovation_initiatives: Optional[str] = None
    automation_opportunities: Optional[str] = None
    renewal_status: str
    expansion_opportunities: Optional[str] = None
    action_items: Optional[str] = None
    action_owner_id: Optional[int] = None
    due_date: Optional[date] = None
    qbr_deck_shared: bool = False
    leadership_attendees: Optional[str] = None
    overall_account_health: str
    next_qbr_planned_date: Optional[date] = None
    remarks: Optional[str] = None


class QBRTrackerCreate(QBRTrackerBase):
    pass


class QBRTrackerUpdate(QBRTrackerBase):
    pass


class QBRTrackerOut(OrmBase, QBRTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    customer_partner_name: Optional[str] = None
    account_owner_name: Optional[str] = None
    action_owner_name: Optional[str] = None


class EscalationTrackerBase(BaseModel):
    escalation_id: str
    escalation_date: Optional[date] = None
    customer_id: int
    account_owner_id: int
    escalation_category: str
    priority: str
    issue_summary: str
    impact_area: Optional[str] = None
    root_cause: Optional[str] = None
    immediate_action_taken: Optional[str] = None
    long_term_resolution_plan: Optional[str] = None
    escalation_owner_id: int
    internal_stakeholders: Optional[str] = None
    external_stakeholders: Optional[str] = None
    eta_for_resolution: Optional[int] = None
    current_status: str
    severity_level: str
    leadership_visibility: bool = False
    escalated_to: Optional[str] = None
    closure_date: Optional[date] = None
    customer_confirmation_received: bool = False
    lessons_learned: Optional[str] = None
    preventive_actions: Optional[str] = None
    remarks: Optional[str] = None


class EscalationTrackerCreate(EscalationTrackerBase):
    pass


class EscalationTrackerUpdate(EscalationTrackerBase):
    pass


class EscalationTrackerOut(OrmBase, EscalationTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    customer_partner_name: Optional[str] = None
    account_owner_name: Optional[str] = None
    escalation_owner_name: Optional[str] = None


class DealStageEnum(str, Enum):
    LEAD_IDENTIFIED = "Lead Identified"
    QUALIFICATION = "Qualification"
    DISCOVERY = "Discovery / Requirement Gathering"
    SOLUTIONING = "Solutioning / Proposal Preparation"
    PROPOSAL_SUBMITTED = "Proposal Submitted"
    COMMERCIAL_NEGOTIATION = "Commercial Negotiation"
    MANAGEMENT_APPROVAL = "Management Approval"
    VERBAL_COMMITMENT = "Verbal Commitment"
    WON = "Won (PO/Contract Received)"
    DELIVERY_KICK_OFF = "Delivery Kick-off"
    REVENUE_RECOGNIZED = "Revenue Recognized"
    LOST = "Lost"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"


class CommercialDiscussionStatusEnum(str, Enum):
    ON_HOLD = "on hold"
    CLOSED = "closed"
    IN_PROGRESS = "in progress"


class RenewalStatusEnum(str, Enum):
    UPCOMING = "Upcoming"
    DUE_THIS_MONTH = "Due This Month"
    IN_DISCUSSION = "In Discussion"
    PROPOSAL_SHARED = "Proposal Shared"
    UNDER_NEGOTIATION = "Under Negotiation"
    RENEWED = "Renewed"
    RENEWAL_CONFIRMED = "Renewal Confirmed"
    PO_AWAITED = "PO Awaited"
    CONTRACT_IN_PROCESS = "Contract in Process"
    DELAYED = "Delayed"
    AT_RISK = "At Risk"
    LOST_NOT_RENEWED = "Lost / Not Renewed"
    CANCELLED = "Cancelled"
    AUTO_RENEWED = "Auto Renewed"
    CLOSED = "Closed"


class ExecutiveContentTrackerBase(BaseModel):
    executive_connect_id: str
    customer_id: Optional[int] = None
    account_type: str
    engagement_date: Optional[date] = None
    meeting_type: str
    engagement_mode: Optional[str] = None
    internal_executive_sponsor_id: Optional[int] = None
    external_executive_stakeholders: Optional[str] = None
    business_unit: Optional[str] = None
    strategic_objective: Optional[str] = None
    discussion_summary: Optional[str] = None
    strategic_priorities_discussed: Optional[str] = None
    key_decisions_taken: Optional[str] = None
    risks_highlighted: Optional[str] = None
    opportunities_identified: Optional[str] = None
    commitments_made: Optional[str] = None
    action_items: Optional[str] = None
    action_owner_id: Optional[int] = None
    due_date: Optional[date] = None
    escalation_required: bool = False
    meeting_mom_shared: bool = False
    next_executive_connect_date: Optional[date] = None
    remarks: Optional[str] = None


class ExecutiveContentTrackerCreate(ExecutiveContentTrackerBase):
    pass


class ExecutiveContentTrackerUpdate(ExecutiveContentTrackerBase):
    pass


class ExecutiveContentTrackerOut(OrmBase, ExecutiveContentTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    customer_partner_name: Optional[str] = None
    internal_executive_sponsor_name: Optional[str] = None
    action_owner_name: Optional[str] = None


class AccountTypeEnum(str, Enum):
    CUSTOMER = "Customer"
    PARTNER = "Partner"
    PROSPECT = "Prospect"
    NEW = "New"  # Added to support legacy/bad data


class IndustryEnum(str, Enum):
    BFSI = "Banking, Financial Services & Insurance (BFSI)"
    IT_SERVICES = "Information Technology (IT) & IT Services"
    TELECOM = "Telecommunications"
    GOVT = "Government & Public Sector"
    HEALTHCARE = "Healthcare & Life Sciences"
    MANUFACTURING = "Manufacturing"
    RETAIL = "Retail & E-commerce"
    FMCG = "Consumer Goods (FMCG/CPG)"
    ENERGY = "Energy, Oil & Gas"
    EDUCATION = "Education"
    MEDIA = "Media & Entertainment"
    LOGISTICS = "Transportation & Logistics"
    REAL_ESTATE = "Real Estate & Construction"
    HOSPITALITY = "Travel & Hospitality"
    AGRITECH = "Agriculture & AgriTech"
    PHARMA = "Pharmaceuticals & Biotechnology"
    AEROSPACE = "Aerospace & Defence"
    PROF_SERVICES = "Professional Services"
    ENGINEERING = "Engineering & Infrastructure"
    NON_PROFIT = "Non-Profit / NGO"
    STARTUPS = "Startups"
    OTHERS = "Others"
    UNKNOWN = "Unknown"  # Added to support legacy/bad data
    IT = "IT"  # Added to support legacy/bad data


class CustomerStatusEnum(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class CustomerMasterBase(BaseModel):
    customer_id: str
    customer_name: str = Field(..., min_length=1)
    account_type: AccountTypeEnum
    account_manager_id: Optional[int] = None
    industry: IndustryEnum
    status: CustomerStatusEnum
    contract_value: float = Field(..., ge=0)
    country: Optional[str] = None
    remarks: Optional[str] = None


class CustomerMasterCreate(CustomerMasterBase):
    customer_id: Optional[str] = None


class CustomerMasterUpdate(CustomerMasterBase):
    pass


class CustomerMasterOut(OrmBase, CustomerMasterBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    account_manager_name: Optional[str] = None
