"""TheHive SOAR integration."""
from typing import Dict, Any, Optional
import requests
from integrations.base import BaseIntegration
from models.alert import Alert
from models.incident import Incident


class TheHiveIntegration(BaseIntegration):
    """TheHive SOAR integration."""
    
    def connect(self) -> bool:
        """Connect to TheHive."""
        try:
            url = f"{self.config.get('url')}/api/status"
            headers = {
                "Authorization": f"Bearer {self.config.get('api_key')}"
            }
            
            response = requests.get(url, headers=headers, timeout=10, verify=self.config.get("verify_ssl", True))
            self.connected = response.status_code == 200
            return self.connected
        except Exception as e:
            print(f"TheHive integration connection error: {e}")
            self.connected = False
            return False
    
    def send_alert(self, alert: Alert) -> bool:
        """Send alert to TheHive as an observable."""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            url = f"{self.config.get('url')}/api/alert"
            headers = {
                "Authorization": f"Bearer {self.config.get('api_key')}",
                "Content-Type": "application/json"
            }
            
            # Map priority to TheHive severity
            severity_mapping = {
                "critical": 4,
                "high": 3,
                "medium": 2,
                "low": 1,
                "info": 0,
            }
            
            payload = {
                "type": "alert",
                "source": "CSIRT Platform",
                "sourceRef": str(alert.id),
                "title": alert.title,
                "description": alert.description or "",
                "severity": severity_mapping.get(alert.priority.value, 2),
                "tags": [alert.priority.value, alert.source],
                "artifacts": []
            }
            
            # Add event data as artifacts if available
            if alert.event:
                if alert.event.source_ip:
                    payload["artifacts"].append({
                        "dataType": "ip",
                        "data": alert.event.source_ip
                    })
                if alert.event.destination_ip:
                    payload["artifacts"].append({
                        "dataType": "ip",
                        "data": alert.event.destination_ip
                    })
            
            response = requests.post(url, json=payload, headers=headers, timeout=30, verify=self.config.get("verify_ssl", True))
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending alert to TheHive: {e}")
            return False
    
    def create_incident(self, incident: Incident) -> Optional[str]:
        """Create incident in TheHive."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            url = f"{self.config.get('url')}/api/case"
            headers = {
                "Authorization": f"Bearer {self.config.get('api_key')}",
                "Content-Type": "application/json"
            }
            
            # Map severity to TheHive severity
            severity_mapping = {
                "critical": 4,
                "high": 3,
                "medium": 2,
                "low": 1,
            }
            
            payload = {
                "title": incident.title,
                "description": incident.description or "",
                "severity": severity_mapping.get(incident.severity.value, 2),
                "tags": incident.tags or [],
                "status": "Open" if incident.status.value == "open" else "InProgress",
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30, verify=self.config.get("verify_ssl", True))
            response.raise_for_status()
            case_data = response.json()
            return f"thehive://case/{case_data.get('id')}"
        except Exception as e:
            print(f"Error creating incident in TheHive: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "connected": self.connected,
            "type": "thehive",
            "url": self.config.get("url"),
        }

