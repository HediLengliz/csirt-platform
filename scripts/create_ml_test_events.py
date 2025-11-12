"""Create 10 diverse events to test real-time ML detection."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import SessionLocal
from models.event import Event, EventType, EventSource
from alerts.manager import AlertManager
from alerts.tasks import _get_event_context
from datetime import datetime
import time

def create_ml_test_events():
    """Create 10 diverse events to test real-time ML."""
    db = SessionLocal()
    manager = AlertManager()
    
    print("=" * 70)
    print("Creating 10 Events for Real-Time ML Testing")
    print("=" * 70)
    print()
    
    events_to_create = [
        {
            "name": "Ransomware Attack",
            "source": EventSource.ENDPOINT,
            "event_type": EventType.MALWARE_DETECTED,
            "description": "Ransomware detected on server-01. Files encrypted. Bitcoin payment requested. Decrypt key needed. Exploit detected in system files.",
            "severity_score": "9.5",
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.1",
            "user": "admin",
            "hostname": "server-01"
        },
        {
            "name": "Brute Force Attack",
            "source": EventSource.FIREWALL,
            "event_type": EventType.BRUTE_FORCE,
            "description": "Multiple failed login attempts from IP 10.0.0.50. Unauthorized access attempt detected. Password authentication failed repeatedly.",
            "severity_score": "7.5",
            "source_ip": "10.0.0.50",
            "destination_ip": "192.168.1.10",
            "user": "user1"
        },
        {
            "name": "Data Exfiltration",
            "source": EventSource.NETWORK,
            "event_type": EventType.DATA_EXFILTRATION,
            "description": "Large data transfer detected to external IP. Exfiltration of sensitive data. Suspicious volume of data transferred.",
            "severity_score": "8.5",
            "source_ip": "172.16.0.10",
            "destination_ip": "203.0.113.50",
            "user": "data_analyst"
        },
        {
            "name": "Privilege Escalation",
            "source": EventSource.ENDPOINT,
            "event_type": EventType.UNAUTHORIZED_ACCESS,
            "description": "Privilege escalation detected. User attempted sudo access. Admin privileges requested. Root access attempt.",
            "severity_score": "8.0",
            "source_ip": "192.168.1.50",
            "user": "user2",
            "hostname": "workstation-05"
        },
        {
            "name": "DDoS Attack",
            "source": EventSource.NETWORK,
            "event_type": EventType.DDoS,
            "description": "Distributed Denial of Service attack detected. Traffic flood from multiple IPs. Bandwidth overload. Service unavailable.",
            "severity_score": "7.0",
            "source_ip": "198.51.100.10",
            "destination_ip": "192.168.1.1"
        },
        {
            "name": "Phishing Attempt",
            "source": EventSource.CUSTOM,
            "event_type": EventType.PHISHING,
            "description": "Suspicious email detected. Phishing link in attachment. User clicked suspicious link. Malicious attachment detected.",
            "severity_score": "6.0",
            "source_ip": "192.168.1.75",
            "user": "employee1"
        },
        {
            "name": "Suspicious Activity",
            "source": EventSource.IDS_IPS,
            "event_type": EventType.SUSPICIOUS_ACTIVITY,
            "description": "Unusual network traffic pattern detected. Multiple connection attempts to unknown domains. Suspicious behavior observed.",
            "severity_score": "5.5",
            "source_ip": "172.16.0.20",
            "destination_ip": "192.168.1.20"
        },
        {
            "name": "Login Failure",
            "source": EventSource.CUSTOM,
            "event_type": EventType.LOGIN_FAILURE,
            "description": "Failed login attempt for user admin. Incorrect password entered.",
            "severity_score": "3.0",
            "source_ip": "192.168.1.30",
            "user": "admin"
        },
        {
            "name": "Exploit Attempt",
            "source": EventSource.FIREWALL,
            "event_type": EventType.SUSPICIOUS_ACTIVITY,
            "description": "SQL injection attempt detected. Exploit code in request. CVE-2023-1234 vulnerability targeted. Zero-day exploit attempt.",
            "severity_score": "8.5",
            "source_ip": "203.0.113.100",
            "destination_ip": "192.168.1.15",
            "user": "web_user"
        },
        {
            "name": "Normal Login",
            "source": EventSource.CUSTOM,
            "event_type": EventType.LOGIN_SUCCESS,
            "description": "Successful user login from authorized IP address.",
            "severity_score": "1.0",
            "source_ip": "192.168.1.20",
            "user": "normal_user"
        }
    ]
    
    created_alerts = []
    
    for i, event_data in enumerate(events_to_create, 1):
        print(f"{i}. Creating: {event_data['name']}")
        
        event = Event(
            source=event_data["source"],
            event_type=event_data["event_type"],
            description=event_data["description"],
            severity_score=event_data["severity_score"],
            source_ip=event_data.get("source_ip"),
            destination_ip=event_data.get("destination_ip"),
            user=event_data.get("user"),
            hostname=event_data.get("hostname"),
            raw_data={},
            timestamp=datetime.utcnow().isoformat()
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        # Get context
        context = _get_event_context(db, event)
        
        # Create alert (ML will process automatically)
        alert = manager.create_alert_from_event(db, event, context)
        created_alerts.append(alert)
        
        # Show ML results
        print(f"   ✅ Event ID: {event.id}")
        print(f"   ✅ Alert ID: {alert.id}")
        print(f"   ✅ Title: {alert.title[:60]}...")
        print(f"   ✅ Priority: {alert.priority.value.upper()}")
        print(f"   ✅ ML Score: {alert.ml_score:.1%}")
        
        # Check if ML classification is in description
        if "[ML Classification]" in alert.description:
            print(f"   ✅ ML Classification: Active")
        if "[Anomaly Detection]" in alert.description:
            print(f"   ✅ Anomaly Detection: Active")
        
        print()
        
        # Small delay to see real-time processing
        time.sleep(0.5)
    
    print("=" * 70)
    print("✅ 10 Events Created Successfully!")
    print("=" * 70)
    print()
    print("Summary:")
    for i, alert in enumerate(created_alerts, 1):
        attack_type = ""
        if "[Ransomware]" in alert.title:
            attack_type = "Ransomware"
        elif "[Brute Force]" in alert.title:
            attack_type = "Brute Force"
        elif "[Data Exfiltration]" in alert.title:
            attack_type = "Data Exfiltration"
        elif "[Privilege Escalation]" in alert.title:
            attack_type = "Privilege Escalation"
        elif "[DDoS]" in alert.title:
            attack_type = "DDoS"
        elif "[Phishing]" in alert.title:
            attack_type = "Phishing"
        
        print(f"  {i}. Alert {alert.id}: {alert.priority.value.upper()} | ML: {alert.ml_score:.1%} | {attack_type}")
    
    print()
    print("🎯 Next Steps:")
    print("  1. Go to http://localhost:3000/alerts")
    print("  2. Click on any alert to see ML insights")
    print("  3. Scroll to 'ML Analysis' section")
    print("  4. Click 'Refresh' to see real-time ML analysis")
    print()
    print("=" * 70)
    
    db.close()

if __name__ == "__main__":
    create_ml_test_events()

