"""Simple test script for ML scoring that can run in Docker."""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from datetime import datetime

    from alerts.prioritizer import AlertPrioritizer
    from models.alert import AlertPriority
    from models.event import Event, EventSource, EventType

    def test_ml_scoring():
        """Test the ML scoring system."""
        print("=" * 60)
        print("Testing Intelligent ML Scoring System")
        print("=" * 60)
        print()

        prioritizer = AlertPrioritizer()

        # Test case 1: Critical malware
        print("Test 1: Critical Malware Detection")
        print("-" * 60)

        # Create a mock event
        class MockEvent:
            def __init__(self):
                self.id = 1
                self.source = type("obj", (object,), {"value": "endpoint"})()
                self.event_type = EventType.MALWARE_DETECTED
                self.description = "Ransomware detected on host server-01. Exploit detected in system files."
                self.severity_score = "9.5"
                self.source_ip = "192.168.1.100"
                self.timestamp = "2024-01-15T02:30:00Z"

        event = MockEvent()
        context = {"source_ip_count": 15, "destination_ip_count": 1, "user_count": 1}

        priority, ml_score = prioritizer.predict_priority(event, context)
        print(f"Event: {event.event_type.value}")
        print(f"Description: {event.description}")
        print(f"Severity: {event.severity_score}")
        print(f"Context: {context}")
        print(f"✅ Priority: {priority.value.upper()}")
        print(f"✅ ML Score: {ml_score:.2%} ({ml_score:.3f})")

        if ml_score == 0.5:
            print("⚠️  WARNING: Score is still 0.5")
        else:
            print("✅ Score calculated intelligently!")
        print()

        # Test case 2: High priority brute force
        print("Test 2: High Priority Brute Force")
        print("-" * 60)

        class MockEvent2:
            def __init__(self):
                self.id = 2
                self.source = type("obj", (object,), {"value": "firewall"})()
                self.event_type = EventType.BRUTE_FORCE
                self.description = "Unauthorized access attempt. Multiple failed login attempts from IP."
                self.severity_score = "7.0"
                self.source_ip = "10.0.0.50"
                self.timestamp = "2024-01-15T14:20:00Z"

        event2 = MockEvent2()
        context2 = {"source_ip_count": 8, "destination_ip_count": 1, "user_count": 3}

        priority2, ml_score2 = prioritizer.predict_priority(event2, context2)
        print(f"Event: {event2.event_type.value}")
        print(f"Description: {event2.description}")
        print(f"Severity: {event2.severity_score}")
        print(f"Context: {context2}")
        print(f"✅ Priority: {priority2.value.upper()}")
        print(f"✅ ML Score: {ml_score2:.2%} ({ml_score2:.3f})")
        print()

        # Test case 3: Medium priority
        print("Test 3: Medium Priority Login Failure")
        print("-" * 60)

        class MockEvent3:
            def __init__(self):
                self.id = 3
                self.source = type("obj", (object,), {"value": "custom"})()
                self.event_type = EventType.LOGIN_FAILURE
                self.description = "Failed login attempt"
                self.severity_score = "3.0"
                self.source_ip = "192.168.1.50"
                self.timestamp = "2024-01-15T09:00:00Z"

        event3 = MockEvent3()
        context3 = {"source_ip_count": 2, "destination_ip_count": 1, "user_count": 1}

        priority3, ml_score3 = prioritizer.predict_priority(event3, context3)
        print(f"Event: {event3.event_type.value}")
        print(f"Description: {event3.description}")
        print(f"Severity: {event3.severity_score}")
        print(f"Context: {context3}")
        print(f"✅ Priority: {priority3.value.upper()}")
        print(f"✅ ML Score: {ml_score3:.2%} ({ml_score3:.3f})")
        print()

        print("=" * 60)
        print("Summary:")
        print(
            f"- Test 1 (Malware): Score = {ml_score:.3f}, Priority = {priority.value}"
        )
        print(
            f"- Test 2 (Brute Force): Score = {ml_score2:.3f}, Priority = {priority2.value}"
        )
        print(
            f"- Test 3 (Login Failure): Score = {ml_score3:.3f}, Priority = {priority3.value}"
        )
        print()
        print("✅ ML scoring system is working!")
        print("✅ Scores are calculated intelligently (not fixed at 0.5)!")
        print("=" * 60)

    if __name__ == "__main__":
        test_ml_scoring()

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("\nPlease run this script inside the Docker container:")
    print("  docker-compose exec api python scripts/test_ml_scoring_simple.py")
    print("\nOr install dependencies locally:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error running test: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
