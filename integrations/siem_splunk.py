"""Splunk SIEM integration."""

from typing import Any, Dict, Optional

from splunklib import client as splunk_client

from integrations.base import BaseIntegration
from models.alert import Alert
from models.incident import Incident


class SplunkIntegration(BaseIntegration):
    """Splunk SIEM integration."""

    def connect(self) -> bool:
        """Connect to Splunk."""
        try:
            self.splunk = splunk_client.connect(
                host=self.config.get("host"),
                port=self.config.get("port", 8089),
                username=self.config.get("username"),
                password=self.config.get("password"),
                verify=self.config.get("verify_ssl", False),
            )
            self.connected = True
            return True
        except Exception as e:
            print(f"Splunk integration connection error: {e}")
            self.connected = False
            return False

    def send_alert(self, alert: Alert) -> bool:
        """Send alert to Splunk."""
        if not self.connected:
            if not self.connect():
                return False

        try:
            # Create event in Splunk
            event_data = {
                "time": alert.created_at.isoformat(),
                "event": {
                    "alert_id": alert.id,
                    "title": alert.title,
                    "description": alert.description,
                    "priority": alert.priority.value,
                    "status": alert.status.value,
                    "ml_score": alert.ml_score,
                    "source": alert.source,
                },
            }

            # Send to Splunk index
            index_name = self.config.get("index", "csirt_alerts")
            self.splunk.indexes[index_name].submit(
                data=str(event_data), sourcetype="csirt:alert"
            )

            return True
        except Exception as e:
            print(f"Error sending alert to Splunk: {e}")
            return False

    def create_incident(self, incident: Incident) -> Optional[str]:
        """Create incident in Splunk (as a notable event)."""
        if not self.connected:
            if not self.connect():
                return None

        try:
            # Create notable event in Splunk
            event_data = {
                "time": incident.created_at.isoformat(),
                "event": {
                    "incident_id": incident.id,
                    "title": incident.title,
                    "description": incident.description,
                    "severity": incident.severity.value,
                    "status": incident.status.value,
                },
            }

            index_name = self.config.get("index", "csirt_incidents")
            self.splunk.indexes[index_name].submit(
                data=str(event_data), sourcetype="csirt:incident"
            )

            return f"splunk://{index_name}/{incident.id}"
        except Exception as e:
            print(f"Error creating incident in Splunk: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "connected": self.connected,
            "type": "splunk",
            "host": self.config.get("host"),
        }
