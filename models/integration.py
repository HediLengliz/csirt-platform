"""Integration model for SIEM/SOAR connections."""
from sqlalchemy import Column, String, Boolean, Enum, JSON
from models.base import BaseModel
import enum


class IntegrationType(str, enum.Enum):
    """Integration types."""
    SIEM_SPLUNK = "siem_splunk"
    SIEM_ELASTIC = "siem_elastic"
    SOAR_THEHIVE = "soar_thehive"
    SOAR_CORTEX = "soar_cortex"
    SOAR_PHANTOM = "soar_phantom"


class Integration(BaseModel):
    """Integration configuration model."""
    __tablename__ = "integrations"
    
    name = Column(String, nullable=False, unique=True, index=True)
    integration_type = Column(Enum(IntegrationType), nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
    config = Column(JSON, nullable=False)  # Connection config
    last_sync = Column(String, nullable=True)
    status = Column(String, nullable=True)  # active, error, disconnected

