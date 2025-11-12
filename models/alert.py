"""Alert model."""
from sqlalchemy import Column, String, Text, Float, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class AlertStatus(str, enum.Enum):
    """Alert status."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    IGNORED = "ignored"


class AlertPriority(str, enum.Enum):
    """Alert priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Alert(BaseModel):
    """Alert model."""
    __tablename__ = "alerts"
    
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW, nullable=False, index=True)
    priority = Column(Enum(AlertPriority), nullable=False, index=True)
    ml_score = Column(Float, nullable=True, index=True)  # ML-based priority score
    source = Column(String, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    
    # Relationships
    event = relationship("Event", back_populates="alerts")
    incidents = relationship("Incident", back_populates="alert")

