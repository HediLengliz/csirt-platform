"""Base detector class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from models.event import Event, EventSource, EventType


class BaseDetector(ABC):
    """Base class for all detectors."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize detector with configuration."""
        self.config = config
        self.source = self.get_source()

    @abstractmethod
    def get_source(self) -> EventSource:
        """Return the event source type."""
        pass

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to data source."""
        pass

    @abstractmethod
    def fetch_events(
        self, start_time: str = None, end_time: str = None
    ) -> List[Dict[str, Any]]:
        """Fetch events from the source."""
        pass

    @abstractmethod
    def normalize_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize event data to common format."""
        pass

    def detect_events(
        self, start_time: str = None, end_time: str = None
    ) -> List[Event]:
        """Detect and normalize events."""
        if not self.connect():
            raise ConnectionError(f"Failed to connect to {self.source.value}")

        raw_events = self.fetch_events(start_time, end_time)
        normalized_events = []

        for raw_event in raw_events:
            try:
                normalized = self.normalize_event(raw_event)
                event = Event(
                    source=self.source,
                    event_type=self._classify_event_type(normalized),
                    raw_data=raw_event,
                    normalized_data=normalized,
                    timestamp=normalized.get("timestamp"),
                    source_ip=normalized.get("source_ip"),
                    destination_ip=normalized.get("destination_ip"),
                    user=normalized.get("user"),
                    hostname=normalized.get("hostname"),
                    description=normalized.get("description"),
                    severity_score=normalized.get("severity_score"),
                )
                normalized_events.append(event)
            except Exception as e:
                # Log error but continue processing
                print(f"Error normalizing event: {e}")
                continue

        return normalized_events

    def _classify_event_type(self, normalized_data: Dict[str, Any]) -> EventType:
        """Classify event type based on normalized data."""
        event_type_str = normalized_data.get("event_type", "").lower()

        type_mapping = {
            "login_failure": EventType.LOGIN_FAILURE,
            "login_success": EventType.LOGIN_SUCCESS,
            "malware": EventType.MALWARE_DETECTED,
            "suspicious": EventType.SUSPICIOUS_ACTIVITY,
            "unauthorized": EventType.UNAUTHORIZED_ACCESS,
            "exfiltration": EventType.DATA_EXFILTRATION,
            "brute_force": EventType.BRUTE_FORCE,
            "ddos": EventType.DDoS,
            "phishing": EventType.PHISHING,
        }

        for key, event_type in type_mapping.items():
            if key in event_type_str:
                return event_type

        return EventType.OTHER
