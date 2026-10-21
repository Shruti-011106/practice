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
from modules.sales.models import LeadTracker
from modules.hr.models import Employee

class ProposalTracker(Base):
    __tablename__ = "proposal_trackers"
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(String, unique=True, index=True)

    presales_bid_id = Column(Integer, ForeignKey("presales_bids.id"), nullable=True)
    presales_bid_details = relationship("PresalesBID", lazy="selectin")

    proposal_name = Column(String)
    customer_submission_date = Column(Date, nullable=True)
    proposal_version = Column(String, nullable=True)
    
    pricing = Column(Float, nullable=True)
    timeline = Column(String, nullable=True)
    assumptions = Column(Text, nullable=True)
    attachments = Column(String, nullable=True)
    internal_approval = Column(String, nullable=True)
    
    status = Column(String)

    approver_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approver_details = relationship("Employee", lazy="selectin")

    remarks_and_scope = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def bid_no(self):
        return self.presales_bid_details.bid_id if self.presales_bid_details else None

    @property
    def client_name(self):
        return self.presales_bid_details.client_name if self.presales_bid_details else None

    @property
    def approver_name(self):
        return self.approver_details.employee_name if self.approver_details else None


class RFPTracker(Base):
    __tablename__ = "rfp_trackers"
    id = Column(Integer, primary_key=True, index=True)
    rfp_id = Column(String, unique=True, index=True)

    lead_id = Column(Integer, ForeignKey("lead_trackers.id"), nullable=True)
    lead_details = relationship("LeadTracker", lazy="selectin")

    submission_date = Column(Date, nullable=True)
    bid_closing_date = Column(Date, nullable=True)

    presales_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    presales_owner_details = relationship("Employee", lazy="selectin")

    solution_type = Column(String)
    document_url = Column(String, nullable=True)
    win_probability = Column(Float, default=0)
    priority = Column(String, nullable=True)
    status = Column(String)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def client_name(self):
        return self.lead_details.client_name if self.lead_details else None

    @property
    def presales_owner(self):
        return (
            self.presales_owner_details.employee_name
            if self.presales_owner_details
            else None
        )


class POCTracker(Base):
    __tablename__ = "poc_trackers"
    id = Column(Integer, primary_key=True, index=True)
    poc_id = Column(String, unique=True, index=True)
    poc_name = Column(String, nullable=True)

    proposal_tracker_id = Column(Integer, ForeignKey("proposal_trackers.id"), nullable=True)
    proposal_details = relationship("ProposalTracker", lazy="selectin")

    technology = Column(String)
    environment = Column(String, nullable=True)
    
    owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    owner_details = relationship("Employee", lazy="selectin")
    
    poc_start_date = Column(Date, nullable=True)
    poc_end_date = Column(Date, nullable=True)
    status = Column(String)
    outcome = Column(String, nullable=True)
    success_percentage = Column(Float, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def client(self):
        return self.proposal_details.client_name if self.proposal_details else None


class PresalesBID(Base):
    __tablename__ = "presales_bids"
    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(String, unique=True, index=True)

    rfp_tracker_id = Column(Integer, ForeignKey("rfp_trackers.id"), nullable=True)
    rfp_details = relationship("RFPTracker", lazy="selectin")

    bid_submission_date = Column(Date, nullable=True)
    bid_decision = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    estimate_revenue = Column(Float, default=0)
    estimate_cost = Column(Float, default=0)
    win_probability = Column(Float, default=0)
    risks = Column(String, nullable=True)
    competitors = Column(String, nullable=True)
    
    approver_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approver_details = relationship("Employee", lazy="selectin")
    
    status = Column(String)  # Pending, Approved, Rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def rfp_no(self):
        return self.rfp_details.rfp_id if self.rfp_details else None

    @property
    def client_name(self):
        return self.rfp_details.lead_details.client_name if self.rfp_details and self.rfp_details.lead_details else None

    @property
    def approver_name(self):
        return (
            self.approver_details.employee_name
            if self.approver_details
            else None
        )


class PresalesDemo(Base):
    __tablename__ = "presales_demos"
    id = Column(Integer, primary_key=True, index=True)
    demo_name = Column(String)

    poc_tracker_id = Column(Integer, ForeignKey("poc_trackers.id"), nullable=True)
    poc_details = relationship("POCTracker", lazy="selectin")

    technology = Column(String)
    business_use_case = Column(Text, nullable=True)

    demo_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    demo_owner_details = relationship("Employee", lazy="selectin")

    status = Column(String)
    demo_url = Column(String, nullable=True)
    credentials = Column(String, nullable=True)
    reusable_for = Column(String, nullable=True)
    last_updated = Column(Date, nullable=True)
    
    demo_date = Column(Date, nullable=True)
    attendees = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    questions = Column(Text, nullable=True)
    outcome = Column(String, nullable=True)
    next_step = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def demo_owner(self):
        return (
            self.demo_owner_details.employee_name if self.demo_owner_details else None
        )


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
