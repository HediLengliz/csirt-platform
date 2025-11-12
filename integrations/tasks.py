"""Celery tasks for integration operations."""
from config.celery_app import celery_app
from config.database import SessionLocal
from models.alert import Alert
from models.incident import Incident
from models.integration import Integration, IntegrationType
from integrations.siem_splunk import SplunkIntegration
from integrations.siem_elastic import ElasticIntegration
from integrations.soar_thehive import TheHiveIntegration
from integrations.soar_cortex import CortexIntegration
from integrations.soar_phantom import PhantomIntegration
from typing import Dict, Any


@celery_app.task
def send_alert_to_integrations(alert_id: int):
    """Send alert to all enabled integrations."""
    db = SessionLocal()
    
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return {"error": "Alert not found", "status": "failed"}
        
        integrations = db.query(Integration).filter(Integration.enabled == True).all()
        results = {}
        
        for integration in integrations:
            try:
                integrator = _get_integrator(integration)
                if integrator:
                    success = integrator.send_alert(alert)
                    results[integration.name] = "success" if success else "failed"
                else:
                    results[integration.name] = "not_configured"
            except Exception as e:
                results[integration.name] = f"error: {str(e)}"
        
        return {"alert_id": alert_id, "results": results, "status": "completed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        db.close()


@celery_app.task
def create_incident_in_integrations(incident_id: int):
    """Create incident in all enabled SOAR integrations."""
    db = SessionLocal()
    
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return {"error": "Incident not found", "status": "failed"}
        
        # Only SOAR integrations
        soar_types = [
            IntegrationType.SOAR_THEHIVE,
            IntegrationType.SOAR_CORTEX,
            IntegrationType.SOAR_PHANTOM,
        ]
        
        integrations = db.query(Integration).filter(
            Integration.enabled == True,
            Integration.integration_type.in_(soar_types)
        ).all()
        
        results = {}
        
        for integration in integrations:
            try:
                integrator = _get_integrator(integration)
                if integrator:
                    external_id = integrator.create_incident(incident)
                    results[integration.name] = external_id if external_id else "failed"
                else:
                    results[integration.name] = "not_configured"
            except Exception as e:
                results[integration.name] = f"error: {str(e)}"
        
        return {"incident_id": incident_id, "results": results, "status": "completed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        db.close()


def _get_integrator(integration: Integration):
    """Get integrator instance from integration model."""
    config = integration.config
    
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
    
    return integrator_class(config)

