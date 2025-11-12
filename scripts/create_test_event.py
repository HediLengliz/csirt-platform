"""Create a test event to verify ML scoring works."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import SessionLocal
from models.event import Event, EventType, EventSource
from alerts.manager import AlertManager
from alerts.tasks import _get_event_context
from datetime import datetime

def create_test_events():
    """Create test events with different characteristics."""
    db = SessionLocal()
    manager = AlertManager()
    
    try:
        print("Creating test events to verify ML scoring...")
        print("=" * 60)
        
        # Test 1: Critical - Malware
        print("\n1. Creating Critical Malware Event...")
        event1 = Event(
            source=EventSource.ENDPOINT,
            event_type=EventType.MALWARE_DETECTED,
            description="Ransomware detected on host server-01. Exploit detected in system files. Unauthorized access attempt.",
            severity_score="9.5",
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            user="admin",
            hostname="server-01",
            raw_data={},
            timestamp=datetime.utcnow().isoformat()
        )
        db.add(event1)
        db.commit()
        db.refresh(event1)
        
        context1 = _get_event_context(db, event1)
        alert1 = manager.create_alert_from_event(db, event1, context1)
        print(f"   ✅ Event ID: {event1.id}")
        print(f"   ✅ Alert ID: {alert1.id}")
        print(f"   ✅ Priority: {alert1.priority.value.upper()}")
        print(f"   ✅ ML Score: {alert1.ml_score:.3f} ({alert1.ml_score*100:.1f}%)")
        
        # Test 2: High - Brute Force
        print("\n2. Creating High Priority Brute Force Event...")
        event2 = Event(
            source=EventSource.FIREWALL,
            event_type=EventType.BRUTE_FORCE,
            description="Unauthorized access attempt detected. Multiple failed login attempts from IP. Attack pattern detected.",
            severity_score="7.0",
            source_ip="10.0.0.50",
            destination_ip="192.168.1.10",
            user="user1",
            raw_data={},
            timestamp=datetime.utcnow().isoformat()
        )
        db.add(event2)
        db.commit()
        db.refresh(event2)
        
        context2 = _get_event_context(db, event2)
        alert2 = manager.create_alert_from_event(db, event2, context2)
        print(f"   ✅ Event ID: {event2.id}")
        print(f"   ✅ Alert ID: {alert2.id}")
        print(f"   ✅ Priority: {alert2.priority.value.upper()}")
        print(f"   ✅ ML Score: {alert2.ml_score:.3f} ({alert2.ml_score*100:.1f}%)")
        
        # Test 3: Medium - Suspicious Activity
        print("\n3. Creating Medium Priority Suspicious Activity Event...")
        event3 = Event(
            source=EventSource.NETWORK,
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            description="Unusual network traffic pattern detected",
            severity_score="5.0",
            source_ip="172.16.0.10",
            destination_ip="192.168.1.20",
            raw_data={},
            timestamp=datetime.utcnow().isoformat()
        )
        db.add(event3)
        db.commit()
        db.refresh(event3)
        
        context3 = _get_event_context(db, event3)
        alert3 = manager.create_alert_from_event(db, event3, context3)
        print(f"   ✅ Event ID: {event3.id}")
        print(f"   ✅ Alert ID: {alert3.id}")
        print(f"   ✅ Priority: {alert3.priority.value.upper()}")
        print(f"   ✅ ML Score: {alert3.ml_score:.3f} ({alert3.ml_score*100:.1f}%)")
        
        # Test 4: Low - Login Failure
        print("\n4. Creating Low Priority Login Failure Event...")
        event4 = Event(
            source=EventSource.CUSTOM,
            event_type=EventType.LOGIN_FAILURE,
            description="Failed login attempt",
            severity_score="2.0",
            source_ip="192.168.1.50",
            user="user2",
            raw_data={},
            timestamp=datetime.utcnow().isoformat()
        )
        db.add(event4)
        db.commit()
        db.refresh(event4)
        
        context4 = _get_event_context(db, event4)
        alert4 = manager.create_alert_from_event(db, event4, context4)
        print(f"   ✅ Event ID: {event4.id}")
        print(f"   ✅ Alert ID: {alert4.id}")
        print(f"   ✅ Priority: {alert4.priority.value.upper()}")
        print(f"   ✅ ML Score: {alert4.ml_score:.3f} ({alert4.ml_score*100:.1f}%)")
        
        print("\n" + "=" * 60)
        print("Summary:")
        print(f"  Critical Alert: ML Score = {alert1.ml_score:.3f} ({alert1.ml_score*100:.1f}%)")
        print(f"  High Alert: ML Score = {alert2.ml_score:.3f} ({alert2.ml_score*100:.1f}%)")
        print(f"  Medium Alert: ML Score = {alert3.ml_score:.3f} ({alert3.ml_score*100:.1f}%)")
        print(f"  Low Alert: ML Score = {alert4.ml_score:.3f} ({alert4.ml_score*100:.1f}%)")
        print("\n✅ Test events created successfully!")
        print("✅ Check the frontend at http://localhost:3000/alerts to see the ML scores!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error creating test events: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_events()

