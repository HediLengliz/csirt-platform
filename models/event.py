"""Event model for security events."""
from sqlalchemy import Column, String, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
import enum


class EventSource(str, enum.Enum):
    """Event source types."""
    SPLUNK = "splunk"
    ELASTIC = "elastic"
    ENDPOINT = "endpoint"
    NETWORK = "network"
    FIREWALL = "firewall"
    IDS_IPS = "ids_ips"
    CUSTOM = "custom"


class EventType(str, enum.Enum):
    """Event types."""
    LOGIN_FAILURE = "login_failure"
    LOGIN_SUCCESS = "login_success"
    MALWARE_DETECTED = "malware_detected"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    BRUTE_FORCE = "brute_force"
    DDoS = "ddos"
    PHISHING = "phishing"
    OTHER = "other"


class Event(BaseModel):
    """Security event model."""
    __tablename__ = "events"
    
    source = Column(Enum(EventSource), nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False, index=True)
    raw_data = Column(JSON, nullable=False)
    normalized_data = Column(JSON, nullable=True)
    timestamp = Column(String, nullable=False, index=True)
    source_ip = Column(String, nullable=True, index=True)
    destination_ip = Column(String, nullable=True, index=True)
    user = Column(String, nullable=True, index=True)
    hostname = Column(String, nullable=True, index=True)
    description = Column(Text, nullable=True)
    severity_score = Column(String, nullable=True)
    
    # Relationships
    alerts = relationship("Alert", back_populates="event")

