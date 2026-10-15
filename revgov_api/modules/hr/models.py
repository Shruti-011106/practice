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
    Time,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, column_property
import enum
from sqlalchemy import Enum as SQLAlchemyEnum, select
from core.database import Base


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
    NOT_STARTED = "Not Started"


class LinkedInTrackerStatusEnum(str, enum.Enum):
    ACTIVE = "Active"
    DRAFT = "Draft"
    PAUSED = "Paused"
    CLOSED = "Closed"


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
    DROP = "dropped"


class PriorityEnum(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class FeedbackStatusEnum(str, enum.Enum):
    PENDING = "pending"
    SELECTED = "selected"
    NOT_SELECTED = "not selected"
    ON_HOLD = "on hold"

class InterviewRoundStatusEnum(str, enum.Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


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
    email = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    department_id = Column(Integer, ForeignKey("department_masters.id"), nullable=True)
    department_details = relationship("DepartmentMaster", lazy="selectin")
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
    
    # Personal Details
    mobile_number = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    # Job & Position additions
    date_of_confirmation = Column(Date, nullable=True)
    company_name = Column(String, nullable=True, default=None)
    operating_region = Column(String, nullable=True)
    assigned_branch = Column(String, nullable=True)

    # Documents & Verifications
    pan_number = Column(String, nullable=True)
    aadhar_number = Column(String, nullable=True)
    passport_number = Column(String, nullable=True)
    
    # Uploaded Documents URLs
    profile_image = Column(String, nullable=True)
    pan_document = Column(String, nullable=True)
    aadhar_document = Column(String, nullable=True)
    itr_document = Column(String, nullable=True)
    esic_document = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def department_name(self):
        return (
            self.department_details.department_name if self.department_details else None
        )

    @property
    def manager_name(self):
        return self.manager.employee_name if self.manager else None


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

    @property
    def employee_name(self):
        return self.employee.employee_name if self.employee else None


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
    vacancies = Column(Integer, default=1)
    department_id = Column(Integer, ForeignKey("department_masters.id"), nullable=True)
    department_details = relationship("DepartmentMaster", lazy="selectin")
    hiring_manager_id = Column(Integer, ForeignKey("employees.id"))
    hiring_manager = relationship(
        "Employee", foreign_keys=[hiring_manager_id], lazy="selectin"
    )
    priority = Column(SQLAlchemyEnum(PriorityEnum), nullable=True)
    experience_required = Column(String)
    skills_required = Column(Text)
    location = Column(String)
    employment_type = Column(String)
    budget_ctc_range = Column(String, nullable=True)
    open_date = Column(Date, nullable=True)
    target_closure_date = Column(Date, nullable=True)
    current_status = Column(String)
    recruiter = Column(String)
    linkedin_posted = Column(Boolean, default=False)
    public_form_uuid = Column(String(36), unique=True, index=True, nullable=True)
    aging_days = Column(Integer, default=0)
    rounds_count = Column(Integer, default=1, nullable=True)
    interview_round_names = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def department_name(self):
        return (
            self.department_details.department_name if self.department_details else None
        )

    @property
    def hiring_manager_name(self):
        return self.hiring_manager.employee_name if self.hiring_manager else None


class InterviewGovernance(Base):
    __tablename__ = "interview_governance"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(String, unique=True, index=True, nullable=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True)
    candidate = relationship("Candidate", lazy="selectin", foreign_keys=[candidate_id])
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"))
    job_opening = relationship("JobOpening", lazy="selectin")
    round = Column(String)
    status = Column(SQLAlchemyEnum(InterviewRoundStatusEnum), default=InterviewRoundStatusEnum.SCHEDULED)
    interview_date = Column(Date, nullable=True)
    interview_time = Column(Time, nullable=True)
    interview_mode = Column(String, nullable=True)
    meeting_platform = Column(String, nullable=True)
    meeting_link = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    instructions = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    feedbacks = relationship("InterviewFeedback", back_populates="interview", cascade="all, delete-orphan", lazy="selectin")

    @property
    def job_opening_name(self):
        return self.job_opening.job_title if self.job_opening else None

    @property
    def candidate_name(self):
        return self.candidate.candidate_name if self.candidate else None


class InterviewFeedback(Base):
    __tablename__ = "interview_feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interview_governance.id", ondelete="CASCADE"))
    interviewer_id = Column(Integer, ForeignKey("employees.id"))
    
    interview = relationship("InterviewGovernance", back_populates="feedbacks")
    interviewer = relationship("Employee", lazy="selectin")
    
    feedback_status = Column(SQLAlchemyEnum(FeedbackStatusEnum), default=FeedbackStatusEnum.PENDING)
    rating = Column(Integer, nullable=True)
    remark = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def interviewer_name(self):
        return self.interviewer.employee_name if self.interviewer else None


class OfferTracker(Base):
    __tablename__ = "offer_trackers"
    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(String, unique=True, index=True, nullable=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True)
    candidate = relationship("Candidate", lazy="selectin")
    candidate_name = Column(String)
    offered_designation = Column(String)
    offered_ctc = Column(String)
    joining_date = Column(Date, nullable=True)
    location = Column(String)
    probation_period = Column(String, default="6 Months", nullable=True)
    remarks = Column(Text, nullable=True)
    status = Column(String, default="Offer Released")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PartnerTracker(Base):
    __tablename__ = "partner_trackers"
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String, unique=True, index=True)
    partner_name = Column(String)
    partner_type = Column(String)
    initiative_name = Column(String, nullable=True)
    partnership_level = Column(String)
    region = Column(String)
    industry_focus = Column(String)
    partnership_start_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    agreement_renewal_date = Column(Date, nullable=True)
    account_manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    account_manager = relationship("Employee", lazy="selectin")

    @property
    def account_manager_name(self):
        return self.account_manager.employee_name if self.account_manager else None

    partner_poc_name = Column(String)
    contact_number = Column(String)
    email_id = Column(String)
    current_status = Column(String)
    last_business_review_date = Column(Date, nullable=True)
    next_review_date = Column(Date, nullable=True)
    open_action_items = Column(Integer, default=0)
    open_escalations = Column(Integer, default=0)
    escalation_severity = Column(String, nullable=True)
    partner_satisfaction_score = Column(Integer, nullable=True)
    health_status = Column(String, nullable=True)
    risk_identified = Column(String, nullable=True)
    mitigation_plan = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VendorPartnerHiring(Base):
    __tablename__ = "vendor_partner_hirings"
    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String, nullable=True)
    category = Column(String, nullable=True)
    country = Column(String, nullable=True)
    primary_contact_email = Column(String, nullable=True)
    vendor_poc_name = Column(String, nullable=True)
    annual_contract_value = Column(Float, default=0.0)
    payment_terms = Column(String, nullable=True)
    contract_start_date = Column(Date, nullable=True)
    contract_expiry_date = Column(Date, nullable=True)
    vendor_gstin = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    req_id = Column(String, unique=True, index=True, nullable=True)
    role = Column(String, nullable=True)
    department = Column(String, nullable=True)
    vendor_partner = Column(String, nullable=True)
    business_unit = Column(String, nullable=True)
    hiring_manager = Column(String, nullable=True)
    skill_set = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    employment_type = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    no_of_positions = Column(Integer, default=1)
    budget = Column(Float, default=0.0)
    request_date = Column(Date, nullable=True)
    target_joining_date = Column(Date, nullable=True)
    candidate_name = Column(String, nullable=True)
    resume_received = Column(String, default="No", nullable=True)
    interview_stage = Column(String, nullable=True)
    interview_date = Column(Date, nullable=True)
    interview_feedback = Column(Text, nullable=True)
    offer_status = Column(String, nullable=True)
    joining_date = Column(Date, nullable=True)
    current_status = Column(String, default="Open", nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    department_id = Column(Integer, ForeignKey("department_masters.id"), nullable=True)
    department_details = relationship("DepartmentMaster", lazy="selectin")
    hiring_manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    hiring_manager_details = relationship(
        "Employee", foreign_keys=[hiring_manager_id], lazy="selectin"
    )
    vendor_partner_id = Column(Integer, ForeignKey("partner_trackers.id"), nullable=True)
    vendor_partner_details = relationship(
        "PartnerTracker", foreign_keys=[vendor_partner_id], lazy="selectin"
    )

    @property
    def department_name(self):
        return (
            self.department_details.department_name
            if self.department_details
            else self.department
        )

    @property
    def hiring_manager_name(self):
        return (
            self.hiring_manager_details.employee_name
            if self.hiring_manager_details
            else self.hiring_manager
        )

    @property
    def vendor_partner_name(self):
        return (
            self.vendor_partner_details.partner_name
            if self.vendor_partner_details
            else self.vendor_partner
        )


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

    @property
    def mentor_name(self):
        return self.mentor.employee_name if self.mentor else None


class BuddyEngagement(Base):
    __tablename__ = "buddy_engagements"
    id = Column(Integer, primary_key=True, index=True)
    new_joiner_id = Column(Integer, ForeignKey("employees.id"))
    new_joiner = relationship("Employee", foreign_keys=[new_joiner_id], lazy="selectin")
    buddy_assigned_id = Column(Integer, ForeignKey("employees.id"))
    buddy_assigned = relationship(
        "Employee", foreign_keys=[buddy_assigned_id], lazy="selectin"
    )
    onboarding_progress = Column(String, nullable=True)
    feedback = Column(Text, nullable=True)
    engagement_score = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def new_joiner_name(self):
        return self.new_joiner.employee_name if self.new_joiner else None

    @property
    def buddy_assigned_name(self):
        return self.buddy_assigned.employee_name if self.buddy_assigned else None


class EmployeePerformance(Base):
    __tablename__ = "employee_performances"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", foreign_keys=[employee_id], lazy="selectin")
    kras = Column(Text)
    quarterly_rating = Column(Float, default=0)
    manager_feedback = Column(Text, nullable=True)
    improvement_areas = Column(Text, nullable=True)
    promotion_readiness = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def employee_name(self):
        return self.employee.employee_name if self.employee else None


class DepartmentMaster(Base):
    __tablename__ = "department_masters"
    id = Column(Integer, primary_key=True, index=True)
    department_code = Column(String, unique=True, index=True)
    department_name = Column(String)
    status = Column(String)
    remark = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"))
    job_opening = relationship("JobOpening", lazy="selectin")
    candidate_name = Column(String)
    email = Column(String)
    contact_number = Column(String, nullable=True)
    experience = Column(String, nullable=True)
    skills = Column(Text, nullable=True)
    resume_url = Column(String, nullable=True)
    current_company = Column(String, nullable=True)
    notice_period = Column(String, nullable=True)
    current_ctc = Column(String, nullable=True)
    expected_ctc = Column(String, nullable=True)
    source = Column(String, default="Career Site", nullable=True)
    remarks_notes = Column(Text, nullable=True)
    status = Column(String, default="Applied")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def job_opening_title(self):
        return self.job_opening.job_title if self.job_opening else None


JobOpening.application_received_count = column_property(
    select(func.count(Candidate.id))
    .where(Candidate.job_opening_id == JobOpening.id)
    .correlate_except(Candidate)
    .scalar_subquery()
)
