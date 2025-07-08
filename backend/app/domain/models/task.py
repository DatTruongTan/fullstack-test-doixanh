from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import datetime
import enum

from app.infrastructure.db.session import Base

class PriorityEnum(enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    due_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.normal, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="tasks") 