"""Alert management system with real-time ML."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.alert import Alert, AlertStatus, AlertPriority
from models.event import Event
from alerts.prioritizer import AlertPrioritizer
from datetime import datetime
import sys
import os

# Add ml package to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ml.singleton import get_ml_system
    ML_SYSTEM_AVAILABLE = True
except ImportError:
    try:
        from ml.detector import RealTimeMLSystem
        ML_SYSTEM_AVAILABLE = True
        get_ml_system = lambda: RealTimeMLSystem()  # Fallback
    except ImportError:
        ML_SYSTEM_AVAILABLE = False
        print("Warning: Real-time ML system not available. Install required dependencies.")


class AlertManager:
    """Manages alert creation and prioritization with real-time ML."""
    
    def __init__(self, model_path: str = "./models/alert_prioritizer.pkl"):
        """Initialize alert manager."""
        self.prioritizer = AlertPrioritizer(model_path)
        self.ml_system = get_ml_system() if ML_SYSTEM_AVAILABLE else None
    
    def create_alert_from_event(
        self,
        db: Session,
        event: Event,
        context: Dict[str, Any] = None
    ) -> Alert:
        """Create an alert from an event with ML-based prioritization and real-time classification."""
        context = context or {}
        
        # Real-time ML processing
        ml_insights = None
        if self.ml_system:
            try:
                ml_insights = self.ml_system.process_event(event, context)
            except Exception as e:
                print(f"Error in real-time ML processing: {e}")
        
        # Get ML-based priority (use classification if available)
        if ml_insights and ml_insights["classification"]["recommended_priority"]:
            priority = ml_insights["classification"]["recommended_priority"]
            ml_score = ml_insights["ml_confidence"]
        else:
            priority, ml_score = self.prioritizer.predict_priority(event, context)
        
        # Generate alert title (enhanced with classification)
        title = self._generate_alert_title(event, ml_insights)
        
        # Enhanced description with ML insights
        description = event.description or f"Security event detected: {event.event_type.value}"
        if ml_insights:
            if ml_insights["classification"]["attack_type"]:
                description += f"\n\n[ML Classification] Attack Type: {ml_insights['classification']['attack_type']}"
                description += f"\nConfidence: {ml_insights['classification']['confidence']:.1%}"
            if ml_insights["is_anomaly"]:
                description += f"\n[Anomaly Detection] Anomaly Score: {ml_insights['anomaly_score']:.1%}"
            if ml_insights["recommended_action"]:
                description += f"\nRecommended Action: {ml_insights['recommended_action']}"
        
        # Create alert
        alert = Alert(
            title=title,
            description=description,
            status=AlertStatus.NEW,
            priority=priority,
            ml_score=ml_score,
            source=event.source.value,
            event_id=event.id
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        return alert
    
    def _generate_alert_title(self, event: Event, ml_insights: Dict[str, Any] = None) -> str:
        """Generate alert title from event, enhanced with ML classification."""
        event_type = event.event_type.value.replace("_", " ").title()
        source = event.source.value.upper()
        
        # Add ML classification to title if available
        prefix = ""
        if ml_insights and ml_insights["classification"]["attack_type"]:
            attack_type = ml_insights["classification"]["attack_type"].replace("_", " ").title()
            prefix = f"[{attack_type}] "
        
        if event.source_ip:
            return f"{prefix}{event_type} detected from {event.source_ip} ({source})"
        elif event.user:
            return f"{prefix}{event_type} detected for user {event.user} ({source})"
        else:
            return f"{prefix}{event_type} detected ({source})"
    
    def update_alert_status(
        self,
        db: Session,
        alert_id: int,
        status: AlertStatus,
        notes: str = None
    ) -> Optional[Alert]:
        """Update alert status."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = status
        if notes:
            alert.description = f"{alert.description}\n\nUpdate: {notes}"
        
        db.commit()
        db.refresh(alert)
        return alert
    
    def get_alerts_by_priority(
        self,
        db: Session,
        priority: AlertPriority,
        limit: int = 100
    ) -> List[Alert]:
        """Get alerts by priority level."""
        return db.query(Alert).filter(
            Alert.priority == priority,
            Alert.status != AlertStatus.RESOLVED
        ).order_by(Alert.created_at.desc()).limit(limit).all()
    
    def get_critical_alerts(self, db: Session, limit: int = 50) -> List[Alert]:
        """Get critical alerts."""
        return self.get_alerts_by_priority(db, AlertPriority.CRITICAL, limit)
