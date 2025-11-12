"""Base integration class."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.alert import Alert
from models.incident import Incident


class BaseIntegration(ABC):
    """Base class for all integrations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize integration with configuration."""
        self.config = config
        self.connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection."""
        pass
    
    @abstractmethod
    def send_alert(self, alert: Alert) -> bool:
        """Send alert to external system."""
        pass
    
    @abstractmethod
    def create_incident(self, incident: Incident) -> Optional[str]:
        """Create incident in external system."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        pass

