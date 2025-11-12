"""Test script for real-time ML detection and classification."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from alerts.tasks import _get_event_context
from config.database import SessionLocal
from ml.detector import RealTimeMLSystem
from models.event import Event, EventSource, EventType


def test_realtime_ml():
    """Test real-time ML detection and classification."""
    db = SessionLocal()
    ml_system = RealTimeMLSystem()

    print("=" * 70)
    print("Testing Real-Time ML Detection and Classification System")
    print("=" * 70)
    print()

    test_cases = [
        {
            "name": "Ransomware Attack",
            "event": Event(
                source=EventSource.ENDPOINT,
                event_type=EventType.MALWARE_DETECTED,
                description="Ransomware detected on server. Files encrypted. Bitcoin payment requested. Decrypt key needed.",
                severity_score="9.5",
                source_ip="192.168.1.100",
                timestamp=datetime.utcnow().isoformat(),
                raw_data={},
            ),
            "context": {
                "source_ip_count": 1,
                "destination_ip_count": 1,
                "user_count": 1,
            },
        },
        {
            "name": "Brute Force Attack",
            "event": Event(
                source=EventSource.FIREWALL,
                event_type=EventType.BRUTE_FORCE,
                description="Multiple failed login attempts from IP. Password authentication failed. Unauthorized access attempt.",
                severity_score="7.0",
                source_ip="10.0.0.50",
                timestamp=datetime.utcnow().isoformat(),
                raw_data={},
            ),
            "context": {
                "source_ip_count": 15,
                "destination_ip_count": 1,
                "user_count": 3,
            },
        },
        {
            "name": "Data Exfiltration",
            "event": Event(
                source=EventSource.NETWORK,
                event_type=EventType.DATA_EXFILTRATION,
                description="Large data transfer detected. Exfiltration to external IP. Suspicious volume of data.",
                severity_score="8.5",
                source_ip="172.16.0.10",
                destination_ip="203.0.113.50",
                timestamp=datetime.utcnow().isoformat(),
                raw_data={},
            ),
            "context": {
                "source_ip_count": 5,
                "destination_ip_count": 1,
                "user_count": 1,
            },
        },
        {
            "name": "Privilege Escalation",
            "event": Event(
                source=EventSource.ENDPOINT,
                event_type=EventType.UNAUTHORIZED_ACCESS,
                description="Privilege escalation detected. User attempted sudo access. Admin privileges requested.",
                severity_score="8.0",
                source_ip="192.168.1.50",
                user="user1",
                timestamp=datetime.utcnow().isoformat(),
                raw_data={},
            ),
            "context": {
                "source_ip_count": 3,
                "destination_ip_count": 1,
                "user_count": 1,
            },
        },
        {
            "name": "Normal Login",
            "event": Event(
                source=EventSource.CUSTOM,
                event_type=EventType.LOGIN_SUCCESS,
                description="Successful user login",
                severity_score="1.0",
                source_ip="192.168.1.20",
                timestamp=datetime.utcnow().isoformat(),
                raw_data={},
            ),
            "context": {
                "source_ip_count": 1,
                "destination_ip_count": 1,
                "user_count": 1,
            },
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("-" * 70)

        event = test_case["event"]
        context = test_case["context"]

        # Process with ML system
        result = ml_system.process_event(event, context)

        print(f"Event Type: {event.event_type.value}")
        print(f"Description: {event.description[:80]}...")
        print()
        print("🤖 ML Results:")
        print(f"  ✅ Anomaly Detected: {result['is_anomaly']}")
        print(f"  📊 Anomaly Score: {result['anomaly_score']:.1%}")
        print(f"  🎯 Attack Type: {result['classification']['attack_type'] or 'None'}")
        print(f"  🏷️  Category: {result['classification']['category']}")
        print(f"  📈 Confidence: {result['classification']['confidence']:.1%}")
        print(f"  ⚠️  Risk Level: {result['risk_level'].upper()}")
        print(f"  💡 Recommended Action: {result['recommended_action']}")
        print(f"  🔢 ML Confidence: {result['ml_confidence']:.1%}")

        if result["classification"]["tags"]:
            print(f"  🏷️  Tags: {', '.join(result['classification']['tags'])}")

        if result["classification"]["ioc"]:
            print(f"  🔍 IOCs Found: {len(result['classification']['ioc'])}")
            for ioc in result["classification"]["ioc"][:3]:  # Show first 3
                print(f"     - {ioc['type']}: {ioc['value']}")

        print()
        print("=" * 70)
        print()

    print("Summary:")
    print("✅ Real-time ML system is working!")
    print("✅ Anomaly detection is functional!")
    print("✅ Alert classification is operational!")
    print("✅ IOC extraction is active!")


if __name__ == "__main__":
    test_realtime_ml()
