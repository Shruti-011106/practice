from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from core.schemas import OrmBase
from enum import Enum


class ProjectStatusEnum(str, Enum):
    PLANNING = "Planning"
    ACTIVE = "Active"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"
    IN_PROGRESS = "in progress"
    CANCELLED = "Cancelled"
    DELAYED = "Delayed"


class ProjectGovernanceBase(BaseModel):
    project_name: str
    customer_id: int
    pm_id: int
    delivery_lead_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_status: str
    budget: float = 0
    utilization_pct: float = Field(default=0, ge=0, le=100)
    milestone_status: Optional[str] = None
    risks: int = 0
    escalations: int = 0
    dependencies: int = 0
    next_milestone: Optional[str] = None
    key_delivery_risks: Optional[str] = None
    active_escalations: Optional[str] = None
    critical_dependencies: Optional[str] = None


class ProjectGovernanceCreate(ProjectGovernanceBase):
    pass


class ProjectGovernanceUpdate(ProjectGovernanceBase):
    pass


class ProjectGovernanceOut(OrmBase, ProjectGovernanceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    customer_name: Optional[str] = None
    pm_name: Optional[str] = None
    delivery_lead_name: Optional[str] = None


class ProjectGovernanceKPIs(BaseModel):
    total_projects: int = 0
    on_track_projects: int = 0
    projects_at_risk: int = 0
    budget_utilized_pct: float = 0.0
    total_budget: float = 0.0
    total_budget_formatted: str = "₹0.0 L Total Budget"


class ProjectGovernanceListWithKPIs(BaseModel):
    kpis: ProjectGovernanceKPIs
    data: List[ProjectGovernanceOut]



class DeliverableTrackerBase(BaseModel):
    milestone_id: str
    project_id: int
    milestone_name: str
    deliverable_name: str
    planned_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    status: str
    dependency: Optional[str] = None
    owner_id: int
    delay_reason: Optional[str] = None
    customer_signoff: bool = False
    remarks: Optional[str] = None


class DeliverableTrackerCreate(DeliverableTrackerBase):
    pass


class DeliverableTrackerUpdate(DeliverableTrackerBase):
    pass


class DeliverableTrackerOut(OrmBase, DeliverableTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_name: Optional[str] = None
    owner_name: Optional[str] = None


class DeliverableTrackerKPIs(BaseModel):
    total_deliverables: int = 0
    completed_deliverables: int = 0
    delayed_milestones: int = 0
    client_signoffs: int = 0


class DeliverableTrackerListWithKPIs(BaseModel):
    kpis: DeliverableTrackerKPIs
    data: List[DeliverableTrackerOut]



class CustomerSatisfactionBase(BaseModel):
    customer_id: int
    project_id: int
    feedback_date: Optional[date] = None
    feedback_type: str
    csat_score: float = Field(default=0, ge=0, le=5)
    nps_score: float = Field(default=0, ge=-100, le=100)
    positive_feedback: Optional[str] = None
    improvement_areas: Optional[str] = None
    action_items: Optional[str] = None
    owner_id: int
    target_closure_date: Optional[date] = None
    current_status: Optional[str] = None
    remarks: Optional[str] = None


class CustomerSatisfactionCreate(CustomerSatisfactionBase):
    pass


class CustomerSatisfactionUpdate(CustomerSatisfactionBase):
    pass


class CustomerSatisfactionOut(OrmBase, CustomerSatisfactionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    customer_name: Optional[str] = None
    project_name: Optional[str] = None
    owner_name: Optional[str] = None


class CustomerSatisfactionKPIs(BaseModel):
    avg_csat_score: float = 0.0
    avg_nps_score: float = 0.0
    open_action_items: int = 0


class CustomerSatisfactionListWithKPIs(BaseModel):
    kpis: CustomerSatisfactionKPIs
    data: List[CustomerSatisfactionOut]



class QATrackerBase(BaseModel):
    project_id: int
    testing_phase: str
    test_cases_planned: int = 0
    test_cases_executed: int = 0
    pass_pct: float = Field(default=0, ge=0, le=100)
    defect_count: int = 0
    critical_defects: int = 0
    reopened_defects: int = 0
    owner_id: int
    golive_readiness: Optional[str] = None
    quality_status: Optional[str] = None
    remarks: Optional[str] = None


class QATrackerCreate(QATrackerBase):
    pass


class QATrackerUpdate(QATrackerBase):
    pass


class QATrackerOut(OrmBase, QATrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_name: Optional[str] = None
    owner_name: Optional[str] = None


class QATrackerKPIs(BaseModel):
    tracked_projects: int = 0
    total_defects: int = 0
    critical_defects: int = 0
    ready_to_golive: int = 0


class QATrackerListWithKPIs(BaseModel):
    kpis: QATrackerKPIs
    data: List[QATrackerOut]



class ChangeRequestBase(BaseModel):
    cr_id: str
    project_id: int
    description: str
    business_impact: Optional[str] = None
    effort_estimate: Optional[str] = None
    cost_impact: float = 0
    approval_status: str
    delivery_date: Optional[date] = None


class ChangeRequestCreate(ChangeRequestBase):
    pass


class ChangeRequestUpdate(ChangeRequestBase):
    pass


class ChangeRequestOut(OrmBase, ChangeRequestBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_name: Optional[str] = None


class ChangeRequestKPIs(BaseModel):
    total_change_requests: int = 0
    approved_crs: int = 0
    pending_approval: int = 0
    total_cost_impact: float = 0.0
    total_cost_impact_formatted: str = "₹0.0 L Total Cost Impact"


class ChangeRequestListWithKPIs(BaseModel):
    kpis: ChangeRequestKPIs
    data: List[ChangeRequestOut]



class ResourceUtilizationBase(BaseModel):
    employee_id: int
    skill: str
    role: Optional[str] = None
    project_id: Optional[int] = None
    billable_pct: float = Field(default=0, ge=0, le=100)
    utilization_pct: float = Field(default=0, ge=0, le=100)
    allocation_status: Optional[str] = "Active"
    assigned_on: Optional[date] = None
    release_date: Optional[date] = None
    bench_status: Optional[str] = None
    availability: Optional[date] = None


class ResourceUtilizationCreate(ResourceUtilizationBase):
    pass


class ResourceUtilizationUpdate(ResourceUtilizationBase):
    pass


class ResourceUtilizationOut(OrmBase, ResourceUtilizationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    employee_name: Optional[str] = None
    project_name: Optional[str] = None


class ResourceUtilizationKPIs(BaseModel):
    total_resources: int = 0
    avg_billable_pct: float = 0.0
    avg_utilization_pct: float = 0.0
    bench_resources: int = 0
    active_allocations: int = 0


class ResourceUtilizationListWithKPIs(BaseModel):
    kpis: ResourceUtilizationKPIs
    data: List[ResourceUtilizationOut]


class EmployeeProjectDashboardOut(BaseModel):
    id: int
    project_id: int
    project_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_status: Optional[str] = None
    milestone: Optional[str] = None
    pm_name: Optional[str] = None
    primary_skill: Optional[str] = None
    role: Optional[str] = None
    utilization_pct: Optional[float] = 0.0
    allocation_status: Optional[str] = None
    assigned_on: Optional[date] = None
    release_date: Optional[date] = None
    bench_status: Optional[str] = None
    availability_date: Optional[date] = None


class EmployeeProjectDetailsOut(EmployeeProjectDashboardOut):
    delivery_lead_name: Optional[str] = None
    risks: Optional[int] = 0
    escalations: Optional[int] = 0
    dependencies: Optional[int] = 0
    key_delivery_risks: Optional[str] = None
    active_escalations: Optional[str] = None
    critical_dependencies: Optional[str] = None


class EmployeeProjectKPIs(BaseModel):
    total_projects: int = 0
    total_active_projects: int = 0
    upcoming_projects: int = 0
    completed_projects: int = 0


class EmployeeProjectDashboardList(BaseModel):
    kpis: EmployeeProjectKPIs
    data: List[EmployeeProjectDashboardOut]



class RAIDBase(BaseModel):
    raid_id: str
    project_id: int
    type: str
    description: str
    impact: Optional[str] = None
    owner_id: int
    mitigation_plan: Optional[str] = None
    status: str
    target_closure: Optional[date] = None


class RAIDCreate(RAIDBase):
    pass


class RAIDUpdate(RAIDBase):
    pass


class RAIDOut(OrmBase, RAIDBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_name: Optional[str] = None
    owner_name: Optional[str] = None


class RAIDKPIs(BaseModel):
    total_raid_mapped: int = 0
    active_risks_issues: int = 0
    critical_impact_items: int = 0
    resolved_closed: int = 0


class RAIDListWithKPIs(BaseModel):
    kpis: RAIDKPIs
    data: List[RAIDOut]



class VendorSubcontractorGovernanceBase(BaseModel):
    vendor_gov_id: str
    project_id: int
    vendor_id: int
    subcontractor_agency_name: Optional[str] = None
    contract_status: str = "Active"
    sla_target_rating: Optional[str] = "90%"
    allocated_budget: Optional[float] = 0.0
    subcontractor_scope_of_work: Optional[str] = None
    remarks: Optional[str] = None

    @field_validator("allocated_budget", mode="before")
    @classmethod
    def default_budget_if_none(cls, v):
        return 0.0 if v is None else v


class VendorSubcontractorGovernanceCreate(VendorSubcontractorGovernanceBase):
    pass


class VendorSubcontractorGovernanceUpdate(VendorSubcontractorGovernanceBase):
    pass


class VendorSubcontractorGovernanceOut(OrmBase, VendorSubcontractorGovernanceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_name: Optional[str] = None
    vendor_name: Optional[str] = None


class VendorSubcontractorGovernanceKPIs(BaseModel):
    total_contracts: int = 0
    active_subcontractors: int = 0
    total_allocated_budget: float = 0.0


class VendorSubcontractorGovernanceListWithKPIs(BaseModel):
    kpis: VendorSubcontractorGovernanceKPIs
    data: List[VendorSubcontractorGovernanceOut]


class MilestoneBillingBase(BaseModel):
    billing_id: str
    project_id: int
    amount: float = 0.0
    invoice_status: str = "Pending"
    realization_date: Optional[date] = None
    milestone_scope: str
    remarks: Optional[str] = None

    @field_validator("amount", mode="before")
    @classmethod
    def default_amount_if_none(cls, v):
        return 0.0 if v is None else v


class MilestoneBillingCreate(MilestoneBillingBase):
    pass


class MilestoneBillingUpdate(MilestoneBillingBase):
    pass


class MilestoneBillingOut(OrmBase, MilestoneBillingBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_name: Optional[str] = None


class MilestoneBillingKPIs(BaseModel):
    total_milestones: int = 0
    total_milestone_value: float = 0.0
    realized_paid_invoices: float = 0.0


class MilestoneBillingListWithKPIs(BaseModel):
    kpis: MilestoneBillingKPIs
    data: List[MilestoneBillingOut]


class ProjectClosureBase(BaseModel):
    closure_id: str
    project_id: int
    closure_date: date
    closure_status: str = "Initiated"
    asset_handover_status: str = "Pending"
    csat_rating: Optional[float] = 0.0
    retrospective_summary: str
    remarks: Optional[str] = None

    @field_validator("csat_rating", mode="before")
    @classmethod
    def default_csat_if_none(cls, v):
        return 0.0 if v is None else v


class ProjectClosureCreate(ProjectClosureBase):
    pass


class ProjectClosureUpdate(ProjectClosureBase):
    pass


class ProjectClosureOut(OrmBase, ProjectClosureBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_name: Optional[str] = None


class ProjectClosureKPIs(BaseModel):
    closures_initiated: int = 0
    projects_closed: int = 0
    avg_csat_rating: float = 0.0


class ProjectClosureListWithKPIs(BaseModel):
    kpis: ProjectClosureKPIs
    data: List[ProjectClosureOut]


