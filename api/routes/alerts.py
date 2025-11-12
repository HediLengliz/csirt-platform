"""Alerts API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from models.alert import Alert, AlertStatus, AlertPriority
from alerts.manager import AlertManager
from alerts.tasks import process_events_to_alerts
from integrations.tasks import send_alert_to_integrations
from pydantic import BaseModel

router = APIRouter()


class AlertResponse(BaseModel):
    """Alert response schema."""
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    ml_score: Optional[float]
    source: str
    created_at: str
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    """Alert update schema."""
    status: Optional[str] = None
    notes: Optional[str] = None


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get alerts with filtering."""
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == AlertStatus(status))
    if priority:
        query = query.filter(Alert.priority == AlertPriority(priority))
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return [
        AlertResponse(
            id=a.id,
            title=a.title,
            description=a.description,
            status=a.status.value,
            priority=a.priority.value,
            ml_score=a.ml_score,
            source=a.source,
            created_at=a.created_at.isoformat() if a.created_at else "",
        )
        for a in alerts
    ]


@router.get("/critical", response_model=List[AlertResponse])
async def get_critical_alerts(limit: int = 50, db: Session = Depends(get_db)):
    """Get critical alerts."""
    alert_manager = AlertManager()
    alerts = alert_manager.get_critical_alerts(db, limit)
    return [
        AlertResponse(
            id=a.id,
            title=a.title,
            description=a.description,
            status=a.status.value,
            priority=a.priority.value,
            ml_score=a.ml_score,
            source=a.source,
            created_at=a.created_at.isoformat() if a.created_at else "",
        )
        for a in alerts
    ]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse(
        id=alert.id,
        title=alert.title,
        description=alert.description,
        status=alert.status.value,
        priority=alert.priority.value,
        ml_score=alert.ml_score,
        source=alert.source,
        created_at=alert.created_at.isoformat() if alert.created_at else "",
    )


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update alert status."""
    alert_manager = AlertManager()
    
    status = None
    if alert_update.status:
        status = AlertStatus(alert_update.status)
    
    alert = alert_manager.update_alert_status(
        db, alert_id, status, alert_update.notes
    )
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse(
        id=alert.id,
        title=alert.title,
        description=alert.description,
        status=alert.status.value,
        priority=alert.priority.value,
        ml_score=alert.ml_score,
        source=alert.source,
        created_at=alert.created_at.isoformat() if alert.created_at else "",
    )


@router.post("/{alert_id}/send", response_model=dict)
async def send_alert(alert_id: int, db: Session = Depends(get_db)):
    """Send alert to integrations."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Trigger async task
    task = send_alert_to_integrations.delay(alert_id)
    
    return {
        "message": "Alert sending initiated",
        "task_id": task.id,
        "alert_id": alert_id
    }
