from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class EventWebinar(Base):
    __tablename__ = "event_webinars"
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String)
    date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    owner_relation = relationship("Employee", foreign_keys=[owner_id], lazy="selectin")
    created_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_by_relation = relationship("Employee", foreign_keys=[created_by_id], lazy="selectin")
    participants = Column(Integer, default=0)
    leads_generated = Column(Integer, default=0)
    followup_status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def owner_name(self):
        return self.owner_relation.employee_name if self.owner_relation else None


class ContentBranding(Base):
    __tablename__ = "content_brandings"
    id = Column(Integer, primary_key=True, index=True)
    asset_name = Column(String)
    type = Column(String)
    owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    owner_relation = relationship("Employee", foreign_keys=[owner_id], lazy="selectin")
    created_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_by_relation = relationship("Employee", foreign_keys=[created_by_id], lazy="selectin")
    approval_status = Column(String)
    reusability = Column(String, nullable=True)
    last_updated = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def owner_name(self):
        return self.owner_relation.employee_name if self.owner_relation else None


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String)
    campaign_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    campaign_owner_relation = relationship("Employee", foreign_keys=[campaign_owner_id], lazy="selectin")
    created_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_by_relation = relationship("Employee", foreign_keys=[created_by_id], lazy="selectin")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(Float, default=0)
    leads_generated = Column(Integer, default=0)
    roi = Column(Float, default=0)
    target_audience = Column(String, nullable=True)
    status = Column(String)  # completed / incomplete / on hold
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def campaign_owner_name(self):
        return self.campaign_owner_relation.employee_name if self.campaign_owner_relation else None
