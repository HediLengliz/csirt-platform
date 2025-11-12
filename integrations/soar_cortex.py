"""Cortex SOAR integration."""

from typing import Any, Dict, Optional

import requests

from integrations.base import BaseIntegration
from models.alert import Alert
from models.incident import Incident


class CortexIntegration(BaseIntegration):
    """Cortex SOAR integration for automated response."""

    def connect(self) -> bool:
        """Connect to Cortex."""
        try:
            url = f"{self.config.get('url')}/api/status"
            headers = {"Authorization": f"Bearer {self.config.get('api_key')}"}

            response = requests.get(
                url,
                headers=headers,
                timeout=10,
                verify=self.config.get("verify_ssl", True),
            )
            self.connected = response.status_code == 200
            return self.connected
        except Exception as e:
            print(f"Cortex integration connection error: {e}")
            self.connected = False
            return False

    def send_alert(self, alert: Alert) -> bool:
        """Send alert to Cortex for analysis."""
        if not self.connected:
            if not self.connect():
                return False

        try:
            # Cortex typically works with observables (IOCs)
            # We can create a job to analyze the alert
            url = f"{self.config.get('url')}/api/job"
            headers = {
                "Authorization": f"Bearer {self.config.get('api_key')}",
                "Content-Type": "application/json",
            }

            observables = []
            if alert.event:
                if alert.event.source_ip:
                    observables.append(
                        {
                            "dataType": "ip",
                            "data": alert.event.source_ip,
                            "tlp": 2,
                            "tags": [alert.priority.value],
                        }
                    )
                if alert.event.destination_ip:
                    observables.append(
                        {
                            "dataType": "ip",
                            "data": alert.event.destination_ip,
                            "tlp": 2,
                            "tags": [alert.priority.value],
                        }
                    )
                if alert.event.user:
                    observables.append(
                        {
                            "dataType": "user",
                            "data": alert.event.user,
                            "tlp": 2,
                            "tags": [alert.priority.value],
                        }
                    )

            if not observables:
                return False

            # Create analysis job
            payload = {
                "data": observables,
                "tlp": 2,
                "pap": 2,
                "analyzers": self.config.get("analyzers", []),  # List of analyzer IDs
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
                verify=self.config.get("verify_ssl", True),
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending alert to Cortex: {e}")
            return False

    def create_incident(self, incident: Incident) -> Optional[str]:
        """Create incident in Cortex (as an observable set)."""
        if not self.connected:
            if not self.connect():
                return None

        try:
            # Extract IOCs from incident
            observables = []
            if incident.ioc:
                for ioc in incident.ioc:
                    observables.append(
                        {
                            "dataType": ioc.get("type", "other"),
                            "data": ioc.get("value"),
                            "tlp": 2,
                            "tags": incident.tags or [],
                        }
                    )

            if not observables:
                return None

            url = f"{self.config.get('url')}/api/job"
            headers = {
                "Authorization": f"Bearer {self.config.get('api_key')}",
                "Content-Type": "application/json",
            }

            payload = {
                "data": observables,
                "tlp": 2,
                "pap": 2,
                "analyzers": self.config.get("analyzers", []),
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
                verify=self.config.get("verify_ssl", True),
            )
            response.raise_for_status()
            job_data = response.json()
            return f"cortex://job/{job_data.get('id')}"
        except Exception as e:
            print(f"Error creating incident in Cortex: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "connected": self.connected,
            "type": "cortex",
            "url": self.config.get("url"),
        }
