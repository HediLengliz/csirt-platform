"""Events API routes."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from alerts.tasks import process_events_to_alerts
from config.database import get_db
from models.event import Event, EventSource, EventType

router = APIRouter()


class EventCreate(BaseModel):
    """Event creation schema."""

    source: str
    event_type: str
    raw_data: dict
    timestamp: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    user: Optional[str] = None
    hostname: Optional[str] = None
    description: Optional[str] = None
    severity_score: Optional[str] = None


class EventResponse(BaseModel):
    """Event response schema."""

    id: int
    source: str
    event_type: str
    timestamp: Optional[str]
    source_ip: Optional[str]
    destination_ip: Optional[str]
    user: Optional[str]
    hostname: Optional[str]
    description: Optional[str]
    created_at: str

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


@router.post("/", response_model=EventResponse)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event."""
    try:
        db_event = Event(
            source=EventSource(event.source),
            event_type=EventType(event.event_type),
            raw_data=event.raw_data,
            timestamp=event.timestamp or datetime.utcnow().isoformat(),
            source_ip=event.source_ip,
            destination_ip=event.destination_ip,
            user=event.user,
            hostname=event.hostname,
            description=event.description,
            severity_score=event.severity_score,
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        # Trigger alert creation asynchronously
        process_events_to_alerts.delay([db_event.id])

        # Convert to response format
        return EventResponse(
            id=db_event.id,
            source=db_event.source.value,
            event_type=db_event.event_type.value,
            timestamp=db_event.timestamp,
            source_ip=db_event.source_ip,
            destination_ip=db_event.destination_ip,
            user=db_event.user,
            hostname=db_event.hostname,
            description=db_event.description,
            created_at=db_event.created_at.isoformat() if db_event.created_at else "",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[EventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get events with filtering."""
    query = db.query(Event)

    if source:
        query = query.filter(Event.source == EventSource(source))
    if event_type:
        query = query.filter(Event.event_type == EventType(event_type))

    events = query.order_by(Event.created_at.desc()).offset(skip).limit(limit).all()
    return [
        EventResponse(
            id=e.id,
            source=e.source.value,
            event_type=e.event_type.value,
            timestamp=e.timestamp,
            source_ip=e.source_ip,
            destination_ip=e.destination_ip,
            user=e.user,
            hostname=e.hostname,
            description=e.description,
            created_at=e.created_at.isoformat() if e.created_at else "",
        )
        for e in events
    ]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse(
        id=event.id,
        source=event.source.value,
        event_type=event.event_type.value,
        timestamp=event.timestamp,
        source_ip=event.source_ip,
        destination_ip=event.destination_ip,
        user=event.user,
        hostname=event.hostname,
        description=event.description,
        created_at=event.created_at.isoformat() if event.created_at else "",
    )
