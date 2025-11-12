"""Elastic Security SIEM detector."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from elasticsearch import Elasticsearch

from detection.base import BaseDetector
from models.event import EventSource


class ElasticDetector(BaseDetector):
    """Detector for Elastic Security SIEM."""

    def get_source(self) -> EventSource:
        return EventSource.ELASTIC

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
                    self.config.get("password"),
                )

            self.es = Elasticsearch(**es_config)
            return self.es.ping()
        except Exception as e:
            print(f"Elasticsearch connection error: {e}")
            return False

    def fetch_events(
        self, start_time: str = None, end_time: str = None
    ) -> List[Dict[str, Any]]:
        """Fetch events from Elasticsearch."""
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        if not end_time:
            end_time = datetime.utcnow().isoformat()

        # Default indices - can be customized
        indices = self.config.get("indices", "logstash-*,filebeat-*")

        query = {
            "bool": {
                "must": [
                    {"range": {"@timestamp": {"gte": start_time, "lte": end_time}}}
                ]
            }
        }

        # Add custom query if provided
        if self.config.get("custom_query"):
            query["bool"]["must"].append(self.config.get("custom_query"))

        try:
            response = self.es.search(
                index=indices,
                body={
                    "query": query,
                    "size": self.config.get("max_results", 1000),
                    "sort": [{"@timestamp": {"order": "desc"}}],
                },
            )

            events = []
            for hit in response.get("hits", {}).get("hits", []):
                events.append(hit.get("_source", {}))

            return events
        except Exception as e:
            print(f"Error fetching Elasticsearch events: {e}")
            return []

    def normalize_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Elasticsearch event to common format."""
        return {
            "timestamp": raw_event.get("@timestamp")
            or raw_event.get("timestamp", datetime.utcnow().isoformat()),
            "source_ip": raw_event.get("source.ip")
            or raw_event.get("src_ip")
            or raw_event.get("source_ip"),
            "destination_ip": raw_event.get("destination.ip")
            or raw_event.get("dest_ip")
            or raw_event.get("destination_ip"),
            "user": raw_event.get("user.name")
            or raw_event.get("user")
            or raw_event.get("username"),
            "hostname": raw_event.get("host.name")
            or raw_event.get("hostname")
            or raw_event.get("host"),
            "description": raw_event.get("message")
            or raw_event.get("description")
            or str(raw_event),
            "event_type": raw_event.get("event.type")
            or raw_event.get("event_type")
            or raw_event.get("action"),
            "severity_score": raw_event.get("event.severity")
            or raw_event.get("severity")
            or raw_event.get("priority"),
            "elastic_index": raw_event.get("_index"),
        }
