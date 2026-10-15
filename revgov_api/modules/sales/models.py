from sqlalchemy import Column, Integer, String, Float, Date, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class LeadTracker(Base):
    __tablename__ = "lead_trackers"
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(String, unique=True, index=True)
    client_name = Column(String)
    industry = Column(String, nullable=True)
    lead_source = Column(String, nullable=True)

    country = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    expected_budget = Column(Float, default=0)
    expected_timeline = Column(String, nullable=True)

    sales_owner_id = Column(Integer, ForeignKey("employees.id"))
    sales_owner_details = relationship("Employee", foreign_keys=[sales_owner_id], lazy="selectin")
    
    presales_engineer_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    presales_engineer_details = relationship("Employee", foreign_keys=[presales_engineer_id], lazy="selectin")

    lead_status = Column(String)
    expected_revenue = Column(Float, default=0)
    next_followup = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def sales_owner(self):
        return (
            self.sales_owner_details.employee_name if self.sales_owner_details else None
        )

    @property
    def assigned_presales_engineer(self):
        return (
            self.presales_engineer_details.employee_name if self.presales_engineer_details else None
        )


class SalesRevenueTracker(Base):
    __tablename__ = "sales_revenue_trackers"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String)

    pipeline_id = Column(Integer, ForeignKey("sales_pipelines.id"), nullable=True)
    pipeline_details = relationship("SalesPipeline", lazy="selectin")

    revenue_owner_id = Column(Integer, ForeignKey("employees.id"))
    revenue_owner_details = relationship("Employee", lazy="selectin")

    deal_value = Column(Float, default=0)
    invoice = Column(Float, default=0)
    collected = Column(Float, default=0)
    pending = Column(Float, default=0)
    forecast = Column(Float, default=0)
    quarter = Column(String, nullable=True)
    status = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def revenue_owner(self):
        return (
            self.revenue_owner_details.employee_name if self.revenue_owner_details else None
        )


class SalesPipeline(Base):
    __tablename__ = "sales_pipelines"
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(String, unique=True, index=True)

    lead_id = Column(Integer, ForeignKey("lead_trackers.id"), nullable=True)
    lead_details = relationship("LeadTracker", foreign_keys=[lead_id], lazy="selectin")

    demo_tracker_id = Column(Integer, ForeignKey("presales_demos.id"), nullable=True)
    demo_details = relationship("PresalesDemo", lazy="selectin")

    account_name = Column(String)
    vertical = Column(String, nullable=True)
    opportunity_name = Column(String)

    opportunity_owner = Column(String, nullable=True)

    revdau_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    revdau_owner_details = relationship(
        "Employee", foreign_keys=[revdau_owner_id], lazy="selectin"
    )

    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    deal_value = Column(Float, default=0)
    expected_closure_quarter = Column(String, nullable=True)
    expected_closure_date = Column(Date, nullable=True)
    pipeline_stage = Column(String)
    risks = Column(Text, nullable=True)
    next_action = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def revdau_owner(self):
        return (
            self.revdau_owner_details.employee_name
            if self.revdau_owner_details
            else None
        )

    @property
    def client_name(self):
        return self.lead_details.client_name if self.lead_details else None


class SalesPipelineActionHistory(Base):
    __tablename__ = "sales_pipeline_action_histories"
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("sales_pipelines.id"))
    pipeline = relationship("SalesPipeline", backref="action_histories")
    action_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

