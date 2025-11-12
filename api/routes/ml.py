"""API routes for ML system management."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from alerts.tasks import _get_event_context
from config.database import get_db
from ml.singleton import get_ml_system
from models.event import Event

router = APIRouter(prefix="/ml", tags=["ML"])

# Use singleton instance to share state
ml_system = get_ml_system()


@router.post("/detect/{event_id}")
async def detect_anomaly(event_id: int, db: Session = Depends(get_db)):
    """Detect anomaly for a specific event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    context = _get_event_context(db, event)
    result = ml_system.process_event(event, context)

    return {
        "event_id": event_id,
        "is_anomaly": result["is_anomaly"],
        "anomaly_score": result["anomaly_score"],
        "classification": result["classification"],
        "risk_level": result["risk_level"],
        "recommended_action": result["recommended_action"],
        "ml_confidence": result["ml_confidence"],
    }


@router.post("/classify/{event_id}")
async def classify_event(event_id: int, db: Session = Depends(get_db)):
    """Classify an event using ML."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    context = _get_event_context(db, event)
    classification = ml_system.classifier.classify_alert(event, context)

    return {"event_id": event_id, "classification": classification}


@router.get("/stats")
async def get_ml_stats(db: Session = Depends(get_db)):
    """Get ML system statistics."""
    # Populate window with recent events if empty
    if len(ml_system.event_window) == 0:
        try:
            from alerts.tasks import _get_event_context

            recent_events = (
                db.query(Event).order_by(Event.created_at.desc()).limit(100).all()
            )
            for event in recent_events:
                context = _get_event_context(db, event)
                ml_system.process_event(event, context)
        except Exception as e:
            print(f"Error populating ML window: {e}")

    return {
        "anomaly_detector_trained": ml_system.anomaly_detector.is_trained,
        "events_in_window": len(ml_system.event_window),
        "patterns_loaded": len(ml_system.classifier.patterns),
    }


@router.post("/update-models")
async def update_models(event_ids: List[int], db: Session = Depends(get_db)):
    """Update ML models with training data from events."""
    events = db.query(Event).filter(Event.id.in_(event_ids)).all()
    if len(events) < 10:
        raise HTTPException(
            status_code=400, detail="Need at least 10 events for training"
        )

    contexts = [_get_event_context(db, event) for event in events]
    ml_system.update_models(events, contexts)

    return {
        "status": "success",
        "events_used": len(events),
        "message": "ML models updated successfully",
    }
