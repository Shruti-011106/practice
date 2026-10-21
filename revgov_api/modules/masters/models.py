from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from core.database import Base
from core.models import TimestampMixin


class SystemLookup(TimestampMixin, Base):
    __tablename__ = "sys_lookups"

    type = Column(String(50), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    label = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("type", "code", name="uq_lookup_type_code"),)
