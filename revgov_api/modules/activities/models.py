from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class SystemComment(Base):
    __tablename__ = "system_comments"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True) 
    entity_id = Column(Integer, index=True)  
    user_id = Column(Integer, ForeignKey("users.id")) 
    comment_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", lazy="selectin")

    @property
    def user_name(self):
        return f"{self.user.first_name} {self.user.last_name}" if self.user else None


class SystemAuditLog(Base):
    __tablename__ = "system_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True) 
    entity_id = Column(Integer, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # System actions might be null
    action = Column(String)  
    details = Column(Text, nullable=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", lazy="selectin")

    @property
    def user_name(self):
        if not self.user:
            return "System Admin"
        return f"{self.user.first_name} {self.user.last_name}"
