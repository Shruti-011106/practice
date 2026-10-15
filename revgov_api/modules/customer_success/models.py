from sqlalchemy import Column, Integer, String, Float, Date, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from core.models import TimestampMixin


class QBRTracker(TimestampMixin, Base):
    __tablename__ = "qbr_trackers"
    qbr_id = Column(String, unique=True, index=True)
    quarter = Column(String)
    
    customer_id = Column(Integer, ForeignKey("customer_masters.id"))
    customer = relationship("CustomerMaster", foreign_keys=[customer_id], lazy="selectin")
    
    account_owner_id = Column(Integer, ForeignKey("employees.id"))
    account_owner = relationship("Employee", foreign_keys=[account_owner_id], lazy="selectin")
    
    qbr_date = Column(Date, nullable=True)
    review_type = Column(String)
    delivery_performance = Column(String)
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
    
    action_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    action_owner = relationship("Employee", foreign_keys=[action_owner_id], lazy="selectin")
    
    due_date = Column(Date, nullable=True)
    qbr_deck_shared = Column(Boolean, default=False)
    leadership_attendees = Column(Text, nullable=True)
    overall_account_health = Column(String)
    next_qbr_planned_date = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)

    @property
    def customer_partner_name(self):
        return self.customer.customer_name if self.customer else None

    @property
    def account_owner_name(self):
        return self.account_owner.employee_name if self.account_owner else None

    @property
    def action_owner_name(self):
        return self.action_owner.employee_name if self.action_owner else None


class EscalationTracker(TimestampMixin, Base):
    __tablename__ = "escalation_trackers"
    escalation_id = Column(String, unique=True, index=True)
    escalation_date = Column(Date, nullable=True)
    
    customer_id = Column(Integer, ForeignKey("customer_masters.id"))
    customer = relationship("CustomerMaster", foreign_keys=[customer_id], lazy="selectin")
    
    account_owner_id = Column(Integer, ForeignKey("employees.id"))
    account_owner = relationship("Employee", foreign_keys=[account_owner_id], lazy="selectin")
    
    escalation_category = Column(String)
    priority = Column(String)
    issue_summary = Column(Text)
    impact_area = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    immediate_action_taken = Column(Text, nullable=True)
    long_term_resolution_plan = Column(Text, nullable=True)
    
    escalation_owner_id = Column(Integer, ForeignKey("employees.id"))
    escalation_owner = relationship("Employee", foreign_keys=[escalation_owner_id], lazy="selectin")
    
    internal_stakeholders = Column(Text, nullable=True)
    external_stakeholders = Column(Text, nullable=True)
    eta_for_resolution = Column(Integer, nullable=True)
    current_status = Column(String)
    severity_level = Column(String)
    leadership_visibility = Column(Boolean, default=False)
    escalated_to = Column(String, nullable=True)
    closure_date = Column(Date, nullable=True)
    customer_confirmation_received = Column(Boolean, default=False)
    lessons_learned = Column(Text, nullable=True)
    preventive_actions = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)

    @property
    def customer_partner_name(self):
        return self.customer.customer_name if self.customer else None

    @property
    def account_owner_name(self):
        return self.account_owner.employee_name if self.account_owner else None

    @property
    def escalation_owner_name(self):
        return self.escalation_owner.employee_name if self.escalation_owner else None


class ExecutiveContentTracker(TimestampMixin, Base):
    __tablename__ = "executive_content_trackers"
    executive_connect_id = Column(String, unique=True, index=True)
    
    customer_id = Column(Integer, ForeignKey("customer_masters.id"))
    customer = relationship("CustomerMaster", foreign_keys=[customer_id], lazy="selectin")
    
    account_type = Column(String)
    engagement_date = Column(Date, nullable=True)
    meeting_type = Column(String)
    engagement_mode = Column(String, nullable=True)
    
    internal_executive_sponsor_id = Column(Integer, ForeignKey("employees.id"))
    internal_executive_sponsor = relationship("Employee", foreign_keys=[internal_executive_sponsor_id], lazy="selectin")
    
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
    
    action_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    action_owner = relationship("Employee", foreign_keys=[action_owner_id], lazy="selectin")
    
    due_date = Column(Date, nullable=True)
    escalation_required = Column(Boolean, default=False)
    meeting_mom_shared = Column(Boolean, default=False)
    next_executive_connect_date = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)

    @property
    def customer_partner_name(self):
        return self.customer.customer_name if self.customer else None

    @property
    def internal_executive_sponsor_name(self):
        return self.internal_executive_sponsor.employee_name if self.internal_executive_sponsor else None

    @property
    def action_owner_name(self):
        return self.action_owner.employee_name if self.action_owner else None


class CustomerMaster(TimestampMixin, Base):
    __tablename__ = "customer_masters"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    customer_name = Column(String)
    account_type = Column(String)
    account_manager_id = Column(Integer, ForeignKey("employees.id"))
    account_manager = relationship(
        "Employee", foreign_keys=[account_manager_id], lazy="selectin"
    )
    industry = Column(String)
    status = Column(String)
    contract_value = Column(Float, default=0.0)
    country = Column(String, nullable=True)
    remarks = Column(String, nullable=True)

    @property
    def account_manager_name(self):
        return self.account_manager.employee_name if self.account_manager else None
