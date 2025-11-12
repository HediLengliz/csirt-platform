"""Network detector for firewall/IDS/IPS events."""

from datetime import datetime
from typing import Any, Dict, List

import requests

from detection.base import BaseDetector
from models.event import EventSource


class NetworkDetector(BaseDetector):
    """Detector for network security events (firewall, IDS/IPS)."""

    def get_source(self) -> EventSource:
        return EventSource.NETWORK

    def connect(self) -> bool:
        """Connect to network security system."""
        self.api_url = self.config.get("api_url")
        self.api_key = self.config.get("api_key")
        return bool(self.api_url and self.api_key)

    def fetch_events(
        self, start_time: str = None, end_time: str = None
    ) -> List[Dict[str, Any]]:
        """Fetch events from network security system."""
        if not self.api_url:
            return []

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {}
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time

            response = requests.get(
                f"{self.api_url}/events", headers=headers, params=params, timeout=30
            )
            response.raise_for_status()
            return response.json().get("events", [])
        except Exception as e:
            print(f"Error fetching network events: {e}")
            return []

    def normalize_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize network event to common format."""
        return {
            "timestamp": raw_event.get("timestamp")
            or raw_event.get("time", datetime.utcnow().isoformat()),
            "source_ip": raw_event.get("src_ip")
            or raw_event.get("source_ip")
            or raw_event.get("src"),
            "destination_ip": raw_event.get("dest_ip")
            or raw_event.get("destination_ip")
            or raw_event.get("dst"),
            "source_port": raw_event.get("src_port"),
            "destination_port": raw_event.get("dest_port") or raw_event.get("dst_port"),
            "protocol": raw_event.get("protocol"),
            "user": raw_event.get("user"),
            "hostname": raw_event.get("hostname") or raw_event.get("host"),
            "description": raw_event.get("description")
            or raw_event.get("message")
            or raw_event.get("signature"),
            "event_type": raw_event.get("event_type")
            or raw_event.get("type")
            or raw_event.get("action"),
            "severity_score": raw_event.get("severity") or raw_event.get("priority"),
            "bytes_sent": raw_event.get("bytes_sent"),
            "bytes_received": raw_event.get("bytes_received"),
        }
