"""Event correlation engine."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from config.database import SessionLocal
from models.alert import Alert
from models.event import Event


class EventCorrelator:
    """Correlates events to identify patterns and potential incidents."""

    def correlate_events(self, time_window_minutes: int = 60) -> List[Dict[str, Any]]:
        """Correlate events within a time window."""
        db = SessionLocal()

        try:
            # Get events from time window
            start_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

            events = (
                db.query(Event)
                .filter(Event.created_at >= start_time)
                .order_by(Event.created_at.desc())
                .all()
            )

            # Correlate by different criteria
            correlations = []

            # Correlate by source IP
            source_ip_correlation = self._correlate_by_source_ip(db, events, start_time)
            correlations.extend(source_ip_correlation)

            # Correlate by user
            user_correlation = self._correlate_by_user(db, events, start_time)
            correlations.extend(user_correlation)

            # Correlate by event type
            event_type_correlation = self._correlate_by_event_type(
                db, events, start_time
            )
            correlations.extend(event_type_correlation)

            return correlations
        finally:
            db.close()

    def _correlate_by_source_ip(
        self, db: Session, events: List[Event], start_time: datetime
    ) -> List[Dict[str, Any]]:
        """Correlate events by source IP."""
        correlations = []

        # Group events by source IP
        source_ips = {}
        for event in events:
            if event.source_ip:
                if event.source_ip not in source_ips:
                    source_ips[event.source_ip] = []
                source_ips[event.source_ip].append(event)

        # Identify suspicious patterns
        for source_ip, ip_events in source_ips.items():
            if len(ip_events) >= 5:  # Threshold for correlation
                # Check for multiple failed logins
                failed_logins = [
                    e for e in ip_events if e.event_type.value == "login_failure"
                ]
                if len(failed_logins) >= 3:
                    correlations.append(
                        {
                            "type": "brute_force_attempt",
                            "source_ip": source_ip,
                            "event_count": len(failed_logins),
                            "events": [e.id for e in failed_logins],
                            "severity": "high",
                        }
                    )

                # Check for multiple event types from same IP
                event_types = set(e.event_type.value for e in ip_events)
                if len(event_types) >= 3:
                    correlations.append(
                        {
                            "type": "suspicious_activity",
                            "source_ip": source_ip,
                            "event_count": len(ip_events),
                            "event_types": list(event_types),
                            "events": [e.id for e in ip_events],
                            "severity": "medium",
                        }
                    )

        return correlations

    def _correlate_by_user(
        self, db: Session, events: List[Event], start_time: datetime
    ) -> List[Dict[str, Any]]:
        """Correlate events by user."""
        correlations = []

        # Group events by user
        users = {}
        for event in events:
            if event.user:
                if event.user not in users:
                    users[event.user] = []
                users[event.user].append(event)

        # Identify suspicious patterns
        for user, user_events in users.items():
            if len(user_events) >= 10:  # Threshold for correlation
                # Check for access from multiple IPs
                source_ips = set(e.source_ip for e in user_events if e.source_ip)
                if len(source_ips) >= 3:
                    correlations.append(
                        {
                            "type": "account_compromise",
                            "user": user,
                            "source_ips": list(source_ips),
                            "event_count": len(user_events),
                            "events": [e.id for e in user_events],
                            "severity": "high",
                        }
                    )

        return correlations

    def _correlate_by_event_type(
        self, db: Session, events: List[Event], start_time: datetime
    ) -> List[Dict[str, Any]]:
        """Correlate events by event type."""
        correlations = []

        # Group events by type
        event_types = {}
        for event in events:
            event_type = event.event_type.value
            if event_type not in event_types:
                event_types[event_type] = []
            event_types[event_type].append(event)

        # Identify patterns
        for event_type, type_events in event_types.items():
            if len(type_events) >= 20:  # Threshold for correlation
                correlations.append(
                    {
                        "type": "event_flood",
                        "event_type": event_type,
                        "event_count": len(type_events),
                        "events": [e.id for e in type_events],
                        "severity": "medium",
                    }
                )

        return correlations

    def create_incident_from_correlation(
        self, correlation: Dict[str, Any], db: Session
    ) -> int:
        """Create an incident from a correlation."""
        from models.alert import Alert
        from models.incident import Incident, IncidentSeverity, IncidentStatus

        # Map correlation severity to incident severity
        severity_mapping = {
            "critical": IncidentSeverity.CRITICAL,
            "high": IncidentSeverity.HIGH,
            "medium": IncidentSeverity.MEDIUM,
            "low": IncidentSeverity.LOW,
        }

        incident = Incident(
            title=f"Correlated Incident: {correlation.get('type', 'unknown')}",
            description=f"Detected pattern: {correlation.get('type')} with {correlation.get('event_count')} events",
            status=IncidentStatus.OPEN,
            severity=severity_mapping.get(
                correlation.get("severity", "medium"), IncidentSeverity.MEDIUM
            ),
            tags=[correlation.get("type")],
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident.id
