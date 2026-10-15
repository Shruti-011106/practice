# from pydantic import BaseModel, EmailStr, Field, HttpUrl
# from typing import Optional, List
# from datetime import date, datetime


# # ─── Helpers ────────────────────────────────
# class OrmBase(BaseModel):
#     model_config = {"from_attributes": True}

# # ─────────────────────────────────────────────
# # AUTH MODULE
# # ─────────────────────────────────────────────

# class RoleBase(BaseModel):
#     name: str

# class RoleResponse(RoleBase):
#     id: int
#     permissions: Optional[dict] = {}
#     model_config = {"from_attributes": True}

# class UserBase(BaseModel):
#     email: EmailStr
#     first_name: str
#     last_name: str

# class UserCreate(UserBase):
#     password: str = Field(..., min_length=8)
#     role_id: int

# class UserUpdate(BaseModel):
#     email: Optional[EmailStr] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     password: Optional[str] = None
#     is_active: Optional[bool] = None
#     role_ids: Optional[List[int]] = None

# class UserResponse(UserBase):
#     id: int
#     is_active: bool
#     roles: List[RoleResponse] = []
#     model_config = {"from_attributes": True}

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str
#     message: str
#     user: UserResponse

# class ChangePasswordRequest(BaseModel):
#     old_password: str
#     new_password: str = Field(..., min_length=8)
#     confirm_password: str

# class MessageResponse(BaseModel):
#     message: str


# # ─────────────────────────────────────────────
# # HR MODULE
# # ─────────────────────────────────────────────
# from app.db.models import EmploymentTypeEnum, StatusEnum, CompletionStatusEnum, JobStatusEnum, PriorityEnum, OfferDropEnum, FeedbackStatusEnum

# class EmployeeBase(BaseModel):
#     employee_code: Optional[str] = None
#     employee_name: str
#     department: str
#     designation: str
#     manager_id: Optional[int] = None
#     location: Optional[str] = None
#     doj: Optional[date] = None
#     employment_type: EmploymentTypeEnum
#     status: StatusEnum
#     remarks: Optional[str] = None

# class EmployeeCreate(EmployeeBase): pass
# class EmployeeUpdate(EmployeeBase): pass
# class EmployeeOut(OrmBase, EmployeeBase):
#     id: int
#     employee_code: Optional[str] = None
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class LearningTrackerBase(BaseModel):
#     employee_id: int
#     training_name: str
#     training_date: Optional[date] = None
#     trainer: str
#     certification: Optional[str] = None
#     completion_status: CompletionStatusEnum
#     remarks: Optional[str] = None

# class LearningTrackerCreate(LearningTrackerBase): pass
# class LearningTrackerUpdate(LearningTrackerBase): pass
# class LearningTrackerOut(OrmBase, LearningTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class LinkedInTrackerBase(BaseModel):
#     job_title: str
#     linkedin_post_date: Optional[date] = None
#     job_link: Optional[HttpUrl] = None
#     no_of_applicants: int = 0
#     engagement_count: int = 0
#     last_updated: Optional[date] = None
#     status: str

# class LinkedInTrackerCreate(LinkedInTrackerBase): pass
# class LinkedInTrackerUpdate(LinkedInTrackerBase): pass
# class LinkedInTrackerOut(OrmBase, LinkedInTrackerBase):
#     id: int
#     posting_id: str
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# from pydantic import model_validator

# class JobOpeningBase(BaseModel):
#     job_title: str
#     department: str
#     hiring_manager_id: int
#     priority: Optional[PriorityEnum] = None
#     experience_required: Optional[str] = None
#     skills_required: Optional[str] = None
#     location: Optional[str] = None
#     employment_type: EmploymentTypeEnum
#     budget_ctc_range: Optional[str] = None
#     open_date: Optional[date] = None
#     target_closure_date: Optional[date] = None
#     current_status: JobStatusEnum
#     recruiter: Optional[str] = None
#     linkedin_posted: bool = False
#     applications_received: int = 0
#     shortlisted: int = 0
#     interviewed: int = 0
#     offered: int = 0
#     joined: int = 0
#     offer_drop: Optional[OfferDropEnum] = None
#     remarks: Optional[str] = None

#     @model_validator(mode='after')
#     def validate_recruitment_funnel(self):
#         # Date validation
#         if self.open_date and self.target_closure_date:
#             if self.target_closure_date < self.open_date:
#                 raise ValueError("Target closure date must be after open date.")

#         # Funnel numbers validation
#         if self.shortlisted > self.applications_received:
#             raise ValueError("Shortlisted count cannot exceed Applications Received.")
#         if self.interviewed > self.shortlisted:
#             raise ValueError("Interviewed count cannot exceed Shortlisted count.")
#         if self.offered > self.interviewed:
#             raise ValueError("Offered count cannot exceed Interviewed count.")
#         if self.joined > self.offered:
#             raise ValueError("Joined count cannot exceed Offered count.")

#         return self

# class JobOpeningCreate(JobOpeningBase): pass
# class JobOpeningUpdate(JobOpeningBase): pass
# class JobOpeningOut(OrmBase, JobOpeningBase):
#     id: int
#     req_id: str
#     aging_days: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class InterviewGovernanceBase(BaseModel):
#     candidate_name: str
#     job_opening_id: int
#     round: str
#     interviewer_id: int
#     interview_date: Optional[date] = None
#     feedback_status: FeedbackStatusEnum
#     result: str
#     next_round: Optional[str] = None
#     final_decision: Optional[str] = None
#     remark: Optional[str] = None

# class InterviewGovernanceCreate(InterviewGovernanceBase): pass
# class InterviewGovernanceUpdate(InterviewGovernanceBase): pass
# class InterviewGovernanceOut(OrmBase, InterviewGovernanceBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class PartnerTrackerBase(BaseModel):
#     partner_id: str
#     partner_name: str
#     partner_type: str
#     partnership_level: Optional[str] = None
#     region: Optional[str] = None
#     industry_focus: Optional[str] = None
#     partnership_start_date: Optional[date] = None
#     agreement_renewal_date: Optional[date] = None
#     account_manager: str
#     partner_poc_name: str
#     contact_number: Optional[str] = None
#     email_id: Optional[str] = None
#     annual_revenue_target: float = 0
#     ytd_revenue_generated: float = 0
#     pipeline_value: float = 0
#     opportunities_open: int = 0
#     opportunities_won: int = 0
#     opportunities_lost: int = 0
#     win_rate_pct: float = 0
#     certifications_achieved: Optional[str] = None
#     competency_status: Optional[str] = None
#     training_completed: bool = False
#     certification_expiry_date: Optional[date] = None
#     joint_events_conducted: int = 0
#     webinars_conducted: int = 0
#     marketing_campaigns_executed: int = 0
#     last_business_review_date: Optional[date] = None
#     next_review_date: Optional[date] = None
#     open_action_items: int = 0
#     open_escalations: int = 0
#     escalation_severity: Optional[str] = None
#     partner_satisfaction_score: float = 0
#     health_status: Optional[str] = None
#     risk_identified: Optional[str] = None
#     mitigation_plan: Optional[str] = None
#     current_status: str
#     remarks: Optional[str] = None

# class PartnerTrackerCreate(PartnerTrackerBase): pass
# class PartnerTrackerUpdate(PartnerTrackerBase): pass
# class PartnerTrackerOut(OrmBase, PartnerTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class VendorPartnerHiringBase(BaseModel):
#     partner_name: str
#     skills_provided: str
#     resources_shared: int = 0
#     sla_adherence: Optional[str] = None
#     cost: float = 0
#     feedback_score: float = 0

# class VendorPartnerHiringCreate(VendorPartnerHiringBase): pass
# class VendorPartnerHiringUpdate(VendorPartnerHiringBase): pass
# class VendorPartnerHiringOut(OrmBase, VendorPartnerHiringBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class InternshipStatusBase(BaseModel):
#     intern_name: str
#     college: str
#     mentor_id: int
#     project_assigned: str
#     start_date: Optional[date] = None
#     evaluation_status: str

# class InternshipStatusCreate(InternshipStatusBase): pass
# class InternshipStatusUpdate(InternshipStatusBase): pass
# class InternshipStatusOut(OrmBase, InternshipStatusBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class BuddyEngagementBase(BaseModel):
#     new_joiner: str
#     buddy_assigned: str
#     onboarding_progress: Optional[str] = None
#     feedback: Optional[str] = None
#     engagement_score: float = 0

# class BuddyEngagementCreate(BuddyEngagementBase): pass
# class BuddyEngagementUpdate(BuddyEngagementBase): pass
# class BuddyEngagementOut(OrmBase, BuddyEngagementBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class EmployeePerformanceBase(BaseModel):
#     employee: str
#     kras: str
#     quarterly_rating: float = 0
#     manager_feedback: Optional[str] = None
#     improvement_areas: Optional[str] = None
#     promotion_readiness: Optional[str] = None

# class EmployeePerformanceCreate(EmployeePerformanceBase): pass
# class EmployeePerformanceUpdate(EmployeePerformanceBase): pass
# class EmployeePerformanceOut(OrmBase, EmployeePerformanceBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# # ─────────────────────────────────────────────
# # PROJECT GOVERNANCE MODULE
# # ─────────────────────────────────────────────

# class ProjectGovernanceBase(BaseModel):
#     project_name: str
#     customer: str
#     pm: str
#     delivery_lead: str
#     start_date: Optional[date] = None
#     end_date: Optional[date] = None
#     project_status: str
#     budget: float = 0
#     utilization_pct: float = 0
#     milestone_status: Optional[str] = None
#     risks: Optional[str] = None
#     escalations: Optional[str] = None
#     dependencies: Optional[str] = None
#     next_milestone: Optional[str] = None

# class ProjectGovernanceCreate(ProjectGovernanceBase): pass
# class ProjectGovernanceUpdate(ProjectGovernanceBase): pass
# class ProjectGovernanceOut(OrmBase, ProjectGovernanceBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class DeliverableTrackerBase(BaseModel):
#     milestone_id: str
#     project_name: str
#     milestone_name: str
#     deliverable_name: str
#     planned_date: Optional[date] = None
#     actual_completion_date: Optional[date] = None
#     status: str
#     dependency: Optional[str] = None
#     owner: str
#     delay_reason: Optional[str] = None
#     customer_signoff: bool = False
#     remarks: Optional[str] = None

# class DeliverableTrackerCreate(DeliverableTrackerBase): pass
# class DeliverableTrackerUpdate(DeliverableTrackerBase): pass
# class DeliverableTrackerOut(OrmBase, DeliverableTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class CustomerSatisfactionBase(BaseModel):
#     customer_name: str
#     project_name: str
#     feedback_date: Optional[date] = None
#     feedback_type: str
#     csat_score: float = 0
#     nps_score: float = 0
#     positive_feedback: Optional[str] = None
#     improvement_areas: Optional[str] = None
#     action_items: Optional[str] = None
#     owner: Optional[str] = None
#     target_closure_date: Optional[date] = None
#     current_status: Optional[str] = None
#     remarks: Optional[str] = None

# class CustomerSatisfactionCreate(CustomerSatisfactionBase): pass
# class CustomerSatisfactionUpdate(CustomerSatisfactionBase): pass
# class CustomerSatisfactionOut(OrmBase, CustomerSatisfactionBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class QATrackerBase(BaseModel):
#     project_name: str
#     testing_phase: str
#     test_cases_planned: int = 0
#     test_cases_executed: int = 0
#     pass_pct: float = 0
#     defect_count: int = 0
#     critical_defects: int = 0
#     reopened_defects: int = 0
#     qa_owner: str
#     golive_readiness: Optional[str] = None
#     quality_status: Optional[str] = None
#     remarks: Optional[str] = None

# class QATrackerCreate(QATrackerBase): pass
# class QATrackerUpdate(QATrackerBase): pass
# class QATrackerOut(OrmBase, QATrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class ChangeRequestBase(BaseModel):
#     cr_id: str
#     project: str
#     description: str
#     business_impact: Optional[str] = None
#     effort_estimate: Optional[str] = None
#     cost_impact: float = 0
#     approval_status: str
#     delivery_date: Optional[date] = None

# class ChangeRequestCreate(ChangeRequestBase): pass
# class ChangeRequestUpdate(ChangeRequestBase): pass
# class ChangeRequestOut(OrmBase, ChangeRequestBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class ResourceUtilizationBase(BaseModel):
#     employee_name: str
#     skill: str
#     project_allocation: Optional[str] = None
#     billable_pct: float = 0
#     utilization_pct: float = 0
#     availability: Optional[str] = None

# class ResourceUtilizationCreate(ResourceUtilizationBase): pass
# class ResourceUtilizationUpdate(ResourceUtilizationBase): pass
# class ResourceUtilizationOut(OrmBase, ResourceUtilizationBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class RAIDBase(BaseModel):
#     raid_id: str
#     type: str
#     description: str
#     impact: Optional[str] = None
#     owner: str
#     mitigation_plan: Optional[str] = None
#     status: str
#     target_closure: Optional[date] = None

# class RAIDCreate(RAIDBase): pass
# class RAIDUpdate(RAIDBase): pass
# class RAIDOut(OrmBase, RAIDBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# # ─────────────────────────────────────────────
# # CUSTOMER SUCCESS GOVERNANCE MODULE
# # ─────────────────────────────────────────────

# class QBRTrackerBase(BaseModel):
#     qbr_id: str
#     quarter: str
#     customer_partner_name: str
#     account_owner: str
#     qbr_date: Optional[date] = None
#     review_type: str
#     delivery_performance: str
#     revenue_achievement: float = 0
#     open_risks: Optional[str] = None
#     escalations_discussed: Optional[str] = None
#     csat_score: float = 0
#     sla_compliance_pct: float = 0
#     key_achievements: Optional[str] = None
#     innovation_initiatives: Optional[str] = None
#     automation_opportunities: Optional[str] = None
#     renewal_status: str
#     expansion_opportunities: Optional[str] = None
#     action_items: Optional[str] = None
#     action_owner: Optional[str] = None
#     due_date: Optional[date] = None
#     qbr_deck_shared: bool = False
#     leadership_attendees: Optional[str] = None
#     overall_account_health: str
#     next_qbr_planned_date: Optional[date] = None
#     remarks: Optional[str] = None

# class QBRTrackerCreate(QBRTrackerBase): pass
# class QBRTrackerUpdate(QBRTrackerBase): pass
# class QBRTrackerOut(OrmBase, QBRTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class EscalationTrackerBase(BaseModel):
#     escalation_id: str
#     escalation_date: Optional[date] = None
#     customer_partner_name: str
#     account_owner: str
#     escalation_category: str
#     priority: str
#     issue_summary: str
#     impact_area: Optional[str] = None
#     root_cause: Optional[str] = None
#     immediate_action_taken: Optional[str] = None
#     long_term_resolution_plan: Optional[str] = None
#     escalation_owner: str
#     internal_stakeholders: Optional[str] = None
#     external_stakeholders: Optional[str] = None
#     eta_for_resolution: Optional[int] = None
#     current_status: str
#     severity_level: str
#     leadership_visibility: bool = False
#     escalated_to: Optional[str] = None
#     closure_date: Optional[date] = None
#     customer_confirmation_received: bool = False
#     lessons_learned: Optional[str] = None
#     preventive_actions: Optional[str] = None
#     remarks: Optional[str] = None

# class EscalationTrackerCreate(EscalationTrackerBase): pass
# class EscalationTrackerUpdate(EscalationTrackerBase): pass
# class EscalationTrackerOut(OrmBase, EscalationTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class RevenueTrackerBase(BaseModel):
#     opportunity_id: str
#     customer_name: str
#     account_manager: str
#     current_contract_value: float = 0
#     renewal_due_date: Optional[date] = None
#     renewal_status: str
#     renewal_probability: bool = False
#     expansion_opportunity: bool = False
#     potential_revenue: float = 0
#     solution_area: Optional[str] = None
#     customer_pain_points: Optional[str] = None
#     proposed_solutions: Optional[str] = None
#     competitor_presence: Optional[str] = None
#     commercial_discussion_status: str
#     proposal_submitted_date: Optional[date] = None
#     executive_sponsor: Optional[str] = None
#     risks: Optional[str] = None
#     action_items: Optional[str] = None
#     next_followup_date: Optional[date] = None
#     deal_stage: Optional[str] = None
#     closure_forecast: Optional[date] = None
#     win_loss_status: Optional[str] = None
#     remarks: Optional[str] = None

# class RevenueTrackerCreate(RevenueTrackerBase): pass
# class RevenueTrackerUpdate(RevenueTrackerBase): pass
# class RevenueTrackerOut(OrmBase, RevenueTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class ExecutiveContentTrackerBase(BaseModel):
#     executive_connect_id: str
#     customer_partner_name: str
#     account_type: str
#     engagement_date: Optional[date] = None
#     meeting_type: str
#     engagement_mode: Optional[str] = None
#     internal_executive_sponsor: str
#     external_executive_stakeholders: Optional[str] = None
#     business_unit: Optional[str] = None
#     strategic_objective: Optional[str] = None
#     discussion_summary: Optional[str] = None
#     strategic_priorities_discussed: Optional[str] = None
#     key_decisions_taken: Optional[str] = None
#     risks_highlighted: Optional[str] = None
#     opportunities_identified: Optional[str] = None
#     commitments_made: Optional[str] = None
#     action_items: Optional[str] = None
#     action_owner: Optional[str] = None
#     due_date: Optional[date] = None
#     escalation_required: bool = False
#     meeting_mom_shared: bool = False
#     next_executive_connect_date: Optional[date] = None
#     remarks: Optional[str] = None

# class ExecutiveContentTrackerCreate(ExecutiveContentTrackerBase): pass
# class ExecutiveContentTrackerUpdate(ExecutiveContentTrackerBase): pass
# class ExecutiveContentTrackerOut(OrmBase, ExecutiveContentTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# # ─────────────────────────────────────────────
# # FINANCE & PROCUREMENT MODULE
# # ─────────────────────────────────────────────

# class POTrackerBase(BaseModel):
#     po_number: str
#     vendor_name: str
#     po_date: Optional[date] = None
#     amount: float = 0
#     department: str
#     approval_status: str
#     payment_status: Optional[str] = None
#     remarks: Optional[str] = None

# class POTrackerCreate(POTrackerBase): pass
# class POTrackerUpdate(POTrackerBase): pass
# class POTrackerOut(OrmBase, POTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class InvoiceTrackerBase(BaseModel):
#     invoice_number: str
#     vendor: str
#     invoice_date: Optional[date] = None
#     invoice_amount: float = 0
#     due_date: Optional[date] = None
#     payment_status: str
#     remarks: Optional[str] = None

# class InvoiceTrackerCreate(InvoiceTrackerBase): pass
# class InvoiceTrackerUpdate(InvoiceTrackerBase): pass
# class InvoiceTrackerOut(OrmBase, InvoiceTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class BudgetTrackerBase(BaseModel):
#     department: str
#     budget_allocated: float = 0
#     budget_utilized: float = 0
#     remaining_budget: float = 0
#     quarter: str
#     remarks: Optional[str] = None

# class BudgetTrackerCreate(BudgetTrackerBase): pass
# class BudgetTrackerUpdate(BudgetTrackerBase): pass
# class BudgetTrackerOut(OrmBase, BudgetTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# # ─────────────────────────────────────────────
# # LEARNING & DEVELOPMENT MODULE
# # ─────────────────────────────────────────────

# class ReusableAssetBase(BaseModel):
#     asset_name: str
#     category: str
#     technology: str
#     owner: str
#     version: Optional[str] = None
#     documentation: Optional[str] = None
#     repository_link: Optional[str] = None
#     reuse_count: int = 0
#     maturity_level: Optional[str] = None

# class ReusableAssetCreate(ReusableAssetBase): pass
# class ReusableAssetUpdate(ReusableAssetBase): pass
# class ReusableAssetOut(OrmBase, ReusableAssetBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# Knowledge Repository - Merged into Reusable Asset (Temporarily Disabled)
# class KnowledgeRepoBase(BaseModel):
#     document_name: str
#     category: str
#     team: str
#     owner: str
#     approval_status: str
#     last_review_date: Optional[date] = None
#     tag: Optional[str] = None

# class KnowledgeRepoCreate(KnowledgeRepoBase): pass
# class KnowledgeRepoUpdate(KnowledgeRepoBase): pass
# class KnowledgeRepoOut(OrmBase, KnowledgeRepoBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class CapabilityBuildingBase(BaseModel):
#     employee_name: str
#     current_skill: str
#     target_skill: str
#     certification_planned: Optional[str] = None
#     completion_status: str
#     skill_level: Optional[str] = None
#     business_alignment: Optional[str] = None

# class CapabilityBuildingCreate(CapabilityBuildingBase): pass
# class CapabilityBuildingUpdate(CapabilityBuildingBase): pass
# class CapabilityBuildingOut(OrmBase, CapabilityBuildingBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class PartnershipAllianceBase(BaseModel):
#     partner_name: str
#     alliance_owner: str
#     partnership_type: str
#     joint_opportunities: Optional[str] = None
#     certifications: Optional[str] = None
#     gtm_activities: Optional[str] = None
#     revenue_contribution: float = 0

# class PartnershipAllianceCreate(PartnershipAllianceBase): pass
# class PartnershipAllianceUpdate(PartnershipAllianceBase): pass
# class PartnershipAllianceOut(OrmBase, PartnershipAllianceBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class TechCapabilityBase(BaseModel):
#     technology: str
#     practice_owner: str
#     certified_resources: int = 0
#     active_projects: int = 0
#     readiness_score: float = 0
#     strategic_priority: Optional[str] = None

# class TechCapabilityCreate(TechCapabilityBase): pass
# class TechCapabilityUpdate(TechCapabilityBase): pass
# class TechCapabilityOut(OrmBase, TechCapabilityBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class InnovationAutomationBase(BaseModel):
#     innovation_name: str
#     team: str
#     automation_type: str
#     productivity_gain: Optional[str] = None
#     status: str
#     business_benefit: Optional[str] = None

# class InnovationAutomationCreate(InnovationAutomationBase): pass
# class InnovationAutomationUpdate(InnovationAutomationBase): pass
# class InnovationAutomationOut(OrmBase, InnovationAutomationBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class TrainingTrackerBase(BaseModel):
#     training_name: str
#     team: str
#     planned_date: Optional[date] = None
#     completion_pct: float = 0
#     certification_status: Optional[str] = None
#     kpi_impact: Optional[str] = None

# class TrainingTrackerCreate(TrainingTrackerBase): pass
# class TrainingTrackerUpdate(TrainingTrackerBase): pass
# class TrainingTrackerOut(OrmBase, TrainingTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# # ─────────────────────────────────────────────
# # MARKETING MODULE
# # ─────────────────────────────────────────────

# class EventWebinarBase(BaseModel):
#     event_name: str
#     date: Optional[date] = None
#     owner: str
#     participants: int = 0
#     leads_generated: int = 0
#     followup_status: str

# class EventWebinarCreate(EventWebinarBase): pass
# class EventWebinarUpdate(EventWebinarBase): pass
# class EventWebinarOut(OrmBase, EventWebinarBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class ContentBrandingBase(BaseModel):
#     asset_name: str
#     type: str
#     owner: str
#     approval_status: str
#     reusability: bool = False
#     last_updated: Optional[date] = None

# class ContentBrandingCreate(ContentBrandingBase): pass
# class ContentBrandingUpdate(ContentBrandingBase): pass
# class ContentBrandingOut(OrmBase, ContentBrandingBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class CampaignBase(BaseModel):
#     campaign_name: str
#     campaign_owner: str
#     start_date: Optional[date] = None
#     end_date: Optional[date] = None
#     budget: float = 0
#     leads_generated: int = 0
#     roi: float = 0
#     target_audience: Optional[str] = None
#     status: str

# class CampaignCreate(CampaignBase): pass
# class CampaignUpdate(CampaignBase): pass
# class CampaignOut(OrmBase, CampaignBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# # ─────────────────────────────────────────────
# # PRESALES MODULE
# # ─────────────────────────────────────────────

# class ProposalTrackerBase(BaseModel):
#     proposal_id: str
#     client: str
#     proposal_name: str
#     submission_date: Optional[date] = None
#     version: Optional[str] = None
#     proposal_status: str

# class ProposalTrackerCreate(ProposalTrackerBase): pass
# class ProposalTrackerUpdate(ProposalTrackerBase): pass
# class ProposalTrackerOut(OrmBase, ProposalTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class RFPTrackerBase(BaseModel):
#     rfp_id: str
#     client_name: str
#     submission_date: Optional[date] = None
#     presales_owner: str
#     solution_type: str
#     status: str
#     win_probability: float = 0
#     remarks: Optional[str] = None

# class RFPTrackerCreate(RFPTrackerBase): pass
# class RFPTrackerUpdate(RFPTrackerBase): pass
# class RFPTrackerOut(OrmBase, RFPTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class POCTrackerBase(BaseModel):
#     poc_id: str
#     client: str
#     technology: str
#     environment: Optional[str] = None
#     poc_start_date: Optional[date] = None
#     poc_end_date: Optional[date] = None
#     status: str
#     outcome: Optional[str] = None
#     remarks: Optional[str] = None

# class POCTrackerCreate(POCTrackerBase): pass
# class POCTrackerUpdate(POCTrackerBase): pass
# class POCTrackerOut(OrmBase, POCTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class PresalesBIDBase(BaseModel):
#     bid_id: str
#     client: str
#     rfp_rfi: Optional[str] = None
#     bid_submission_date: Optional[date] = None
#     solution_architect: str
#     demo_required: bool = False
#     proposal_status: str
#     dependencies: Optional[str] = None
#     review_status: Optional[str] = None
#     win_loss_status: Optional[str] = None

# class PresalesBIDCreate(PresalesBIDBase): pass
# class PresalesBIDUpdate(PresalesBIDBase): pass
# class PresalesBIDOut(OrmBase, PresalesBIDBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class PresalesDemoBase(BaseModel):
#     demo_name: str
#     technology: str
#     business_use_case: Optional[str] = None
#     demo_owner: str
#     status: str
#     demo_url: Optional[str] = None
#     credentials: Optional[str] = None
#     reusable_for: Optional[str] = None
#     last_updated: Optional[date] = None

# class PresalesDemoCreate(PresalesDemoBase): pass
# class PresalesDemoUpdate(PresalesDemoBase): pass
# class PresalesDemoOut(OrmBase, PresalesDemoBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class PresalesGovernanceBase(BaseModel):
#     asset_name: str
#     category: str
#     technology: str
#     demo_ready: bool = False
#     reusable: bool = False
#     last_used: Optional[date] = None
#     business_impact: Optional[str] = None

# class PresalesGovernanceCreate(PresalesGovernanceBase): pass
# class PresalesGovernanceUpdate(PresalesGovernanceBase): pass
# class PresalesGovernanceOut(OrmBase, PresalesGovernanceBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# # ─────────────────────────────────────────────
# # SALES MODULE
# # ─────────────────────────────────────────────

# class LeadTrackerBase(BaseModel):
#     lead_id: str
#     client_name: str
#     industry: Optional[str] = None
#     lead_source: Optional[str] = None
#     sales_owner: str
#     lead_status: str
#     expected_revenue: float = 0
#     next_followup: Optional[date] = None
#     remarks: Optional[str] = None

# class LeadTrackerCreate(LeadTrackerBase): pass
# class LeadTrackerUpdate(LeadTrackerBase): pass
# class LeadTrackerOut(OrmBase, LeadTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class SalesRevenueTrackerBase(BaseModel):
#     month: str
#     sales_owner: str
#     target_revenue: float = 0
#     achieved_revenue: float = 0
#     variance: float = 0
#     region: Optional[str] = None
#     status: Optional[str] = None
#     remarks: Optional[str] = None

# class SalesRevenueTrackerCreate(SalesRevenueTrackerBase): pass
# class SalesRevenueTrackerUpdate(SalesRevenueTrackerBase): pass
# class SalesRevenueTrackerOut(OrmBase, SalesRevenueTrackerBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None


# class SalesPipelineBase(BaseModel):
#     opportunity_id: str
#     account_name: str
#     vertical: Optional[str] = None
#     opportunity_name: str
#     client_name: str
#     opportunity_owner: str
#     revdau_owner: Optional[str] = None
#     lead_source: Optional[str] = None
#     country: Optional[str] = None
#     region: Optional[str] = None
#     deal_value: float = 0
#     probability_pct: float = 0
#     expected_closure_quarter: Optional[str] = None
#     expected_closure_date: Optional[date] = None
#     status: str
#     risks: Optional[str] = None
#     next_action: Optional[str] = None
#     year: Optional[int] = None

# class SalesPipelineCreate(SalesPipelineBase): pass
# class SalesPipelineUpdate(SalesPipelineBase): pass
# class SalesPipelineOut(OrmBase, SalesPipelineBase):
#     id: int
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None
