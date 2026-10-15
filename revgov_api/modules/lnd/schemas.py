from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from core.schemas import OrmBase


class ReusableAssetBase(BaseModel):
    asset_name: str
    category: str
    technology: Optional[str] = None
    owner_id: Optional[int] = None
    created_by_id: Optional[int] = None
    version: Optional[str] = None
    document_name: Optional[str] = None
    document_type: Optional[str] = None
    upload: Optional[str] = (
        None  # Stores the generated path/URL of the uploaded PDF file
    )
    repository_link: Optional[str] = None
    maturity_level: Optional[str] = None
    approval_status: Optional[str] = None
    last_review_date: Optional[date] = None
    tag: Optional[str] = None
    description: Optional[str] = None


class ReusableAssetCreate(ReusableAssetBase):
    technology: str
    owner_id: int


class ReusableAssetUpdate(ReusableAssetBase):
    technology: str
    owner_id: int


class ReusableAssetOut(OrmBase, ReusableAssetBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    owner_name: Optional[str] = None


# Knowledge Repository - Merged into Reusable Asset (Temporarily Disabled)
# class KnowledgeRepoBase(BaseModel):
#     document_name: str
#     category: str
#     team: str
#     owner: str
#     approval_status: str
#     last_review_date: Optional[date] = None
#     tag: Optional[str] = None
#
#
# class KnowledgeRepoCreate(KnowledgeRepoBase):
#     pass
#
#
# class KnowledgeRepoUpdate(KnowledgeRepoBase):
#     pass
#
#
# class KnowledgeRepoOut(OrmBase, KnowledgeRepoBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


class TrainingDetailItem(BaseModel):
    training_name: Optional[str] = None
    planned_date: Optional[str] = None
    completion_status: Optional[str] = None
    completion_pct: Optional[float] = 0.0
    certification_planned: Optional[str] = None
    certification_status: Optional[str] = None


class CapabilityBuildingBase(BaseModel):
    employee_id: Optional[int] = None
    practice_owner_id: Optional[int] = None
    technology: Optional[str] = None
    skill_level: Optional[str] = None
    current_skill: Optional[str] = None
    target_skill: Optional[str] = None
    active_projects: Optional[str] = None
    business_alignment: Optional[str] = None
    readiness_score: Optional[float] = 0.0
    strategic_priority: Optional[str] = None
    
    training_count: Optional[int] = 0
    training_details: Optional[List[TrainingDetailItem]] = None


class CapabilityBuildingCreate(CapabilityBuildingBase):
    pass


class CapabilityBuildingUpdate(CapabilityBuildingBase):
    pass


class CapabilityBuildingOut(OrmBase, CapabilityBuildingBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    employee_name: Optional[str] = None
    practice_owner_name: Optional[str] = None


class CapabilityBuildingKPIs(BaseModel):
    # Admin fields
    total_employees_tracked: Optional[int] = None
    active_training_tracks: Optional[int] = None
    intermediate_advance: Optional[int] = None
    
    # Employee fields
    total_trainings: Optional[int] = None
    completed_courses: Optional[int] = None
    learning_progress_pct: Optional[float] = None
    
    # Shared fields
    certifications_completed: Optional[int] = None


class CapabilityBuildingListWithKPIs(BaseModel):
    kpis: CapabilityBuildingKPIs
    data: list[CapabilityBuildingOut]


class PartnershipAllianceBase(BaseModel):
    partner_name: str
    alliance_owner: str
    partnership_type: str
    joint_opportunities: Optional[str] = None
    certifications: Optional[str] = None
    gtm_activities: Optional[str] = None
    revenue_contribution: float = 0


class PartnershipAllianceCreate(PartnershipAllianceBase):
    pass


class PartnershipAllianceUpdate(PartnershipAllianceBase):
    pass


class PartnershipAllianceOut(OrmBase, PartnershipAllianceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TechCapabilityBase(BaseModel):
    technology: str
    practice_owner: str
    certified_resources: int = 0
    active_projects: int = 0
    readiness_score: float = 0
    strategic_priority: Optional[str] = None


class TechCapabilityCreate(TechCapabilityBase):
    pass


class TechCapabilityUpdate(TechCapabilityBase):
    pass


class TechCapabilityOut(OrmBase, TechCapabilityBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InnovationAutomationBase(BaseModel):
    innovation_name: Optional[str] = None
    created_by_id: Optional[int] = None
    team: Optional[str] = None
    automation_type: Optional[str] = None
    productivity_gain: Optional[str] = None
    status: Optional[str] = None
    business_benefit: Optional[str] = None


class InnovationAutomationCreate(InnovationAutomationBase):
    pass


class InnovationAutomationUpdate(InnovationAutomationBase):
    pass


class InnovationAutomationOut(OrmBase, InnovationAutomationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InnovationAutomationKPIs(BaseModel):
    total_innovations: int = 0
    ai_automations: int = 0
    high_efficiency_gain: int = 0
    active_implementations: int = 0


class InnovationAutomationListWithKPIs(BaseModel):
    kpis: InnovationAutomationKPIs
    data: list[InnovationAutomationOut]


class TrainingTrackerBase(BaseModel):
    training_name: str
    team: str
    planned_date: Optional[date] = None
    completion_pct: float = 0
    certification_status: Optional[str] = None
    kpi_impact: Optional[str] = None


class TrainingTrackerCreate(TrainingTrackerBase):
    pass


class TrainingTrackerUpdate(TrainingTrackerBase):
    pass


class TrainingTrackerOut(OrmBase, TrainingTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
