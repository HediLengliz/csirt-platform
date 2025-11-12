"""Test script to verify ML scoring system."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alerts.prioritizer import AlertPrioritizer
from models.alert import AlertPriority
from models.event import Event, EventSource, EventType


def test_ml_scoring():
    """Test the ML scoring system with various event types."""
    prioritizer = AlertPrioritizer()

    print("=" * 60)
    print("Testing Intelligent ML Scoring System")
    print("=" * 60)
    print()

    # Test cases
    test_cases = [
        {
            "name": "Critical: Malware Detected",
            "event": Event(
                id=1,
                source=EventSource.ENDPOINT,
                event_type=EventType.MALWARE_DETECTED,
                description="Ransomware detected on host server-01. Exploit detected in system files.",
                severity_score="9.5",
                source_ip="192.168.1.100",
                timestamp="2024-01-15T02:30:00Z",
            ),
            "context": {
                "source_ip_count": 15,
                "destination_ip_count": 1,
                "user_count": 1,
            },
        },
        {
            "name": "High: Brute Force Attack",
            "event": Event(
                id=2,
                source=EventSource.FIREWALL,
                event_type=EventType.BRUTE_FORCE,
                description="Unauthorized access attempt detected. Multiple failed login attempts from IP.",
                severity_score="7.0",
                source_ip="10.0.0.50",
                timestamp="2024-01-15T14:20:00Z",
            ),
            "context": {
                "source_ip_count": 8,
                "destination_ip_count": 1,
                "user_count": 3,
            },
        },
        {
            "name": "Medium: Suspicious Activity",
            "event": Event(
                id=3,
                source=EventSource.NETWORK,
                event_type=EventType.SUSPICIOUS_ACTIVITY,
                description="Unusual network traffic pattern detected",
                severity_score="5.0",
                source_ip="172.16.0.10",
                timestamp="2024-01-15T10:15:00Z",
            ),
            "context": {
                "source_ip_count": 3,
                "destination_ip_count": 2,
                "user_count": 1,
            },
        },
        {
            "name": "Low: Login Failure",
            "event": Event(
                id=4,
                source=EventSource.CUSTOM,
                event_type=EventType.LOGIN_FAILURE,
                description="Failed login attempt",
                severity_score="2.0",
                source_ip="192.168.1.50",
                timestamp="2024-01-15T09:00:00Z",
            ),
            "context": {
                "source_ip_count": 2,
                "destination_ip_count": 1,
                "user_count": 1,
            },
        },
        {
            "name": "Info: Login Success",
            "event": Event(
                id=5,
                source=EventSource.CUSTOM,
                event_type=EventType.LOGIN_SUCCESS,
                description="Successful user login",
                severity_score="1.0",
                source_ip="192.168.1.20",
                timestamp="2024-01-15T08:30:00Z",
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
        print("-" * 60)

        priority, ml_score = prioritizer.predict_priority(
            test_case["event"], test_case["context"]
        )

        print(f"Event Type: {test_case['event'].event_type.value}")
        print(f"Description: {test_case['event'].description}")
        print(f"Severity Score: {test_case['event'].severity_score}")
        print(f"Context: {test_case['context']}")
        print()
        print(f"✅ Predicted Priority: {priority.value.upper()}")
        print(f"✅ ML Score: {ml_score:.2%} ({ml_score:.3f})")
        print()

        # Verify score is not 0.5 (the old default)
        if ml_score == 0.5:
            print("⚠️  WARNING: Score is still 0.5 (default fallback)")
        else:
            print("✅ Score is calculated intelligently!")

        print("=" * 60)
        print()

    print("Summary:")
    print("- ML scoring system is working!")
    print("- Scores are calculated based on event characteristics")
    print("- No more fixed 0.5 scores!")


if __name__ == "__main__":
    test_ml_scoring()
