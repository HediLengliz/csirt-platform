"""Script to train the ML model for alert prioritization."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

from alerts.prioritizer import AlertPrioritizer
from alerts.tasks import _get_event_context
from config.database import SessionLocal
from models.alert import Alert
from models.event import Event


def train_model():
    """Train the ML model using existing alerts or generate synthetic data."""
    db = SessionLocal()
    prioritizer = AlertPrioritizer()

    try:
        # Try to get training data from existing alerts
        alerts = db.query(Alert).filter(Alert.ml_score.isnot(None)).limit(1000).all()
        events = db.query(Event).limit(500).all()

        training_data = []

        # Use existing alerts if available
        if alerts and len(alerts) > 10:
            print(f"Using {len(alerts)} existing alerts for training...")
            for alert in alerts:
                if alert.event_id:
                    event = db.query(Event).filter(Event.id == alert.event_id).first()
                    if event:
                        context = _get_event_context(db, event)
                        training_data.append(
                            {
                                "event_type": event.event_type.value,
                                "source": event.source.value,
                                "description": event.description or "",
                                "severity_score": (
                                    float(event.severity_score)
                                    if event.severity_score
                                    else 0.0
                                ),
                                "source_ip_count": context.get("source_ip_count", 1),
                                "destination_ip_count": context.get(
                                    "destination_ip_count", 1
                                ),
                                "user_count": context.get("user_count", 1),
                                "priority": alert.priority.value,
                            }
                        )
        else:
            # Generate synthetic training data
            print("Generating synthetic training data...")
            from scripts.generate_training_data import generate_training_data

            training_data = generate_training_data(200)

        if len(training_data) < 10:
            print("Not enough training data. Generating more...")
            from scripts.generate_training_data import generate_training_data

            training_data.extend(generate_training_data(100))

        print(f"Training model with {len(training_data)} samples...")
        prioritizer.train(training_data)
        print("Model training complete!")

    except Exception as e:
        print(f"Error training model: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    train_model()
