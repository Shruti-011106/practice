# pyrefly: ignore [missing-import]
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from core.database import Base
from core.models import TimestampMixin


class OrgSetting(TimestampMixin, Base):
    __tablename__ = "org_settings"

    # Company Profile fields
    organization_name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=True)
    alias_name = Column(String(255), nullable=True)
    primary_domain = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    company_logo = Column(String(500), nullable=True)

    # Contact & Support fields
    admin_email = Column(String(255), nullable=False)
    support_email = Column(String(255), nullable=True)
    billing_contact_email = Column(String(255), nullable=True)


class MicrosoftEntraConfig(TimestampMixin, Base):
    __tablename__ = "microsoft_entra_configs"

    tenant_id = Column(String(255), nullable=False)
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(500), nullable=False)
    organization_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    connection_status = Column(String(50), default="UNVERIFIED", nullable=False)
    last_tested_at = Column(DateTime(timezone=True), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    synced_users_count = Column(Integer, default=0, nullable=False)
