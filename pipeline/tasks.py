"""Celery tasks for pipeline processing."""
from config.celery_app import celery_app
from config.database import SessionLocal
from pipeline.processor import EventProcessor
from pipeline.correlator import EventCorrelator
from detection.splunk_detector import SplunkDetector
from detection.elastic_detector import ElasticDetector
from detection.endpoint_detector import EndpointDetector
from detection.network_detector import NetworkDetector
from models.integration import Integration, IntegrationType
from config.settings import settings
from typing import Dict, Any


@celery_app.task
def collect_events_from_sources():
    """Collect events from all configured sources."""
    db = SessionLocal()
    processor = EventProcessor()
    
    try:
        # Get enabled integrations
        integrations = db.query(Integration).filter(Integration.enabled == True).all()
        all_events = []
        
        for integration in integrations:
            try:
                detector = _get_detector(integration)
                if detector:
                    events = detector.detect_events()
                    all_events.extend(events)
            except Exception as e:
                print(f"Error collecting events from {integration.name}: {e}")
                continue
        
        # Process all collected events
        if all_events:
            result = processor.process_events(all_events)
            return result
        
        return {"status": "success", "events_collected": 0}
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        db.close()


@celery_app.task
def correlate_events():
    """Correlate events and create incidents if needed."""
    db = SessionLocal()
    correlator = EventCorrelator()
    
    try:
        correlations = correlator.correlate_events(time_window_minutes=60)
        
        incident_ids = []
        for correlation in correlations:
            if correlation.get("severity") in ["high", "critical"]:
                incident_id = correlator.create_incident_from_correlation(correlation, db)
                incident_ids.append(incident_id)
        
        return {
            "status": "success",
            "correlations_found": len(correlations),
            "incidents_created": len(incident_ids),
            "incident_ids": incident_ids
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}
    finally:
        db.close()


def _get_detector(integration: Integration):
    """Get detector instance from integration model."""
    config = integration.config
    
    type_mapping = {
        IntegrationType.SIEM_SPLUNK: SplunkDetector,
        IntegrationType.SIEM_ELASTIC: ElasticDetector,
    }
    
    detector_class = type_mapping.get(integration.integration_type)
    if not detector_class:
        return None
    
    # Map integration config to detector config
    if integration.integration_type == IntegrationType.SIEM_SPLUNK:
        detector_config = {
            "host": config.get("host") or settings.SPLUNK_HOST,
            "port": config.get("port", settings.SPLUNK_PORT),
            "username": config.get("username") or settings.SPLUNK_USERNAME,
            "password": config.get("password") or settings.SPLUNK_PASSWORD,
            "verify_ssl": config.get("verify_ssl", settings.SPLUNK_VERIFY_SSL),
            "search_query": config.get("search_query"),
            "max_results": config.get("max_results", 1000),
        }
    elif integration.integration_type == IntegrationType.SIEM_ELASTIC:
        detector_config = {
            "host": config.get("host") or settings.ELASTIC_HOST,
            "port": config.get("port", settings.ELASTIC_PORT),
            "username": config.get("username") or settings.ELASTIC_USERNAME,
            "password": config.get("password") or settings.ELASTIC_PASSWORD,
            "verify_ssl": config.get("verify_ssl", settings.ELASTIC_VERIFY_SSL),
            "indices": config.get("indices"),
            "max_results": config.get("max_results", 1000),
        }
    else:
        return None
    
    return detector_class(detector_config)

