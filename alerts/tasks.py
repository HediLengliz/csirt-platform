"""Celery tasks for alert processing."""

from typing import List

from alerts.manager import AlertManager
from config.celery_app import celery_app
from config.database import SessionLocal
from models.event import Event


@celery_app.task
def process_events_to_alerts(event_ids: List[int]):
    """Process events and create alerts."""
    db = SessionLocal()
    alert_manager = AlertManager()

    try:
        events = db.query(Event).filter(Event.id.in_(event_ids)).all()

        for event in events:
            # Get context (e.g., count of similar events)
            context = _get_event_context(db, event)

            # Create alert
            alert_manager.create_alert_from_event(db, event, context)

        return {"processed": len(events), "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        db.close()


def _get_event_context(db, event: Event) -> dict:
    """Get enhanced context for event (e.g., similar event counts and patterns)."""
    from datetime import datetime, timedelta

    from sqlalchemy import and_, func, or_

    # Multiple time windows for better context
    time_threshold_1h = datetime.utcnow() - timedelta(hours=1)
    time_threshold_24h = datetime.utcnow() - timedelta(hours=24)

    context = {}

    # Count events from same source IP (1 hour and 24 hours)
    if event.source_ip:
        context["source_ip_count"] = (
            db.query(func.count(Event.id))
            .filter(
                and_(
                    Event.source_ip == event.source_ip,
                    Event.created_at >= time_threshold_1h,
                )
            )
            .scalar()
            or 1
        )

        context["source_ip_count_24h"] = (
            db.query(func.count(Event.id))
            .filter(
                and_(
                    Event.source_ip == event.source_ip,
                    Event.created_at >= time_threshold_24h,
                )
            )
            .scalar()
            or 1
        )
    else:
        context["source_ip_count"] = 1
        context["source_ip_count_24h"] = 1

    # Count events to same destination IP
    if event.destination_ip:
        context["destination_ip_count"] = (
            db.query(func.count(Event.id))
            .filter(
                and_(
                    Event.destination_ip == event.destination_ip,
                    Event.created_at >= time_threshold_1h,
                )
            )
            .scalar()
            or 1
        )
    else:
        context["destination_ip_count"] = 1

    # Count events for same user
    if event.user:
        context["user_count"] = (
            db.query(func.count(Event.id))
            .filter(
                and_(Event.user == event.user, Event.created_at >= time_threshold_1h)
            )
            .scalar()
            or 1
        )
    else:
        context["user_count"] = 1

    # Count similar event types in last hour (pattern detection)
    if event.event_type:
        context["similar_events_count"] = (
            db.query(func.count(Event.id))
            .filter(
                and_(
                    Event.event_type == event.event_type,
                    Event.created_at >= time_threshold_1h,
                    Event.id != event.id,
                )
            )
            .scalar()
            or 0
        )

    return context
