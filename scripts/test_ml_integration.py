"""Test ML integration with alert creation."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import SessionLocal
from models.event import Event, EventType, EventSource
from alerts.manager import AlertManager
from alerts.tasks import _get_event_context
from datetime import datetime

def test_ml_integration():
    """Test if ML is working when creating alerts."""
    db = SessionLocal()
    manager = AlertManager()
    
    print("=" * 70)
    print("Testing ML Integration with Alert Creation")
    print("=" * 70)
    print()
    
    # Check if ML system is available
    print(f"ML System Available: {manager.ml_system is not None}")
    print()
    
    # Create a test event with ransomware keywords
    print("Creating test event with ransomware...")
    event = Event(
        source=EventSource.ENDPOINT,
        event_type=EventType.MALWARE_DETECTED,
        description="Ransomware detected on server. Files encrypted. Bitcoin payment requested. Decrypt key needed.",
        severity_score="9.5",
        source_ip="192.168.1.100",
        destination_ip="10.0.0.1",
        user="admin",
        hostname="server-01",
        raw_data={},
        timestamp=datetime.utcnow().isoformat()
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    print(f"✅ Event created: ID {event.id}")
    print()
    
    # Get context
    context = _get_event_context(db, event)
    print(f"Context: {context}")
    print()
    
    # Test ML processing directly
    if manager.ml_system:
        print("Testing ML processing...")
        try:
            ml_insights = manager.ml_system.process_event(event, context)
            print("✅ ML Processing Successful!")
            print(f"  - Is Anomaly: {ml_insights['is_anomaly']}")
            print(f"  - Anomaly Score: {ml_insights['anomaly_score']:.1%}")
            print(f"  - Attack Type: {ml_insights['classification']['attack_type']}")
            print(f"  - Confidence: {ml_insights['classification']['confidence']:.1%}")
            print(f"  - Risk Level: {ml_insights['risk_level']}")
            print(f"  - Recommended Action: {ml_insights['recommended_action']}")
            print(f"  - IOCs: {len(ml_insights['classification']['ioc'])} found")
            print()
        except Exception as e:
            print(f"❌ ML Processing Error: {e}")
            import traceback
            traceback.print_exc()
            print()
    else:
        print("❌ ML System not available!")
        print()
    
    # Create alert (this should use ML automatically)
    print("Creating alert from event (should use ML automatically)...")
    try:
        alert = manager.create_alert_from_event(db, event, context)
        print(f"✅ Alert created: ID {alert.id}")
        print(f"  - Title: {alert.title}")
        print(f"  - Priority: {alert.priority.value}")
        print(f"  - ML Score: {alert.ml_score:.1%}")
        print(f"  - Description length: {len(alert.description)} chars")
        
        # Check if ML insights are in description
        if "[ML Classification]" in alert.description:
            print("  ✅ ML Classification found in description!")
        else:
            print("  ⚠️  ML Classification NOT found in description")
        
        if "[Anomaly Detection]" in alert.description:
            print("  ✅ Anomaly Detection found in description!")
        else:
            print("  ⚠️  Anomaly Detection NOT found in description")
        
        print()
    except Exception as e:
        print(f"❌ Alert Creation Error: {e}")
        import traceback
        traceback.print_exc()
        print()
    
    print("=" * 70)
    db.close()

if __name__ == "__main__":
    test_ml_integration()

