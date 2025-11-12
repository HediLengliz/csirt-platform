"""Generate synthetic training data for ML model."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta

from models.alert import AlertPriority
from models.event import EventSource, EventType


def generate_training_data(num_samples: int = 100) -> list:
    """Generate synthetic training data for ML model."""
    training_data = []

    # Event type to priority mapping for training
    event_priority_map = {
        EventType.MALWARE_DETECTED: AlertPriority.CRITICAL,
        EventType.UNAUTHORIZED_ACCESS: AlertPriority.CRITICAL,
        EventType.DATA_EXFILTRATION: AlertPriority.CRITICAL,
        EventType.DDoS: AlertPriority.HIGH,
        EventType.BRUTE_FORCE: AlertPriority.HIGH,
        EventType.SUSPICIOUS_ACTIVITY: AlertPriority.HIGH,
        EventType.PHISHING: AlertPriority.MEDIUM,
        EventType.LOGIN_FAILURE: AlertPriority.MEDIUM,
        EventType.LOGIN_SUCCESS: AlertPriority.LOW,
        EventType.OTHER: AlertPriority.INFO,
    }

    # Keywords that affect priority
    critical_keywords = ["malware", "ransomware", "breach", "exploit"]
    high_keywords = ["unauthorized", "attack", "intrusion"]
    medium_keywords = ["suspicious", "failed", "attempt"]

    for i in range(num_samples):
        event_type = random.choice(list(EventType))
        base_priority = event_priority_map.get(event_type, AlertPriority.MEDIUM)

        # Generate description with varying keywords
        description = f"Security event: {event_type.value}"
        if random.random() < 0.3:
            if base_priority == AlertPriority.CRITICAL:
                description += f" - {random.choice(critical_keywords)} detected"
            elif base_priority == AlertPriority.HIGH:
                description += f" - {random.choice(high_keywords)} activity"
            else:
                description += f" - {random.choice(medium_keywords)} pattern"

        # Generate severity score
        if base_priority == AlertPriority.CRITICAL:
            severity_score = random.uniform(7.5, 10.0)
        elif base_priority == AlertPriority.HIGH:
            severity_score = random.uniform(5.0, 7.5)
        elif base_priority == AlertPriority.MEDIUM:
            severity_score = random.uniform(3.0, 5.0)
        else:
            severity_score = random.uniform(0.0, 3.0)

        # Generate frequency counts (higher for critical events)
        if base_priority == AlertPriority.CRITICAL:
            source_ip_count = random.randint(1, 20)
            destination_ip_count = random.randint(1, 15)
            user_count = random.randint(1, 10)
        elif base_priority == AlertPriority.HIGH:
            source_ip_count = random.randint(1, 10)
            destination_ip_count = random.randint(1, 8)
            user_count = random.randint(1, 5)
        else:
            source_ip_count = random.randint(1, 5)
            destination_ip_count = random.randint(1, 3)
            user_count = random.randint(1, 3)

        training_data.append(
            {
                "event_type": event_type.value,
                "source": random.choice(list(EventSource)).value,
                "description": description,
                "severity_score": severity_score,
                "source_ip_count": source_ip_count,
                "destination_ip_count": destination_ip_count,
                "user_count": user_count,
                "priority": base_priority.value,
                "timestamp": (
                    datetime.utcnow() - timedelta(hours=random.randint(0, 24))
                ).isoformat(),
            }
        )

    return training_data


if __name__ == "__main__":
    print("Generating training data...")
    data = generate_training_data(200)
    print(f"Generated {len(data)} training samples")

    # Save to file
    import json

    with open("training_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Training data saved to training_data.json")

    # Train the model
    from alerts.prioritizer import AlertPrioritizer

    print("\nTraining ML model...")
    prioritizer = AlertPrioritizer()
    prioritizer.train(data)
    print("Model training complete!")
