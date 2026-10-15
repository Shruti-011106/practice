from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from core.database import Base
from core.models import TimestampMixin


class ReusableAsset(TimestampMixin, Base):
    __tablename__ = "reusable_assets"
    asset_name = Column(String)
    category = Column(String)
    technology = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("employees.id"))
    owner = relationship("Employee", foreign_keys=[owner_id], lazy="selectin")
    created_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_by_details = relationship("Employee", foreign_keys=[created_by_id], lazy="selectin")
    version = Column(String, nullable=True)
    document_name = Column(String, nullable=True)
    document_type = Column(String, nullable=True)
    upload = Column(
        String, nullable=True
    )  # Stores the generated path/URL of the uploaded PDF file
    repository_link = Column(String, nullable=True)
    maturity_level = Column(String, nullable=True)
    approval_status = Column(String, nullable=True)
    last_review_date = Column(Date, nullable=True)
    tag = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    @property
    def owner_name(self):
        return self.owner.employee_name if self.owner else None


# Knowledge Repository - Merged into Reusable Asset (Temporarily Disabled)
# class KnowledgeRepo(TimestampMixin, Base):
#     __tablename__ = "knowledge_repos"
#     document_name = Column(String)
#     category = Column(String)
#     team = Column(String)
#     owner = Column(String)
#     approval_status = Column(String)
#     last_review_date = Column(Date, nullable=True)
#     tag = Column(String, nullable=True)


class CapabilityBuilding(TimestampMixin, Base):
    __tablename__ = "capability_buildings"

    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", foreign_keys=[employee_id], lazy="selectin")

    practice_owner_id = Column(Integer, ForeignKey("employees.id"))
    practice_owner = relationship(
        "Employee", foreign_keys=[practice_owner_id], lazy="selectin"
    )

    created_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_by_details = relationship("Employee", foreign_keys=[created_by_id], lazy="selectin")


    technology = Column(String)
    skill_level = Column(String, nullable=True)
    current_skill = Column(String)
    target_skill = Column(String)
    active_projects = Column(String, nullable=True)
    business_alignment = Column(String, nullable=True)
    readiness_score = Column(Float, default=0.0)
    strategic_priority = Column(String, nullable=True)

    # Naya JSON Array for tracking multiple trainings
    training_count = Column(Integer, default=0)
    training_details = Column(JSON, default=list)

    @property
    def employee_name(self):
        return self.employee.employee_name if self.employee else None

    @property
    def practice_owner_name(self):
        return self.practice_owner.employee_name if self.practice_owner else None


class PartnershipAlliance(TimestampMixin, Base):
    __tablename__ = "partnership_alliances"
    partner_name = Column(String)
    alliance_owner = Column(String)
    partnership_type = Column(String)
    joint_opportunities = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
    gtm_activities = Column(Text, nullable=True)
    revenue_contribution = Column(Float, default=0)


class TechCapability(TimestampMixin, Base):
    __tablename__ = "tech_capabilities"
    technology = Column(String)
    practice_owner = Column(String)
    certified_resources = Column(Integer, default=0)
    active_projects = Column(Integer, default=0)
    readiness_score = Column(Float, default=0)
    strategic_priority = Column(String, nullable=True)


class InnovationAutomation(TimestampMixin, Base):
    __tablename__ = "innovation_automations"
    innovation_name = Column(String)

    created_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_by_details = relationship("Employee", foreign_keys=[created_by_id], lazy="selectin")

    team = Column(String)
    automation_type = Column(String)
    productivity_gain = Column(String, nullable=True)
    status = Column(String)
    business_benefit = Column(Text, nullable=True)


class TrainingTracker(TimestampMixin, Base):
    __tablename__ = "training_trackers"
    training_name = Column(String)
    team = Column(String)
    planned_date = Column(Date, nullable=True)
    completion_pct = Column(Float, default=0)
    certification_status = Column(String, nullable=True)
    kpi_impact = Column(String, nullable=True)
