"""Incident model."""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class IncidentStatus(str, enum.Enum):
    """Incident status."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentSeverity(str, enum.Enum):
    """Incident severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Incident(BaseModel):
    """Incident model."""
    __tablename__ = "incidents"
    
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN, nullable=False, index=True)
    severity = Column(Enum(IncidentSeverity), nullable=False, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    assigned_to = Column(String, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    ioc = Column(JSON, nullable=True)  # Indicators of Compromise
    
    # Relationships
    alert = relationship("Alert", back_populates="incidents")

