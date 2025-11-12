"""Splunk SIEM detector."""
from typing import List, Dict, Any
from splunklib import client as splunk_client
from detection.base import BaseDetector
from models.event import EventSource
from datetime import datetime, timedelta


class SplunkDetector(BaseDetector):
    """Detector for Splunk SIEM."""
    
    def get_source(self) -> EventSource:
        return EventSource.SPLUNK
    
    def connect(self) -> bool:
        """Connect to Splunk."""
        try:
            self.splunk = splunk_client.connect(
                host=self.config.get("host"),
                port=self.config.get("port", 8089),
                username=self.config.get("username"),
                password=self.config.get("password"),
                verify=self.config.get("verify_ssl", False)
            )
            return True
        except Exception as e:
            print(f"Splunk connection error: {e}")
            return False
    
    def fetch_events(self, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """Fetch events from Splunk."""
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")
        if not end_time:
            end_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Default search query - can be customized
        search_query = self.config.get(
            "search_query",
            "search index=* earliest={} latest={} | head 1000".format(start_time, end_time)
        )
        
        try:
            kwargs = {
                "earliest_time": start_time,
                "latest_time": end_time,
                "count": self.config.get("max_results", 1000)
            }
            
            search_results = self.splunk.jobs.oneshot(search_query, **kwargs)
            events = []
            
            for result in search_results:
                events.append(dict(result))
            
            return events
        except Exception as e:
            print(f"Error fetching Splunk events: {e}")
            return []
    
    def normalize_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Splunk event to common format."""
        return {
            "timestamp": raw_event.get("_time", raw_event.get("timestamp", datetime.utcnow().isoformat())),
            "source_ip": raw_event.get("src_ip") or raw_event.get("src") or raw_event.get("source_ip"),
            "destination_ip": raw_event.get("dest_ip") or raw_event.get("dest") or raw_event.get("destination_ip"),
            "user": raw_event.get("user") or raw_event.get("username"),
            "hostname": raw_event.get("host") or raw_event.get("hostname"),
            "description": raw_event.get("_raw") or raw_event.get("message") or raw_event.get("description"),
            "event_type": raw_event.get("event_type") or raw_event.get("action"),
            "severity_score": raw_event.get("severity") or raw_event.get("priority"),
            "splunk_index": raw_event.get("index"),
            "splunk_sourcetype": raw_event.get("sourcetype"),
        }

