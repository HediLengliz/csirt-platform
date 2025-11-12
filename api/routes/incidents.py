"""Incidents API routes."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.database import get_db
from integrations.tasks import create_incident_in_integrations
from models.incident import Incident, IncidentSeverity, IncidentStatus

router = APIRouter()


class IncidentCreate(BaseModel):
    """Incident creation schema."""

    title: str
    description: Optional[str] = None
    severity: str
    alert_id: Optional[int] = None
    tags: Optional[List[str]] = None
    ioc: Optional[List[dict]] = None


class IncidentResponse(BaseModel):
    """Incident response schema."""

    id: int
    title: str
    description: Optional[str]
    status: str
    severity: str
    assigned_to: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class IncidentUpdate(BaseModel):
    """Incident update schema."""

    status: Optional[str] = None
    severity: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    ioc: Optional[List[dict]] = None


@router.post("/", response_model=IncidentResponse)
async def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    """Create a new incident."""
    try:
        db_incident = Incident(
            title=incident.title,
            description=incident.description,
            status=IncidentStatus.OPEN,
            severity=IncidentSeverity(incident.severity),
            alert_id=incident.alert_id,
            tags=incident.tags,
            ioc=incident.ioc,
        )
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)

        # Trigger async task to create incident in SOAR systems
        create_incident_in_integrations.delay(db_incident.id)

        return IncidentResponse(
            id=db_incident.id,
            title=db_incident.title,
            description=db_incident.description,
            status=db_incident.status.value,
            severity=db_incident.severity.value,
            assigned_to=db_incident.assigned_to,
            created_at=(
                db_incident.created_at.isoformat() if db_incident.created_at else ""
            ),
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[IncidentResponse])
async def get_incidents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get incidents with filtering."""
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == IncidentStatus(status))
    if severity:
        query = query.filter(Incident.severity == IncidentSeverity(severity))

    incidents = (
        query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    )
    return [
        IncidentResponse(
            id=i.id,
            title=i.title,
            description=i.description,
            status=i.status.value,
            severity=i.severity.value,
            assigned_to=i.assigned_to,
            created_at=i.created_at.isoformat() if i.created_at else "",
        )
        for i in incidents
    ]


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get a specific incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        status=incident.status.value,
        severity=incident.severity.value,
        assigned_to=incident.assigned_to,
        created_at=incident.created_at.isoformat() if incident.created_at else "",
    )


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int, incident_update: IncidentUpdate, db: Session = Depends(get_db)
):
    """Update incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident_update.status:
        incident.status = IncidentStatus(incident_update.status)
    if incident_update.severity:
        incident.severity = IncidentSeverity(incident_update.severity)
    if incident_update.assigned_to:
        incident.assigned_to = incident_update.assigned_to
    if incident_update.resolution_notes:
        incident.resolution_notes = incident_update.resolution_notes
    if incident_update.tags:
        incident.tags = incident_update.tags
    if incident_update.ioc:
        incident.ioc = incident_update.ioc

    db.commit()
    db.refresh(incident)
    return IncidentResponse(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        status=incident.status.value,
        severity=incident.severity.value,
        assigned_to=incident.assigned_to,
        created_at=incident.created_at.isoformat() if incident.created_at else "",
    )
