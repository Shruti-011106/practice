from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from sqlalchemy import Enum as SQLAlchemyEnum
from app.db.session import Base

# ─────────────────────────────────────────────
# AUTH MODULE
# ─────────────────────────────────────────────

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    permissions = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", secondary=user_roles, back_populates="roles")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    roles = relationship(
        "Role", secondary=user_roles, back_populates="users", lazy="selectin"
    )


# ─────────────────────────────────────────────
# HR MODULE
# ─────────────────────────────────────────────


class EmploymentTypeEnum(str, enum.Enum):
    INTERN = "Intern"
    PROBATION = "Probation"
    CONFIRMED = "Confirmed"
    CONTRACT = "Contract"
    VENDOR_RESOURCE = "Vendor Resource"
    NOTICE_PERIOD = "Notice Period"
    EXITED = "Exited"


class StatusEnum(str, enum.Enum):
    ACTIVE = "Active"
    ONBOARDING = "Onboarding"
    OFFER_RELEASED = "Offer Released"
    OFFER_ACCEPTED = "Offer Accepted"
    JOINING_AWAITED = "Joining Awaited"
    PROBATION = "Probation"
    CONFIRMED = "Confirmed"
    NOTICE_PERIOD = "Notice Period"
    RESIGNED = "Resigned"
    EXIT_IN_PROGRESS = "Exit in Progress"
    RELIEVED = "Relieved"
    ABSCONDING = "Absconding"
    TERMINATED = "Terminated"
    ONLEAVE = "OnLeave"
    LONGLEAVE = "LongLeave"
    SABBATICAL = "Sabbatical"
    CONTRACTUAL = "Contractual"
    INTERN = "Intern"


class CompletionStatusEnum(str, enum.Enum):
    INPROGRESS = "inprogress"
    COMPLETED = "completed"
    PASS = "Pass"
    FAILED = "Failed"


class JobStatusEnum(str, enum.Enum):
    OPEN = "Open"
    SOURCING = "Sourcing"
    SCREENING = "Screening"
    INTERVIEW_IN_PROGRESS = "Interview In Progress"
    OFFER_RELEASED = "Offer Released"
    POSITION_FILLED = "Position Filled"
    ON_HOLD = "On Hold"
    CANCELLED = "Cancelled"
    CLOSED = "Closed"
    EXPIRED = "Expired"


class OfferDropEnum(str, enum.Enum):
    ACCEPTED = "accepted"
    DROP = "drop"


class PriorityEnum(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class FeedbackStatusEnum(str, enum.Enum):
    SELECTED = "selected"
    NOT_SELECTED = "not selected"
    ON_HOLD = "on hold"


class EvaluationStatusEnum(str, enum.Enum):
    NOT_STARTED = "Not Started"
    UNDER_OBSERVATION = "Under Observation"
    MID_TERM_REVIEW_PENDING = "Mid-Term Review Pending"
    MID_TERM_REVIEW_COMPLETED = "Mid-Term Review Completed"
    PERFORMANCE_EVALUATION_ONGOING = "Performance Evaluation Ongoing"
    TECHNICAL_EVALUATION_COMPLETED = "Technical Evaluation Completed"
    BEHAVIORAL_EVALUATION_COMPLETED = "Behavioral Evaluation Completed"
    MENTOR_FEEDBACK_PENDING = "Mentor Feedback Pending"
    HR_FEEDBACK_PENDING = "HR Feedback Pending"
    FINAL_EVALUATION_PENDING = "Final Evaluation Pending"
    FINAL_EVALUATION_COMPLETED = "Final Evaluation Completed"
    SATISFACTORY = "Satisfactory"
    GOOD_PERFORMANCE = "Good Performance"
    EXCELLENT_PERFORMANCE = "Excellent Performance"
    IMPROVEMENT_REQUIRED = "Improvement Required"
    EXTENSION_RECOMMENDED = "Extension Recommended"
    INTERNSHIP_COMPLETED = "Internship Completed"
    INTERNSHIP_DISCONTINUED = "Internship Discontinued"


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column("employee_id", String, unique=True, index=True)
    employee_name = Column(String)
    department = Column(String)
    designation = Column(String)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    manager = relationship(
        "Employee", remote_side="[Employee.id]", backref="subordinates", lazy="selectin"
    )
    location = Column(String)
    doj = Column(Date, nullable=True)
    employment_type = Column(SQLAlchemyEnum(EmploymentTypeEnum))
    status = Column(SQLAlchemyEnum(StatusEnum))
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LearningTracker(Base):
    __tablename__ = "learning_trackers"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", lazy="selectin")
    training_name = Column(String)
    training_date = Column(Date, nullable=True)
    trainer = Column(String)
    certification = Column(String, nullable=True)
    completion_status = Column(SQLAlchemyEnum(CompletionStatusEnum))
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LinkedInTracker(Base):
    __tablename__ = "linkedin_trackers"
    id = Column(Integer, primary_key=True, index=True)
    posting_id = Column(String, unique=True, index=True)
    job_title = Column(String)
    linkedin_post_date = Column(Date, nullable=True)
    job_link = Column(String, nullable=True)
    no_of_applicants = Column(Integer, default=0)
    engagement_count = Column(Integer, default=0)
    last_updated = Column(Date, nullable=True)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobOpening(Base):
    __tablename__ = "job_openings"
    id = Column(Integer, primary_key=True, index=True)
    req_id = Column(String, unique=True, index=True)
    job_title = Column(String)
    department = Column(String)
    hiring_manager_id = Column(Integer, ForeignKey("employees.id"))
    hiring_manager = relationship(
        "Employee", foreign_keys=[hiring_manager_id], lazy="selectin"
    )
    priority = Column(SQLAlchemyEnum(PriorityEnum), nullable=True)
    experience_required = Column(String)
    skills_required = Column(Text)
    location = Column(String)
    employment_type = Column(SQLAlchemyEnum(EmploymentTypeEnum))
    budget_ctc_range = Column(String, nullable=True)
    open_date = Column(Date, nullable=True)
    target_closure_date = Column(Date, nullable=True)
    current_status = Column(SQLAlchemyEnum(JobStatusEnum))
    recruiter = Column(String)
    linkedin_posted = Column(Boolean, default=False)
    applications_received = Column(Integer, default=0)
    shortlisted = Column(Integer, default=0)
    interviewed = Column(Integer, default=0)
    offered = Column(Integer, default=0)
    joined = Column(Integer, default=0)
    offer_drop = Column(SQLAlchemyEnum(OfferDropEnum), nullable=True)  # accepted / drop
    aging_days = Column(Integer, default=0)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InterviewGovernance(Base):
    __tablename__ = "interview_governance"
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String)
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"))
    job_opening = relationship("JobOpening", lazy="selectin")
    round = Column(String)
    interviewer_id = Column(Integer, ForeignKey("employees.id"))
    interviewer = relationship("Employee", lazy="selectin")
    interview_date = Column(Date, nullable=True)
    feedback_status = Column(SQLAlchemyEnum(FeedbackStatusEnum))
    result = Column(String)
    next_round = Column(String, nullable=True)
    final_decision = Column(String, nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PartnerTracker(Base):
    __tablename__ = "partner_trackers"
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String, unique=True, index=True)
    partner_name = Column(String)
    partner_type = Column(String)
    partnership_level = Column(String)
    region = Column(String)
    industry_focus = Column(String)
    partnership_start_date = Column(Date, nullable=True)
    agreement_renewal_date = Column(Date, nullable=True)
    account_manager = Column(String)
    partner_poc_name = Column(String)
    contact_number = Column(String)
    email_id = Column(String)
    annual_revenue_target = Column(Float, default=0)
    ytd_revenue_generated = Column(Float, default=0)
    pipeline_value = Column(Float, default=0)
    opportunities_open = Column(Integer, default=0)
    opportunities_won = Column(Integer, default=0)
    opportunities_lost = Column(Integer, default=0)
    win_rate_pct = Column(Float, default=0)
    certifications_achieved = Column(Text, nullable=True)
    competency_status = Column(String, nullable=True)
    training_completed = Column(Boolean, default=False)
    certification_expiry_date = Column(Date, nullable=True)
    joint_events_conducted = Column(Integer, default=0)
    webinars_conducted = Column(Integer, default=0)
    marketing_campaigns_executed = Column(Integer, default=0)
    last_business_review_date = Column(Date, nullable=True)
    next_review_date = Column(Date, nullable=True)
    open_action_items = Column(Integer, default=0)
    open_escalations = Column(Integer, default=0)
    escalation_severity = Column(String, nullable=True)
    partner_satisfaction_score = Column(Float, default=0)
    health_status = Column(String, nullable=True)
    risk_identified = Column(Text, nullable=True)
    mitigation_plan = Column(Text, nullable=True)
    current_status = Column(String)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VendorPartnerHiring(Base):
    __tablename__ = "vendor_partner_hirings"
    id = Column(Integer, primary_key=True, index=True)
    partner_name = Column(String)
    skills_provided = Column(Text)
    resources_shared = Column(Integer, default=0)
    sla_adherence = Column(String, nullable=True)
    cost = Column(Float, default=0)
    feedback_score = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InternshipStatus(Base):
    __tablename__ = "internship_statuses"
    id = Column(Integer, primary_key=True, index=True)
    intern_name = Column(String)
    college = Column(String)
    mentor_id = Column(Integer, ForeignKey("employees.id"))
    mentor = relationship("Employee", lazy="selectin")
    project_assigned = Column(String)
    start_date = Column(Date, nullable=True)
    evaluation_status = Column(SQLAlchemyEnum(EvaluationStatusEnum))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BuddyEngagement(Base):
    __tablename__ = "buddy_engagements"
    id = Column(Integer, primary_key=True, index=True)
    new_joiner = Column(String)
    buddy_assigned = Column(String)
    onboarding_progress = Column(String, nullable=True)
    feedback = Column(Text, nullable=True)
    engagement_score = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmployeePerformance(Base):
    __tablename__ = "employee_performances"
    id = Column(Integer, primary_key=True, index=True)
    employee = Column(String)
    kras = Column(Text)
    quarterly_rating = Column(Float, default=0)
    manager_feedback = Column(Text, nullable=True)
    improvement_areas = Column(Text, nullable=True)
    promotion_readiness = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ─────────────────────────────────────────────
# PROJECT GOVERNANCE MODULE
# ─────────────────────────────────────────────


class ProjectGovernance(Base):
    __tablename__ = "project_governances"
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)
    customer = Column(String)
    pm = Column(String)
    delivery_lead = Column(String)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    project_status = Column(String)  # completed / inprogress / on hold
    budget = Column(Float, default=0)
    utilization_pct = Column(Float, default=0)
    milestone_status = Column(String, nullable=True)
    risks = Column(Text, nullable=True)
    escalations = Column(Text, nullable=True)
    dependencies = Column(Text, nullable=True)
    next_milestone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeliverableTracker(Base):
    __tablename__ = "deliverable_trackers"
    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(String, unique=True, index=True)
    project_name = Column(String)
    milestone_name = Column(String)
    deliverable_name = Column(String)
    planned_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)
    status = Column(String)
    dependency = Column(String, nullable=True)
    owner = Column(String)
    delay_reason = Column(Text, nullable=True)
    customer_signoff = Column(Boolean, default=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CustomerSatisfaction(Base):
    __tablename__ = "customer_satisfactions"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    project_name = Column(String)
    feedback_date = Column(Date, nullable=True)
    feedback_type = Column(String)
    csat_score = Column(Float, default=0)
    nps_score = Column(Float, default=0)
    positive_feedback = Column(Text, nullable=True)
    improvement_areas = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    owner = Column(String, nullable=True)
    target_closure_date = Column(Date, nullable=True)
    current_status = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QATracker(Base):
    __tablename__ = "qa_trackers"
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)
    testing_phase = Column(String)
    test_cases_planned = Column(Integer, default=0)
    test_cases_executed = Column(Integer, default=0)
    pass_pct = Column(Float, default=0)
    defect_count = Column(Integer, default=0)
    critical_defects = Column(Integer, default=0)
    reopened_defects = Column(Integer, default=0)
    qa_owner = Column(String)
    golive_readiness = Column(String, nullable=True)
    quality_status = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChangeRequest(Base):
    __tablename__ = "change_requests"
    id = Column(Integer, primary_key=True, index=True)
    cr_id = Column(String, unique=True, index=True)
    project = Column(String)
    description = Column(Text)
    business_impact = Column(Text, nullable=True)
    effort_estimate = Column(String, nullable=True)
    cost_impact = Column(Float, default=0)
    approval_status = Column(String)
    delivery_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ResourceUtilization(Base):
    __tablename__ = "resource_utilizations"
    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String)
    skill = Column(String)
    project_allocation = Column(String, nullable=True)
    billable_pct = Column(Float, default=0)
    utilization_pct = Column(Float, default=0)
    availability = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RAID(Base):
    __tablename__ = "raids"
    id = Column(Integer, primary_key=True, index=True)
    raid_id = Column(String, unique=True, index=True)
    type = Column(String)  # Risk / Assumption / Issue / Dependency
    description = Column(Text)
    impact = Column(Text, nullable=True)
    owner = Column(String)
    mitigation_plan = Column(Text, nullable=True)
    status = Column(String)  # open / closed / inprogress / resolved
    target_closure = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ─────────────────────────────────────────────
# CUSTOMER SUCCESS GOVERNANCE MODULE
# ─────────────────────────────────────────────


class QBRTracker(Base):
    __tablename__ = "qbr_trackers"
    id = Column(Integer, primary_key=True, index=True)
    qbr_id = Column(String, unique=True, index=True)
    quarter = Column(String)
    customer_partner_name = Column(String)
    account_owner = Column(String)
    qbr_date = Column(Date, nullable=True)
    review_type = Column(String)  # virtual / physical
    delivery_performance = Column(String)  # meet expectation / exceed / below
    revenue_achievement = Column(Float, default=0)
    open_risks = Column(Text, nullable=True)
    escalations_discussed = Column(Text, nullable=True)
    csat_score = Column(Float, default=0)
    sla_compliance_pct = Column(Float, default=0)
    key_achievements = Column(Text, nullable=True)
    innovation_initiatives = Column(Text, nullable=True)
    automation_opportunities = Column(Text, nullable=True)
    renewal_status = Column(String)
    expansion_opportunities = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    action_owner = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    qbr_deck_shared = Column(Boolean, default=False)
    leadership_attendees = Column(Text, nullable=True)
    overall_account_health = Column(String)  # Red / Green / Amber
    next_qbr_planned_date = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EscalationTracker(Base):
    __tablename__ = "escalation_trackers"
    id = Column(Integer, primary_key=True, index=True)
    escalation_id = Column(String, unique=True, index=True)
    escalation_date = Column(Date, nullable=True)
    customer_partner_name = Column(String)
    account_owner = Column(String)
    escalation_category = Column(String)
    priority = Column(String)  # P0 / P1 / P2
    issue_summary = Column(Text)
    impact_area = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    immediate_action_taken = Column(Text, nullable=True)
    long_term_resolution_plan = Column(Text, nullable=True)
    escalation_owner = Column(String)
    internal_stakeholders = Column(Text, nullable=True)
    external_stakeholders = Column(Text, nullable=True)
    eta_for_resolution = Column(Integer, nullable=True)  # numeric days
    current_status = Column(String)
    severity_level = Column(String)  # High / Low / Medium
    leadership_visibility = Column(Boolean, default=False)
    escalated_to = Column(String, nullable=True)
    closure_date = Column(Date, nullable=True)
    customer_confirmation_received = Column(Boolean, default=False)
    lessons_learned = Column(Text, nullable=True)
    preventive_actions = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RevenueTracker(Base):
    __tablename__ = "revenue_trackers"
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(String, unique=True, index=True)
    customer_name = Column(String)
    account_manager = Column(String)
    current_contract_value = Column(Float, default=0)
    renewal_due_date = Column(Date, nullable=True)
    renewal_status = Column(String)
    renewal_probability = Column(Boolean, default=False)
    expansion_opportunity = Column(Boolean, default=False)
    potential_revenue = Column(Float, default=0)
    solution_area = Column(String, nullable=True)
    customer_pain_points = Column(Text, nullable=True)
    proposed_solutions = Column(Text, nullable=True)
    competitor_presence = Column(String, nullable=True)
    commercial_discussion_status = Column(String)  # on hold / closed / in progress
    proposal_submitted_date = Column(Date, nullable=True)
    executive_sponsor = Column(String, nullable=True)
    risks = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    next_followup_date = Column(Date, nullable=True)
    deal_stage = Column(String, nullable=True)
    closure_forecast = Column(Date, nullable=True)
    win_loss_status = Column(String, nullable=True)  # win / loss
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ExecutiveContentTracker(Base):
    __tablename__ = "executive_content_trackers"
    id = Column(Integer, primary_key=True, index=True)
    executive_connect_id = Column(String, unique=True, index=True)
    customer_partner_name = Column(String)
    account_type = Column(String)
    engagement_date = Column(Date, nullable=True)
    meeting_type = Column(String)  # online / offline
    engagement_mode = Column(String, nullable=True)
    internal_executive_sponsor = Column(String)
    external_executive_stakeholders = Column(Text, nullable=True)
    business_unit = Column(String, nullable=True)
    strategic_objective = Column(Text, nullable=True)
    discussion_summary = Column(Text, nullable=True)
    strategic_priorities_discussed = Column(Text, nullable=True)
    key_decisions_taken = Column(Text, nullable=True)
    risks_highlighted = Column(Text, nullable=True)
    opportunities_identified = Column(Text, nullable=True)
    commitments_made = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    action_owner = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    escalation_required = Column(Boolean, default=False)
    meeting_mom_shared = Column(Boolean, default=False)
    next_executive_connect_date = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ─────────────────────────────────────────────
# FINANCE & PROCUREMENT MODULE
# ─────────────────────────────────────────────


class POTracker(Base):
    __tablename__ = "po_trackers"
    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, index=True)
    vendor_name = Column(String)
    po_date = Column(Date, nullable=True)
    amount = Column(Float, default=0)
    department = Column(String)
    approval_status = Column(String)
    payment_status = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InvoiceTracker(Base):
    __tablename__ = "invoice_trackers"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True)
    vendor = Column(String)
    invoice_date = Column(Date, nullable=True)
    invoice_amount = Column(Float, default=0)
    due_date = Column(Date, nullable=True)
    payment_status = Column(String)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BudgetTracker(Base):
    __tablename__ = "budget_trackers"
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String)
    budget_allocated = Column(Float, default=0)
    budget_utilized = Column(Float, default=0)
    remaining_budget = Column(Float, default=0)
    quarter = Column(String)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ─────────────────────────────────────────────
# LEARNING & DEVELOPMENT MODULE
# ─────────────────────────────────────────────


class ReusableAsset(Base):
    __tablename__ = "reusable_assets"
    id = Column(Integer, primary_key=True, index=True)
    asset_name = Column(String)
    category = Column(String)
    technology = Column(String, nullable=True)
    owner = Column(String)
    version = Column(String, nullable=True)
    document_name = Column(String, nullable=True)
    document_type = Column(String, nullable=True)
    upload = Column(String, nullable=True)
    repository_link = Column(String, nullable=True)
    maturity_level = Column(String, nullable=True)
    approval_status = Column(String, nullable=True)
    last_review_date = Column(Date, nullable=True)
    tag = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Knowledge Repository - Merged into Reusable Asset (Temporarily Disabled)
# class KnowledgeRepo(Base):
#     __tablename__ = "knowledge_repos"
#     id = Column(Integer, primary_key=True, index=True)
#     document_name = Column(String)
#     category = Column(String)
#     team = Column(String)
#     owner = Column(String)
#     approval_status = Column(String)
#     last_review_date = Column(Date, nullable=True)
#     tag = Column(String, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CapabilityBuilding(Base):
    __tablename__ = "capability_buildings"
    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String)
    current_skill = Column(String)
    target_skill = Column(String)
    certification_planned = Column(String, nullable=True)
    completion_status = Column(String)
    skill_level = Column(String, nullable=True)
    business_alignment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PartnershipAlliance(Base):
    __tablename__ = "partnership_alliances"
    id = Column(Integer, primary_key=True, index=True)
    partner_name = Column(String)
    alliance_owner = Column(String)
    partnership_type = Column(String)
    joint_opportunities = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
    gtm_activities = Column(Text, nullable=True)
    revenue_contribution = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechCapability(Base):
    __tablename__ = "tech_capabilities"
    id = Column(Integer, primary_key=True, index=True)
    technology = Column(String)
    practice_owner = Column(String)
    certified_resources = Column(Integer, default=0)
    active_projects = Column(Integer, default=0)
    readiness_score = Column(Float, default=0)
    strategic_priority = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InnovationAutomation(Base):
    __tablename__ = "innovation_automations"
    id = Column(Integer, primary_key=True, index=True)
    innovation_name = Column(String)
    team = Column(String)
    automation_type = Column(String)
    productivity_gain = Column(String, nullable=True)
    status = Column(String)
    business_benefit = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TrainingTracker(Base):
    __tablename__ = "training_trackers"
    id = Column(Integer, primary_key=True, index=True)
    training_name = Column(String)
    team = Column(String)
    planned_date = Column(Date, nullable=True)
    completion_pct = Column(Float, default=0)
    certification_status = Column(String, nullable=True)
    kpi_impact = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ─────────────────────────────────────────────
# MARKETING MODULE
# ─────────────────────────────────────────────


class EventWebinar(Base):
    __tablename__ = "event_webinars"
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String)
    date = Column(Date, nullable=True)
    owner = Column(String)
    participants = Column(Integer, default=0)
    leads_generated = Column(Integer, default=0)
    followup_status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ContentBranding(Base):
    __tablename__ = "content_brandings"
    id = Column(Integer, primary_key=True, index=True)
    asset_name = Column(String)
    type = Column(String)
    owner = Column(String)
    approval_status = Column(String)
    reusability = Column(Boolean, default=False)
    last_updated = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String)
    campaign_owner = Column(String)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(Float, default=0)
    leads_generated = Column(Integer, default=0)
    roi = Column(Float, default=0)
    target_audience = Column(String, nullable=True)
    status = Column(String)  # completed / incomplete / on hold
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ─────────────────────────────────────────────
# PRESALES MODULE
# ─────────────────────────────────────────────


class ProposalTracker(Base):
    __tablename__ = "proposal_trackers"
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(String, unique=True, index=True)
    client = Column(String)
    proposal_name = Column(String)
    submission_date = Column(Date, nullable=True)
    version = Column(String, nullable=True)
    proposal_status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RFPTracker(Base):
    __tablename__ = "rfp_trackers"
    id = Column(Integer, primary_key=True, index=True)
    rfp_id = Column(String, unique=True, index=True)
    client_name = Column(String)
    submission_date = Column(Date, nullable=True)
    presales_owner = Column(String)
    solution_type = Column(String)
    status = Column(String)
    win_probability = Column(Float, default=0)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class POCTracker(Base):
    __tablename__ = "poc_trackers"
    id = Column(Integer, primary_key=True, index=True)
    poc_id = Column(String, unique=True, index=True)
    client = Column(String)
    technology = Column(String)
    environment = Column(String, nullable=True)
    poc_start_date = Column(Date, nullable=True)
    poc_end_date = Column(Date, nullable=True)
    status = Column(String)
    outcome = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PresalesBID(Base):
    __tablename__ = "presales_bids"
    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(String, unique=True, index=True)
    client = Column(String)
    rfp_rfi = Column(String, nullable=True)
    bid_submission_date = Column(Date, nullable=True)
    solution_architect = Column(String)
    demo_required = Column(Boolean, default=False)
    proposal_status = Column(String)
    dependencies = Column(Text, nullable=True)
    review_status = Column(String, nullable=True)
    win_loss_status = Column(String, nullable=True)  # win / loss
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PresalesDemo(Base):
    __tablename__ = "presales_demos"
    id = Column(Integer, primary_key=True, index=True)
    demo_name = Column(String)
    technology = Column(String)
    business_use_case = Column(Text, nullable=True)
    demo_owner = Column(String)
    status = Column(String)
    demo_url = Column(String, nullable=True)
    credentials = Column(String, nullable=True)
    reusable_for = Column(String, nullable=True)
    last_updated = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PresalesGovernance(Base):
    __tablename__ = "presales_governances"
    id = Column(Integer, primary_key=True, index=True)
    asset_name = Column(String)
    category = Column(String)
    technology = Column(String)
    demo_ready = Column(Boolean, default=False)
    reusable = Column(Boolean, default=False)
    last_used = Column(Date, nullable=True)
    business_impact = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ─────────────────────────────────────────────
# SALES MODULE
# ─────────────────────────────────────────────


class LeadTracker(Base):
    __tablename__ = "lead_trackers"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(String, unique=True, index=True)
    client_name = Column(String)
    industry = Column(String, nullable=True)
    lead_source = Column(String, nullable=True)
    sales_owner = Column(String)
    lead_status = Column(String)
    expected_revenue = Column(Float, default=0)
    next_followup = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SalesRevenueTracker(Base):
    __tablename__ = "sales_revenue_trackers"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String)
    sales_owner = Column(String)
    target_revenue = Column(Float, default=0)
    achieved_revenue = Column(Float, default=0)
    variance = Column(Float, default=0)
    region = Column(String, nullable=True)
    status = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SalesPipeline(Base):
    __tablename__ = "sales_pipelines"
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(String, unique=True, index=True)
    account_name = Column(String)
    vertical = Column(String, nullable=True)
    opportunity_name = Column(String)
    client_name = Column(String)
    opportunity_owner = Column(String)
    revdau_owner = Column(String, nullable=True)
    lead_source = Column(String, nullable=True)
    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    deal_value = Column(Float, default=0)
    probability_pct = Column(Float, default=0)
    expected_closure_quarter = Column(String, nullable=True)
    expected_closure_date = Column(Date, nullable=True)
    status = Column(String)
    risks = Column(Text, nullable=True)
    next_action = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
