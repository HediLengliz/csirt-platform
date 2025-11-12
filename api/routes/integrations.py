"""Integrations API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from models.integration import Integration, IntegrationType
from integrations.siem_splunk import SplunkIntegration
from integrations.siem_elastic import ElasticIntegration
from integrations.soar_thehive import TheHiveIntegration
from integrations.soar_cortex import CortexIntegration
from integrations.soar_phantom import PhantomIntegration
from pydantic import BaseModel

router = APIRouter()


class IntegrationCreate(BaseModel):
    """Integration creation schema."""
    name: str
    integration_type: str
    config: dict
    enabled: bool = True


class IntegrationResponse(BaseModel):
    """Integration response schema."""
    id: int
    name: str
    integration_type: str
    enabled: bool
    status: Optional[str]
    last_sync: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/", response_model=IntegrationResponse)
async def create_integration(integration: IntegrationCreate, db: Session = Depends(get_db)):
    """Create a new integration."""
    try:
        db_integration = Integration(
            name=integration.name,
            integration_type=IntegrationType(integration.integration_type),
            config=integration.config,
            enabled=integration.enabled,
        )
        db.add(db_integration)
        db.commit()
        db.refresh(db_integration)
        return db_integration
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[IntegrationResponse])
async def get_integrations(db: Session = Depends(get_db)):
    """Get all integrations."""
    integrations = db.query(Integration).all()
    return integrations


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(integration_id: int, db: Session = Depends(get_db)):
    """Get a specific integration."""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.post("/{integration_id}/test", response_model=dict)
async def test_integration(integration_id: int, db: Session = Depends(get_db)):
    """Test integration connection."""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Get integrator instance
    integrator = _get_integrator(integration)
    if not integrator:
        raise HTTPException(status_code=400, detail="Unknown integration type")
    
    # Test connection
    connected = integrator.connect()
    status = integrator.get_status()
    
    # Update integration status
    integration.status = "active" if connected else "error"
    db.commit()
    
    return {
        "connected": connected,
        "status": status
    }


def _get_integrator(integration: Integration):
    """Get integrator instance from integration model."""
    type_mapping = {
        IntegrationType.SIEM_SPLUNK: SplunkIntegration,
        IntegrationType.SIEM_ELASTIC: ElasticIntegration,
        IntegrationType.SOAR_THEHIVE: TheHiveIntegration,
        IntegrationType.SOAR_CORTEX: CortexIntegration,
        IntegrationType.SOAR_PHANTOM: PhantomIntegration,
    }
    
    integrator_class = type_mapping.get(integration.integration_type)
    if not integrator_class:
        return None
    
    return integrator_class(integration.config)

