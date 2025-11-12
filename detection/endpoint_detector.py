"""Endpoint detector for EDR/EDP events."""
from typing import List, Dict, Any
from detection.base import BaseDetector
from models.event import EventSource
from datetime import datetime
import requests


class EndpointDetector(BaseDetector):
    """Detector for endpoint security events (EDR/EDP)."""
    
    def get_source(self) -> EventSource:
        return EventSource.ENDPOINT
    
    def connect(self) -> bool:
        """Connect to endpoint detection system."""
        # This would connect to an EDR API (e.g., CrowdStrike, SentinelOne, etc.)
        # For now, we'll use a mock connection
        self.api_url = self.config.get("api_url")
        self.api_key = self.config.get("api_key")
        return bool(self.api_url and self.api_key)
    
    def fetch_events(self, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """Fetch events from endpoint detection system."""
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
                f"{self.api_url}/events",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("events", [])
        except Exception as e:
            print(f"Error fetching endpoint events: {e}")
            return []
    
    def normalize_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize endpoint event to common format."""
        return {
            "timestamp": raw_event.get("timestamp") or raw_event.get("created_at", datetime.utcnow().isoformat()),
            "source_ip": raw_event.get("source_ip") or raw_event.get("ip"),
            "destination_ip": raw_event.get("destination_ip"),
            "user": raw_event.get("user") or raw_event.get("username"),
            "hostname": raw_event.get("hostname") or raw_event.get("host") or raw_event.get("device_name"),
            "description": raw_event.get("description") or raw_event.get("message") or raw_event.get("event_description"),
            "event_type": raw_event.get("event_type") or raw_event.get("type"),
            "severity_score": raw_event.get("severity") or raw_event.get("risk_score"),
            "process_name": raw_event.get("process_name"),
            "file_path": raw_event.get("file_path"),
        }

