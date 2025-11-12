"""Phantom SOAR integration."""
from typing import Dict, Any, Optional
import requests
from integrations.base import BaseIntegration
from models.alert import Alert
from models.incident import Incident


class PhantomIntegration(BaseIntegration):
    """Phantom SOAR integration."""
    
    def connect(self) -> bool:
        """Connect to Phantom."""
        try:
            url = f"{self.config.get('url')}/rest/login"
            auth = {
                "username": self.config.get("username"),
                "password": self.config.get("password")
            }
            
            response = requests.post(
                url,
                json=auth,
                timeout=10,
                verify=self.config.get("verify_ssl", False)
            )
            
            if response.status_code == 200:
                self.auth_token = response.json().get("ph-auth-token")
                self.connected = True
                return True
            else:
                self.connected = False
                return False
        except Exception as e:
            print(f"Phantom integration connection error: {e}")
            self.connected = False
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {
            "ph-auth-token": getattr(self, "auth_token", ""),
            "Content-Type": "application/json"
        }
    
    def send_alert(self, alert: Alert) -> bool:
        """Send alert to Phantom as an event."""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            url = f"{self.config.get('url')}/rest/event"
            headers = self._get_headers()
            
            # Map priority to Phantom severity
            severity_mapping = {
                "critical": "high",
                "high": "medium",
                "medium": "low",
                "low": "low",
                "info": "low",
            }
            
            payload = {
                "container": {
                    "name": alert.title,
                    "description": alert.description or "",
                    "severity": severity_mapping.get(alert.priority.value, "low"),
                    "status": "new",
                    "label": alert.priority.value,
                },
                "artifacts": []
            }
            
            # Add event data as artifacts
            if alert.event:
                if alert.event.source_ip:
                    payload["artifacts"].append({
                        "cef": {
                            "sourceAddress": alert.event.source_ip
                        },
                        "name": "Source IP",
                        "label": "network",
                        "cefTypes": {
                            "sourceAddress": ["ip"]
                        }
                    })
                if alert.event.destination_ip:
                    payload["artifacts"].append({
                        "cef": {
                            "destinationAddress": alert.event.destination_ip
                        },
                        "name": "Destination IP",
                        "label": "network",
                        "cefTypes": {
                            "destinationAddress": ["ip"]
                        }
                    })
                if alert.event.user:
                    payload["artifacts"].append({
                        "cef": {
                            "sourceUserName": alert.event.user
                        },
                        "name": "User",
                        "label": "user",
                        "cefTypes": {
                            "sourceUserName": ["username"]
                        }
                    })
            
            response = requests.post(url, json=payload, headers=headers, timeout=30, verify=self.config.get("verify_ssl", False))
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending alert to Phantom: {e}")
            return False
    
    def create_incident(self, incident: Incident) -> Optional[str]:
        """Create incident in Phantom as a container."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            url = f"{self.config.get('url')}/rest/container"
            headers = self._get_headers()
            
            # Map severity to Phantom severity
            severity_mapping = {
                "critical": "high",
                "high": "medium",
                "medium": "low",
                "low": "low",
            }
            
            payload = {
                "name": incident.title,
                "description": incident.description or "",
                "severity": severity_mapping.get(incident.severity.value, "low"),
                "status": "new" if incident.status.value == "open" else "open",
                "label": incident.severity.value,
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30, verify=self.config.get("verify_ssl", False))
            response.raise_for_status()
            container_data = response.json()
            return f"phantom://container/{container_data.get('id')}"
        except Exception as e:
            print(f"Error creating incident in Phantom: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "connected": self.connected,
            "type": "phantom",
            "url": self.config.get("url"),
        }

