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
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class ProjectGovernance(Base):
    __tablename__ = "project_governances"
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)

    # Master Lookups
    customer_id = Column(Integer, ForeignKey("customer_masters.id"))
    customer_details = relationship("CustomerMaster", lazy="selectin")

    pm_id = Column(Integer, ForeignKey("employees.id"))
    pm = relationship("Employee", foreign_keys=[pm_id], lazy="selectin")

    delivery_lead_id = Column(Integer, ForeignKey("employees.id"))
    delivery_lead = relationship(
        "Employee", foreign_keys=[delivery_lead_id], lazy="selectin"
    )

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    project_status = Column(String)  # completed / inprogress / on hold
    budget = Column(Float, default=0)

    # Auto Calculated Fields
    utilization_pct = Column(Float, default=0)
    milestone_status = Column(String, nullable=True)
    risks = Column(Integer, default=0)  # Changed from Text to Auto Count
    escalations = Column(Integer, default=0)  # Changed from Text to Auto Count
    dependencies = Column(Integer, default=0)  # Changed from Text to Auto Count
    next_milestone = Column(String, nullable=True)
    key_delivery_risks = Column(Text, nullable=True)
    active_escalations = Column(Text, nullable=True)
    critical_dependencies = Column(Text, nullable=True)

    # Relationships to Child Trackers
    deliverables = relationship(
        "DeliverableTracker", back_populates="project", lazy="selectin"
    )
    csat = relationship(
        "CustomerSatisfaction", back_populates="project", lazy="selectin"
    )
    qa_trackers = relationship("QATracker", back_populates="project", lazy="selectin")
    change_requests = relationship(
        "ChangeRequest", back_populates="project", lazy="selectin"
    )
    resources = relationship(
        "ResourceUtilization", back_populates="project", lazy="selectin"
    )
    raids = relationship("RAID", back_populates="project", lazy="selectin")
    vendor_subcontractors = relationship(
        "VendorSubcontractorGovernance", back_populates="project", lazy="selectin"
    )
    milestone_billings = relationship(
        "MilestoneBilling", back_populates="project", lazy="selectin"
    )
    project_closures = relationship(
        "ProjectClosure", back_populates="project", lazy="selectin"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def customer_name(self):
        return self.customer_details.customer_name if self.customer_details else None

    @property
    def pm_name(self):
        return self.pm.employee_name if self.pm else None

    @property
    def delivery_lead_name(self):
        return self.delivery_lead.employee_name if self.delivery_lead else None


class DeliverableTracker(Base):
    __tablename__ = "deliverable_trackers"
    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(String, unique=True, index=True)

    project_id = Column(Integer, ForeignKey("project_governances.id"))
    project = relationship("ProjectGovernance", back_populates="deliverables")

    milestone_name = Column(String)
    deliverable_name = Column(String)
    planned_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)
    status = Column(String)
    dependency = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("employees.id"))
    owner = relationship("Employee", lazy="selectin")

    delay_reason = Column(Text, nullable=True)
    customer_signoff = Column(Boolean, default=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def project_name(self):
        return self.project.project_name if self.project else None

    @property
    def owner_name(self):
        return self.owner.employee_name if self.owner else None


class CustomerSatisfaction(Base):
    __tablename__ = "customer_satisfactions"
    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, ForeignKey("customer_masters.id"))
    customer = relationship("CustomerMaster", lazy="selectin")

    project_id = Column(Integer, ForeignKey("project_governances.id"))
    project = relationship("ProjectGovernance", back_populates="csat")

    feedback_date = Column(Date, nullable=True)
    feedback_type = Column(String)
    csat_score = Column(Float, default=0)
    nps_score = Column(Float, default=0)
    positive_feedback = Column(Text, nullable=True)
    improvement_areas = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("employees.id"))
    owner = relationship("Employee", lazy="selectin")

    target_closure_date = Column(Date, nullable=True)
    current_status = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def customer_name(self):
        return self.customer.customer_name if self.customer else None

    @property
    def project_name(self):
        return self.project.project_name if self.project else None

    @property
    def owner_name(self):
        return self.owner.employee_name if self.owner else None


class QATracker(Base):
    __tablename__ = "qa_trackers"
    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("project_governances.id"))
    project = relationship("ProjectGovernance", back_populates="qa_trackers")

    testing_phase = Column(String)
    test_cases_planned = Column(Integer, default=0)
    test_cases_executed = Column(Integer, default=0)
    pass_pct = Column(Float, default=0)
    defect_count = Column(Integer, default=0)
    critical_defects = Column(Integer, default=0)
    reopened_defects = Column(Integer, default=0)

    owner_id = Column(Integer, ForeignKey("employees.id"))
    owner = relationship("Employee", lazy="selectin")

    golive_readiness = Column(String, nullable=True)
    quality_status = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def project_name(self):
        return self.project.project_name if self.project else None

    @property
    def owner_name(self):
        return self.owner.employee_name if self.owner else None


class ChangeRequest(Base):
    __tablename__ = "change_requests"
    id = Column(Integer, primary_key=True, index=True)
    cr_id = Column(String, unique=True, index=True)

    project_id = Column(Integer, ForeignKey("project_governances.id"))
    project = relationship("ProjectGovernance", back_populates="change_requests")

    description = Column(Text)
    business_impact = Column(Text, nullable=True)
    effort_estimate = Column(String, nullable=True)
    cost_impact = Column(Float, default=0)
    approval_status = Column(String)
    delivery_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def project_name(self):
        return self.project.project_name if self.project else None


class ResourceUtilization(Base):
    __tablename__ = "resource_utilizations"
    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", lazy="selectin")

    skill = Column(String)
    role = Column(String, nullable=True)

    project_id = Column(Integer, ForeignKey("project_governances.id"), nullable=True)
    project = relationship("ProjectGovernance", back_populates="resources")

    billable_pct = Column(Float, default=0)
    utilization_pct = Column(Float, default=0)
    allocation_status = Column(String, default="Active")
    assigned_on = Column(Date, nullable=True)
    release_date = Column(Date, nullable=True)
    bench_status = Column(String, nullable=True)
    availability = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def employee_name(self):
        return self.employee.employee_name if self.employee else None

    @property
    def project_name(self):
        return self.project.project_name if self.project else None


class RAID(Base):
    __tablename__ = "raids"
    id = Column(Integer, primary_key=True, index=True)
    raid_id = Column(String, unique=True, index=True)

    project_id = Column(Integer, ForeignKey("project_governances.id"))
    project = relationship("ProjectGovernance", back_populates="raids")

    type = Column(String)  # Risk / Assumption / Issue / Dependency
    description = Column(Text)
    impact = Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("employees.id"))
    owner = relationship("Employee", lazy="selectin")

    mitigation_plan = Column(Text, nullable=True)
    status = Column(String)  # open / closed / inprogress / resolved
    target_closure = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def project_name(self):
        return self.project.project_name if self.project else None

    @property
    def owner_name(self):
        return self.owner.employee_name if self.owner else None


class VendorSubcontractorGovernance(Base):
    __tablename__ = "vendor_subcontractor_governances"
    id = Column(Integer, primary_key=True, index=True)
    vendor_gov_id = Column(String, unique=True, index=True)

    project_id = Column(Integer, ForeignKey("project_governances.id"))
    project = relationship(
        "ProjectGovernance", back_populates="vendor_subcontractors", lazy="selectin"
    )

    vendor_id = Column(Integer, ForeignKey("partner_trackers.id"))
    vendor = relationship("PartnerTracker", lazy="selectin")

    subcontractor_agency_name = Column(String, nullable=True)
    contract_status = Column(String, default="Active")
    sla_target_rating = Column(String, nullable=True, default="90%")
    allocated_budget = Column(Float, default=0.0)
    subcontractor_scope_of_work = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def project_name(self):
        return self.project.project_name if self.project else None

    @property
    def vendor_name(self):
        return self.vendor.partner_name if self.vendor else None


class MilestoneBilling(Base):
    __tablename__ = "milestone_billings"
    id = Column(Integer, primary_key=True, index=True)
    billing_id = Column(String, unique=True, index=True)

    project_id = Column(Integer, ForeignKey("project_governances.id"))
    project = relationship(
        "ProjectGovernance", back_populates="milestone_billings", lazy="selectin"
    )

    amount = Column(Float, default=0.0)
    invoice_status = Column(String, default="Pending")
    realization_date = Column(Date, nullable=True)
    milestone_scope = Column(Text)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def project_name(self):
        return self.project.project_name if self.project else None


class ProjectClosure(Base):
    __tablename__ = "project_closures"
    id = Column(Integer, primary_key=True, index=True)
    closure_id = Column(String, unique=True, index=True)

    project_id = Column(Integer, ForeignKey("project_governances.id"))
    project = relationship(
        "ProjectGovernance", back_populates="project_closures", lazy="selectin"
    )

    closure_date = Column(Date)
    closure_status = Column(String, default="Initiated")
    asset_handover_status = Column(String, default="Pending")
    csat_rating = Column(Float, default=0.0)
    retrospective_summary = Column(Text)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def project_name(self):
        return self.project.project_name if self.project else None
