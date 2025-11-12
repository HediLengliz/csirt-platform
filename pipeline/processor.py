"""Event processing pipeline."""

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from alerts.manager import AlertManager
from alerts.tasks import process_events_to_alerts
from config.database import SessionLocal
from models.event import Event


class EventProcessor:
    """Processes events through the detection and alert pipeline."""

    def __init__(self):
        """Initialize event processor."""
        self.alert_manager = AlertManager()

    def process_events(self, events: List[Event]) -> Dict[str, Any]:
        """Process a batch of events."""
        db = SessionLocal()

        try:
            processed_events = []
            created_alerts = []

            for event in events:
                # Save event to database
                db.add(event)
                db.commit()
                db.refresh(event)
                processed_events.append(event.id)

                # Create alert asynchronously
                # We'll trigger Celery task for alert creation
                process_events_to_alerts.delay([event.id])

            return {
                "processed": len(processed_events),
                "event_ids": processed_events,
                "status": "success",
            }
        except Exception as e:
            db.rollback()
            return {"error": str(e), "status": "failed"}
        finally:
            db.close()

    def process_event_stream(
        self, event_stream: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process a stream of raw events."""
        db = SessionLocal()

        try:
            events = []
            for raw_event in event_stream:
                # This would need to be converted to Event objects
                # For now, we'll create a simplified version
                event = self._create_event_from_dict(raw_event)
                if event:
                    events.append(event)

            return self.process_events(events)
        except Exception as e:
            return {"error": str(e), "status": "failed"}
        finally:
            db.close()

    def _create_event_from_dict(self, event_dict: Dict[str, Any]) -> Event:
        """Create Event object from dictionary."""
        # This is a simplified version - in production, you'd have proper mapping
        from models.event import EventSource, EventType

        return Event(
            source=EventSource(event_dict.get("source", "custom")),
            event_type=EventType(event_dict.get("event_type", "other")),
            raw_data=event_dict,
            normalized_data=event_dict.get("normalized_data"),
            timestamp=event_dict.get("timestamp", datetime.utcnow().isoformat()),
            source_ip=event_dict.get("source_ip"),
            destination_ip=event_dict.get("destination_ip"),
            user=event_dict.get("user"),
            hostname=event_dict.get("hostname"),
            description=event_dict.get("description"),
            severity_score=event_dict.get("severity_score"),
        )
