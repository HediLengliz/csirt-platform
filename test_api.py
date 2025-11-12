"""Quick test script for CSIRT Platform API."""

import json
import time

import requests

API_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_health_check():
    """Test health check endpoint."""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_create_event():
    """Test creating an event."""
    print_section("2. Create Event")
    event_data = {
        "source": "custom",
        "event_type": "suspicious_activity",
        "raw_data": {"test": "data", "source": "test_script"},
        "timestamp": "2024-01-15T10:30:00",
        "source_ip": "192.168.1.100",
        "destination_ip": "192.168.1.200",
        "user": "test_user",
        "hostname": "test-server",
        "description": "Test event from Python script",
        "severity_score": "7.5",
    }

    try:
        response = requests.post(
            f"{API_URL}/api/v1/events/",
            json=event_data,
            headers={"Content-Type": "application/json"},
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            event = response.json()
            print(f"Event created: ID={event.get('id')}")
            print(f"Event type: {event.get('event_type')}")
            return event.get("id")
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_list_events():
    """Test listing events."""
    print_section("3. List Events")
    try:
        response = requests.get(f"{API_URL}/api/v1/events/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            events = response.json()
            print(f"Total events: {len(events)}")
            if events:
                print(
                    f"First event: ID={events[0].get('id')}, Type={events[0].get('event_type')}"
                )
            return len(events)
        else:
            print(f"Error: {response.text}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0


def test_list_alerts():
    """Test listing alerts."""
    print_section("4. List Alerts")
    try:
        response = requests.get(f"{API_URL}/api/v1/alerts/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            alerts = response.json()
            print(f"Total alerts: {len(alerts)}")
            if alerts:
                alert = alerts[0]
                print(
                    f"First alert: ID={alert.get('id')}, Priority={alert.get('priority')}, Status={alert.get('status')}"
                )
                if alert.get("ml_score"):
                    print(f"ML Score: {alert.get('ml_score')}")
            return len(alerts)
        else:
            print(f"Error: {response.text}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0


def test_get_critical_alerts():
    """Test getting critical alerts."""
    print_section("5. Get Critical Alerts")
    try:
        response = requests.get(f"{API_URL}/api/v1/alerts/critical")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            alerts = response.json()
            print(f"Critical alerts: {len(alerts)}")
            return len(alerts)
        else:
            print(f"Error: {response.text}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0


def test_create_incident():
    """Test creating an incident."""
    print_section("6. Create Incident")
    incident_data = {
        "title": "Test Security Incident",
        "description": "Incident created from test script",
        "severity": "high",
        "tags": ["test", "automated"],
        "ioc": [{"type": "ip", "value": "192.168.1.100"}],
    }

    try:
        response = requests.post(
            f"{API_URL}/api/v1/incidents/",
            json=incident_data,
            headers={"Content-Type": "application/json"},
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            incident = response.json()
            print(f"Incident created: ID={incident.get('id')}")
            print(f"Severity: {incident.get('severity')}")
            return incident.get("id")
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_list_incidents():
    """Test listing incidents."""
    print_section("7. List Incidents")
    try:
        response = requests.get(f"{API_URL}/api/v1/incidents/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            incidents = response.json()
            print(f"Total incidents: {len(incidents)}")
            if incidents:
                print(
                    f"First incident: ID={incidents[0].get('id')}, Severity={incidents[0].get('severity')}"
                )
            return len(incidents)
        else:
            print(f"Error: {response.text}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0


def test_create_multiple_events():
    """Test creating multiple events for correlation."""
    print_section("8. Create Multiple Events (for correlation testing)")
    events_created = 0
    for i in range(3):
        event_data = {
            "source": "custom",
            "event_type": "login_failure",
            "raw_data": {"attempt": i + 1},
            "source_ip": "192.168.1.100",  # Same IP for correlation
            "description": f"Failed login attempt {i + 1}",
        }
        try:
            response = requests.post(
                f"{API_URL}/api/v1/events/",
                json=event_data,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                events_created += 1
                print(f"Event {i + 1} created")
            time.sleep(1)  # Small delay
        except Exception as e:
            print(f"Error creating event {i + 1}: {e}")

    print(f"Total events created: {events_created}")
    return events_created


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CSIRT Platform API Test Suite")
    print("=" * 60)
    print(f"API URL: {API_URL}")

    results = {
        "health_check": test_health_check(),
        "create_event": test_create_event(),
        "list_events": test_list_events(),
        "list_alerts": test_list_alerts(),
        "critical_alerts": test_get_critical_alerts(),
        "create_incident": test_create_incident(),
        "list_incidents": test_list_incidents(),
        "multiple_events": test_create_multiple_events(),
    }

    print_section("Test Summary")
    print(f"Health Check: {'PASS' if results['health_check'] else 'FAIL'}")
    print(f"Create Event: {'PASS' if results['create_event'] else 'FAIL'}")
    print(f"List Events: {results['list_events']} events found")
    print(f"List Alerts: {results['list_alerts']} alerts found")
    print(f"Critical Alerts: {results['critical_alerts']} critical alerts")
    print(f"Create Incident: {'PASS' if results['create_incident'] else 'FAIL'}")
    print(f"List Incidents: {results['list_incidents']} incidents found")
    print(f"Multiple Events: {results['multiple_events']} events created")

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check alerts were generated (wait a few seconds)")
    print("2. Check Celery worker logs: docker-compose logs -f celery-worker")
    print(
        "3. Check database: docker-compose exec postgres psql -U csirt_user -d csirt_db -c 'SELECT COUNT(*) FROM alerts;'"
    )
    print("4. Visit API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
