from pydantic import computed_field
from pydantic import model_validator
from pydantic import BaseModel, Field, HttpUrl, field_validator, EmailStr
from typing import Optional, List
from datetime import date, datetime, time
import re
from core.schemas import OrmBase
from .models import (
    EmploymentTypeEnum,
    StatusEnum,
    PriorityEnum,
    FeedbackStatusEnum,
    InterviewRoundStatusEnum,
    CompletionStatusEnum,
    EvaluationStatusEnum,
    LinkedInTrackerStatusEnum,
)
from enum import Enum


class DepartmentStatusEnum(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class PartnerEscalationSeverityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class PartnerStatusEnum(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"


class VendorCategoryEnum(str, Enum):
    HR = "Human Resource"
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    MARKETING = "Marketing"
    TRAINING = "Training"
    CONSULTING = "Consulting"
    INFRASTRUCTURE = "Infrastructure"
    OTHER = "Other"


class VendorServiceTypeEnum(str, Enum):
    RESOURCE_HIRING = "Resource Hiring"
    STAFF_AUGMENTATION = "Staff Augmentation"
    HARDWARE_PROCUREMENT = "Hardware Procurement"
    SOFTWARE_LICENSE = "Software License"
    CONSULTING = "Consulting"
    TRAINING = "Training"
    MANAGED_SERVICES = "Managed Services"


class VendorResourceTypeEnum(str, Enum):
    DEVELOPER = "Developer"
    QA_ENGINEER = "QA Engineer"
    DEVOPS_ENGINEER = "DevOps Engineer"
    BUSINESS_ANALYST = "Business Analyst"
    PROJECT_MANAGER = "Project Manager"
    UI_UX_DESIGNER = "UI/UX Designer"
    CONSULTANT = "Consultant"
    TRAINER = "Trainer"
    LAPTOP = "Laptop"
    DESKTOP = "Desktop"
    SERVER = "Server"
    SOFTWARE_LICENSE = "Software License"
    OTHER = "Other"


class DepartmentMasterBase(BaseModel):
    department_code: str
    department_name: str
    status: DepartmentStatusEnum
    remark: Optional[str] = None
    
    @field_validator("department_code")
    @classmethod
    def uppercase_code(cls, v):
        return v.upper() if v else v


class DepartmentMasterCreate(DepartmentMasterBase):
    pass


class DepartmentMasterUpdate(DepartmentMasterBase):
    pass


class DepartmentMasterOut(OrmBase, DepartmentMasterBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None


class DepartmentKPIs(BaseModel):
    total_departments: int = 0
    active_departments: int = 0
    inactive_departments: int = 0


class DepartmentListWithKPIs(BaseModel):
    kpis: DepartmentKPIs
    data: List[DepartmentMasterOut]


class EmployeeBase(BaseModel):
    employee_code: Optional[str] = None
    employee_name: str
    email: EmailStr
    department_id: Optional[int] = None
    designation: str
    manager_id: Optional[int] = None
    location: Optional[str] = None

    # Public/Editable Fields
    mobile_number: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    nationality: Optional[str] = None
    profile_image: Optional[str] = None


class EmployeeProfileOut(OrmBase, EmployeeBase):
    """Schema for what an employee sees in their own profile (e.g., /me)"""
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    department_name: Optional[str] = None
    manager_name: Optional[str] = None

    # Read-only fields for employee
    doj: Optional[date] = None
    date_of_birth: Optional[date] = None
    company_name: Optional[str] = None
    operating_region: Optional[str] = None
    assigned_branch: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    passport_number: Optional[str] = None


class EmployeeProfileUpdate(BaseModel):
    """Schema for fields an employee is allowed to update themselves"""
    mobile_number: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    nationality: Optional[str] = None
    profile_image: Optional[str] = None

    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    passport_number: Optional[str] = None
    pan_document: Optional[str] = None
    aadhar_document: Optional[str] = None
    itr_document: Optional[str] = None
    esic_document: Optional[str] = None

    @field_validator("pan_number", mode="before")
    @classmethod
    def validate_pan(cls, v):
        if not v: return v
        v = str(v).strip().upper()
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", v):
            raise ValueError("Invalid PAN format. Must be 10 characters (e.g., ABCDE1234F)")
        return v

    @field_validator("aadhar_number", mode="before")
    @classmethod
    def validate_aadhar(cls, v):
        if not v: return v
        v = str(v).replace(" ", "").strip()
        if not re.match(r"^\d{12}$", v):
            raise ValueError("Invalid Aadhaar format. Must be exactly 12 digits")
        return v

    @field_validator("passport_number", mode="before")
    @classmethod
    def validate_passport(cls, v):
        if not v: return v
        v = str(v).strip().upper()
        if not re.match(r"^[A-Z0-9]{6,20}$", v):
            raise ValueError("Invalid Passport format. Must be 6 to 20 alphanumeric characters.")
        return v


class HREmployeeBase(EmployeeBase):
    """Extended schema for HR containing all sensitive details"""
    doj: Optional[date] = None
    employment_type: EmploymentTypeEnum
    status: StatusEnum
    remarks: Optional[str] = None
    date_of_birth: Optional[date] = None

    date_of_confirmation: Optional[date] = None
    company_name: Optional[str] = None
    operating_region: Optional[str] = None
    assigned_branch: Optional[str] = None

    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    passport_number: Optional[str] = None

    pan_document: Optional[str] = None
    aadhar_document: Optional[str] = None
    itr_document: Optional[str] = None
    esic_document: Optional[str] = None

    @field_validator("pan_number", mode="before")
    @classmethod
    def validate_pan(cls, v):
        if not v: return v
        v = str(v).strip().upper()
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", v):
            raise ValueError("Invalid PAN format. Must be 10 characters (e.g., ABCDE1234F)")
        return v

    @field_validator("aadhar_number", mode="before")
    @classmethod
    def validate_aadhar(cls, v):
        if not v: return v
        v = str(v).replace(" ", "").strip()
        if not re.match(r"^\d{12}$", v):
            raise ValueError("Invalid Aadhaar format. Must be exactly 12 digits")
        return v

    @field_validator("passport_number", mode="before")
    @classmethod
    def validate_passport(cls, v):
        if not v: return v
        v = str(v).strip().upper()
        if not re.match(r"^[A-Z0-9]{6,20}$", v):
            raise ValueError("Invalid Passport format. Must be 6 to 20 alphanumeric characters.")
        return v


class EmployeeCreate(HREmployeeBase):
    pass


class EmployeeUpdate(HREmployeeBase):
    pass


class EmployeeOut(OrmBase, HREmployeeBase):
    """Full schema returned to HR/Admins"""
    id: int
    user_id: Optional[int] = None
    employee_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    department_name: Optional[str] = None
    manager_name: Optional[str] = None


class EmployeeKPIs(BaseModel):
    total_active: int = 0
    new_joiners_this_month: int = 0
    probation_count: int = 0
    resigned_count: int = 0


class EmployeeListWithKPIs(BaseModel):
    kpis: EmployeeKPIs
    data: List[EmployeeOut]


class LearningTrackerBase(BaseModel):
    employee_id: int
    training_name: str
    training_date: Optional[date] = None
    trainer: str
    certification: Optional[str] = None
    completion_status: CompletionStatusEnum
    remarks: Optional[str] = None

    @field_validator("completion_status", mode="before")
    @classmethod
    def parse_completion_status(cls, v):
        if isinstance(v, str):
            mapping = {
                "INPROGRESS": "inprogress",
                "COMPLETED": "completed",
                "PASS": "Pass",
                "FAILED": "Failed",
                "NOT STARTED": "Not Started",
            }
            return mapping.get(v.upper(), v)
        return v


class LearningTrackerCreate(LearningTrackerBase):
    pass


class LearningTrackerUpdate(LearningTrackerBase):
    pass


class LearningTrackerOut(OrmBase, LearningTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    employee_name: Optional[str] = None


class LearningTrackerKPIs(BaseModel):
    total_learning: int = 0
    total_inprogress: int = 0
    total_pass_completed: int = 0
    total_failed_not_started: int = 0


class LearningTrackerListWithKPIs(BaseModel):
    kpis: LearningTrackerKPIs
    data: List[LearningTrackerOut]


class LinkedInTrackerBase(BaseModel):
    job_title: str
    linkedin_post_date: Optional[date] = None
    job_link: Optional[HttpUrl] = None
    no_of_applicants: int = 0
    engagement_count: int = 0
    last_updated: Optional[date] = None
    status: LinkedInTrackerStatusEnum

    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, v):
        if isinstance(v, str):
            mapping = {
                "ACTIVE": "Active",
                "DRAFT": "Draft",
                "PAUSED": "Paused",
                "CLOSED": "Closed",
            }
            return mapping.get(v.upper(), v)
        return v


class LinkedInTrackerCreate(LinkedInTrackerBase):
    pass


class LinkedInTrackerUpdate(LinkedInTrackerBase):
    pass


class LinkedInTrackerOut(OrmBase, LinkedInTrackerBase):
    id: int
    posting_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LinkedInTrackerKPIs(BaseModel):
    total_posting: int = 0
    total_active_posting: int = 0
    total_applicant_count: int = 0
    total_engagement_count: int = 0


class LinkedInTrackerListWithKPIs(BaseModel):
    kpis: LinkedInTrackerKPIs
    data: List[LinkedInTrackerOut]


class JobEmploymentTypeEnum(str, Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    INTERN = "Intern"


class JobOpeningStatusEnum(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"


class JobOpeningBase(BaseModel):
    job_title: str
    vacancies: Optional[int] = 1
    department_id: Optional[int] = None
    hiring_manager_id: int
    priority: Optional[PriorityEnum] = None
    experience_required: Optional[str] = None
    skills_required: Optional[str] = None
    location: Optional[str] = None
    employment_type: JobEmploymentTypeEnum
    budget_ctc_range: Optional[str] = None
    open_date: Optional[date] = None
    target_closure_date: Optional[date] = None
    current_status: JobOpeningStatusEnum
    recruiter: Optional[str] = None
    linkedin_posted: bool = False
    rounds_count: Optional[int] = 1
    interview_round_names: Optional[str] = None
    remarks: Optional[str] = None

    @field_validator("vacancies", mode="before")
    @classmethod
    def set_default_vacancies(cls, v):
        return v if v is not None else 1

    @field_validator("employment_type", mode="before")
    @classmethod
    def parse_employment_type(cls, v):
        if isinstance(v, str):
            mapping = {
                "FULL TIME": "Full Time",
                "PART TIME": "Part Time",
                "CONTRACT": "Contract",
                "INTERN": "Intern",
            }
            return mapping.get(v.upper(), v)
        return v

    @field_validator("current_status", mode="before")
    @classmethod
    def parse_current_status(cls, v):
        if isinstance(v, str):
            mapping = {
                "OPEN": "Open",
                "CLOSED": "Closed",
                "ON HOLD": "On Hold",
                "CANCELLED": "Cancelled",
            }
            return mapping.get(v.upper(), v)
        return v

    @model_validator(mode="after")
    def validate_recruitment_funnel(self):
        # Date validation
        if self.open_date and self.target_closure_date:
            if self.target_closure_date < self.open_date:
                raise ValueError("Target closure date must be after open date.")

        return self


class JobOpeningCreate(JobOpeningBase):
    pass


class JobOpeningUpdate(JobOpeningBase):
    pass


class JobOpeningRecruitmentMetrics(BaseModel):
    total_applicants: int = 0
    in_progress: int = 0
    offers_released: int = 0
    positions_filled: str = "0/0"
    rejected_candidates: int = 0

class JobOpeningOut(OrmBase, JobOpeningBase):
    id: int
    req_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    department_name: Optional[str] = None
    hiring_manager_name: Optional[str] = None
    public_form_uuid: Optional[str] = None
    application_received_count: int = 0
    recruitment_metrics: Optional[JobOpeningRecruitmentMetrics] = None

    @computed_field
    def aging_days(self) -> int:
        if self.open_date:
            end_date = date.today()
            if self.target_closure_date and self.target_closure_date < end_date:
                end_date = self.target_closure_date
            return (end_date - self.open_date).days
        return 0


class JobOpeningKPIs(BaseModel):
    total_open: int = 0
    critical_positions: int = 0
    closing_soon: int = 0
    total_applications: int = 0


class JobOpeningListWithKPIs(BaseModel):
    kpis: JobOpeningKPIs
    data: List[JobOpeningOut]


class InterviewGovernanceBase(BaseModel):
    candidate_id: Optional[int] = None
    job_opening_id: int
    round: str
    status: Optional[InterviewRoundStatusEnum] = InterviewRoundStatusEnum.SCHEDULED
    interview_date: Optional[date] = None
    interview_time: Optional[time] = None
    interview_mode: Optional[str] = None
    meeting_platform: Optional[str] = None
    meeting_link: Optional[str] = None
    duration_minutes: Optional[int] = None
    instructions: Optional[str] = None


class InterviewGovernanceCreate(InterviewGovernanceBase):
    interviewer_ids: List[int]


class InterviewGovernanceUpdate(InterviewGovernanceBase):
    interviewer_ids: Optional[List[int]] = None


class InterviewGovernanceOut(OrmBase, InterviewGovernanceBase):
    id: int
    interview_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    job_opening_name: Optional[str] = None
    candidate_name: Optional[str] = None
    
class InterviewFeedbackBase(BaseModel):
    interviewer_id: int
    feedback_status: FeedbackStatusEnum
    rating: Optional[int] = Field(None, ge=1, le=5)
    remark: Optional[str] = None

class InterviewFeedbackCreate(InterviewFeedbackBase):
    pass

class InterviewFeedbackUpdate(BaseModel):
    feedback_status: FeedbackStatusEnum
    rating: Optional[int] = Field(None, ge=1, le=5)
    remark: Optional[str] = None

class InterviewFeedbackOut(OrmBase, InterviewFeedbackBase):
    id: int
    interview_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    interviewer_name: Optional[str] = None

class InterviewGovernanceOutWithFeedback(InterviewGovernanceOut):
    feedbacks: List[InterviewFeedbackOut] = []


class InterviewGovernanceKPIs(BaseModel):
    total_pipeline: int = 0
    todays: int = 0
    upcoming: int = 0
    completed: int = 0
    pending_feedback: int = 0


class InterviewGovernanceListWithKPIs(BaseModel):
    kpis: InterviewGovernanceKPIs
    data: List[InterviewGovernanceOutWithFeedback]


class OfferTrackerBase(BaseModel):
    candidate_id: Optional[int] = None
    candidate_name: str
    offered_designation: str
    offered_ctc: str
    joining_date: Optional[date] = None
    location: str
    probation_period: Optional[str] = "6 Months"
    remarks: Optional[str] = None
    status: Optional[str] = "Offer Released"


class OfferTrackerCreate(OfferTrackerBase):
    pass


class OfferTrackerUpdate(OfferTrackerBase):
    pass


class OfferTrackerOut(OrmBase, OfferTrackerBase):
    id: int
    offer_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OfferTrackerKPIs(BaseModel):
    total_offers: int = 0
    pending_offers: int = 0
    offers_accepted: int = 0
    offers_dropped: int = 0


class OfferTrackerListWithKPIs(BaseModel):
    kpis: OfferTrackerKPIs
    data: List[OfferTrackerOut]


class PartnerTrackerBase(BaseModel):
    partner_id: str
    partner_name: str
    partner_type: str
    initiative_name: Optional[str] = None
    partnership_level: Optional[str] = None
    region: Optional[str] = None
    industry_focus: Optional[str] = None
    partnership_start_date: Optional[date] = None
    expiry_date: Optional[date] = None
    agreement_renewal_date: Optional[date] = None
    account_manager_id: Optional[int] = None
    partner_poc_name: str
    contact_number: Optional[str] = None
    email_id: Optional[str] = None
    current_status: PartnerStatusEnum
    last_business_review_date: Optional[date] = None
    next_review_date: Optional[date] = None
    open_action_items: Optional[int] = 0
    open_escalations: Optional[int] = 0
    escalation_severity: Optional[str] = None
    partner_satisfaction_score: Optional[float] = 0.0
    health_status: Optional[str] = None
    risk_identified: Optional[str] = None
    mitigation_plan: Optional[str] = None
    remarks: Optional[str] = None

    @field_validator("current_status", mode="before")
    @classmethod
    def parse_current_status(cls, v):
        if isinstance(v, str):
            mapping = {"ACTIVE": "Active", "INACTIVE": "Inactive", "PENDING": "Pending"}
            return mapping.get(v.upper(), v)
        return v


class PartnerTrackerCreate(PartnerTrackerBase):
    pass


class PartnerTrackerUpdate(PartnerTrackerBase):
    pass


class PartnerTrackerOut(OrmBase, PartnerTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    account_manager_name: Optional[str] = None
    partner_name: Optional[str] = None
    partner_type: Optional[str] = None
    industry_focus: Optional[str] = None
    partner_poc_name: Optional[str] = None
    contact_number: Optional[str] = None
    email_id: Optional[str] = None
    current_status: Optional[str] = None
    last_business_review_date: Optional[date] = None
    next_review_date: Optional[date] = None
    open_action_items: Optional[int] = None
    open_escalations: Optional[int] = None
    escalation_severity: Optional[str] = None
    partner_satisfaction_score: Optional[float] = None
    health_status: Optional[str] = None
    risk_identified: Optional[str] = None
    mitigation_plan: Optional[str] = None


class PartnerTrackerKPIs(BaseModel):
    total_partners: int = 0
    total_active_partners: int = 0


class PartnerTrackerListWithKPIs(BaseModel):
    kpis: PartnerTrackerKPIs
    data: List[PartnerTrackerOut]


class VendorPartnerHiringBase(BaseModel):
    vendor_name: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    primary_contact_email: Optional[str] = None
    vendor_poc_name: Optional[str] = None
    annual_contract_value: Optional[float] = 0.0
    payment_terms: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_expiry_date: Optional[date] = None
    vendor_gstin: Optional[str] = None
    notes: Optional[str] = None
    req_id: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    department_id: Optional[int] = None
    vendor_partner: Optional[str] = None
    vendor_partner_id: Optional[int] = None
    business_unit: Optional[str] = None
    hiring_manager: Optional[str] = None
    hiring_manager_id: Optional[int] = None
    skill_set: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    priority: Optional[str] = None
    no_of_positions: Optional[int] = 1
    budget: Optional[float] = 0.0
    request_date: Optional[date] = None
    target_joining_date: Optional[date] = None
    candidate_name: Optional[str] = None
    resume_received: Optional[str] = "No"
    interview_stage: Optional[str] = None
    interview_date: Optional[date] = None
    interview_feedback: Optional[str] = None
    offer_status: Optional[str] = None
    joining_date: Optional[date] = None
    current_status: Optional[str] = "Open"
    remarks: Optional[str] = None

    @field_validator("annual_contract_value", "budget", mode="before")
    @classmethod
    def default_float_if_none(cls, v):
        return 0.0 if v is None else v

    @field_validator("no_of_positions", mode="before")
    @classmethod
    def default_int_if_none(cls, v):
        return 1 if v is None else v


class VendorPartnerHiringCreate(VendorPartnerHiringBase):
    pass


class VendorPartnerHiringUpdate(VendorPartnerHiringBase):
    pass


class VendorPartnerHiringOut(OrmBase, VendorPartnerHiringBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    department_name: Optional[str] = None
    hiring_manager_name: Optional[str] = None
    vendor_partner_name: Optional[str] = None


class VendorPartnerHiringKPIs(BaseModel):
    total_vendors: int = 0
    total_contract_value: float = 0
    total_requests: int = 0
    high_priority: int = 0
    closed_joined: int = 0
    total_positions: int = 0


class VendorPartnerHiringListWithKPIs(BaseModel):
    kpis: VendorPartnerHiringKPIs
    data: List[VendorPartnerHiringOut]


class InternshipStatusBase(BaseModel):
    intern_name: str
    college: str
    mentor_id: int
    project_assigned: str
    start_date: Optional[date] = None
    evaluation_status: EvaluationStatusEnum


class InternshipStatusCreate(InternshipStatusBase):
    pass


class InternshipStatusUpdate(InternshipStatusBase):
    pass


class InternshipStatusOut(OrmBase, InternshipStatusBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    mentor_name: Optional[str] = None


class InternshipStatusKPIs(BaseModel):
    total_interns: int = 0
    not_started: int = 0
    internship_completed: int = 0
    under_observation: int = 0


class InternshipStatusListWithKPIs(BaseModel):
    kpis: InternshipStatusKPIs
    data: List[InternshipStatusOut]


class BuddyEngagementBase(BaseModel):
    new_joiner_id: int
    buddy_assigned_id: int
    onboarding_progress: Optional[str] = None
    feedback: Optional[str] = None
    engagement_score: float = Field(default=0, ge=0)

    @field_validator("onboarding_progress", mode="before")
    @classmethod
    def validate_progress(cls, v):
        if isinstance(v, (int, float)):
            return f"{v}%"
        if isinstance(v, str) and not v.endswith("%"):
            return f"{v}%" if v.isdigit() else v
        return v


class BuddyEngagementCreate(BuddyEngagementBase):
    pass


class BuddyEngagementUpdate(BuddyEngagementBase):
    pass


class BuddyEngagementOut(OrmBase, BuddyEngagementBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    new_joiner_name: Optional[str] = None
    buddy_assigned_name: Optional[str] = None


class BuddyEngagementKPIs(BaseModel):
    total_engagements: int = 0
    onboarding_completed: int = 0
    in_progress: int = 0
    average_engagement: float = 0


class BuddyEngagementListWithKPIs(BaseModel):
    kpis: BuddyEngagementKPIs
    data: List[BuddyEngagementOut]


class EmployeePerformanceBase(BaseModel):
    employee_id: int
    kras: str
    quarterly_rating: float
    manager_feedback: Optional[str] = None
    improvement_areas: Optional[str] = None
    promotion_readiness: str = Field(..., min_length=1)


class EmployeePerformanceCreate(EmployeePerformanceBase):
    pass


class EmployeePerformanceUpdate(EmployeePerformanceBase):
    pass


class EmployeePerformanceOut(OrmBase, EmployeePerformanceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    employee_name: Optional[str] = None
    quarterly_rating: Optional[float] = None
    promotion_readiness: Optional[str] = None


class EmployeePerformanceKPIs(BaseModel):
    total_reviewed: int = 0


class EmployeePerformanceListWithKPIs(BaseModel):
    kpis: EmployeePerformanceKPIs
    data: List[EmployeePerformanceOut]


class CandidateBase(BaseModel):
    job_opening_id: int
    candidate_name: str
    email: str
    contact_number: str
    experience: str
    skills: str
    resume_url: Optional[str] = None
    current_company: Optional[str] = None
    notice_period: Optional[str] = None
    current_ctc: Optional[str] = None
    expected_ctc: Optional[str] = None
    source: Optional[str] = "Career Site"
    remarks_notes: Optional[str] = None
    status: Optional[str] = "Applied"


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(CandidateBase):
    pass


class CandidateOut(OrmBase, CandidateBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    job_opening_title: Optional[str] = None
