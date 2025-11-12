"""Elastic Security SIEM integration."""
from typing import Dict, Any, Optional
from elasticsearch import Elasticsearch
from integrations.base import BaseIntegration
from models.alert import Alert
from models.incident import Incident
from datetime import datetime


class ElasticIntegration(BaseIntegration):
    """Elastic Security SIEM integration."""
    
    def connect(self) -> bool:
        """Connect to Elasticsearch."""
        try:
            es_config = {
                "hosts": [f"{self.config.get('host')}:{self.config.get('port', 9200)}"],
                "verify_certs": self.config.get("verify_ssl", False),
            }
            
            if self.config.get("username") and self.config.get("password"):
                es_config["basic_auth"] = (
                    self.config.get("username"),
                    self.config.get("password")
                )
            
            self.es = Elasticsearch(**es_config)
            self.connected = self.es.ping()
            return self.connected
        except Exception as e:
            print(f"Elasticsearch integration connection error: {e}")
            self.connected = False
            return False
    
    def send_alert(self, alert: Alert) -> bool:
        """Send alert to Elasticsearch."""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            index_name = self.config.get("index", "csirt-alerts")
            
            document = {
                "@timestamp": alert.created_at.isoformat(),
                "alert_id": alert.id,
                "title": alert.title,
                "description": alert.description,
                "priority": alert.priority.value,
                "status": alert.status.value,
                "ml_score": alert.ml_score,
                "source": alert.source,
            }
            
            self.es.index(index=index_name, document=document)
            return True
        except Exception as e:
            print(f"Error sending alert to Elasticsearch: {e}")
            return False
    
    def create_incident(self, incident: Incident) -> Optional[str]:
        """Create incident in Elasticsearch."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            index_name = self.config.get("incident_index", "csirt-incidents")
            
            document = {
                "@timestamp": incident.created_at.isoformat(),
                "incident_id": incident.id,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity.value,
                "status": incident.status.value,
            }
            
            response = self.es.index(index=index_name, document=document)
            return f"elastic://{index_name}/{response['_id']}"
        except Exception as e:
            print(f"Error creating incident in Elasticsearch: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "connected": self.connected,
            "type": "elastic",
            "host": self.config.get("host"),
        }

