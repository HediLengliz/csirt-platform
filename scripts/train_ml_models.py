"""Script to train ML models using existing events."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alerts.tasks import _get_event_context
from config.database import SessionLocal
from ml.detector import RealTimeMLSystem
from models.event import Event


def train_ml_models():
    """Train ML models with existing events from database."""
    db = SessionLocal()
    ml_system = RealTimeMLSystem()

    try:
        print("=" * 70)
        print("Training ML Models")
        print("=" * 70)
        print()

        # Get events from database
        print("Fetching events from database...")
        events = db.query(Event).order_by(Event.created_at.desc()).limit(100).all()

        if len(events) < 10:
            print(
                f"⚠️  Only {len(events)} events found. Need at least 10 events for training."
            )
            print("Creating some test events first...")

            # Create test events if not enough
            from datetime import datetime

            from models.event import EventSource, EventType

            test_events = []
            for i in range(15):
                event = Event(
                    source=EventSource.CUSTOM,
                    event_type=(
                        EventType.SUSPICIOUS_ACTIVITY
                        if i % 3 == 0
                        else EventType.LOGIN_FAILURE
                    ),
                    description=f"Test event {i+1} for ML training",
                    severity_score=str(5.0 + (i % 5)),
                    source_ip=f"192.168.1.{100 + i}",
                    raw_data={},
                    timestamp=datetime.utcnow().isoformat(),
                )
                db.add(event)
                test_events.append(event)

            db.commit()
            for event in test_events:
                db.refresh(event)

            events.extend(test_events)
            print(f"✅ Created {len(test_events)} test events")
            print()

        print(f"Found {len(events)} events for training")
        print()

        # Get contexts for all events
        print("Preparing training data...")
        contexts = []
        for i, event in enumerate(events):
            context = _get_event_context(db, event)
            contexts.append(context)
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(events)} events...")

        print(f"✅ Prepared {len(contexts)} event contexts")
        print()

        # Train the models
        print("Training ML models...")
        print("  - Anomaly Detector: Training with Isolation Forest...")
        print("  - This may take a few moments...")
        print()

        ml_system.update_models(events, contexts)

        print()
        print("=" * 70)
        print("✅ ML Models Training Complete!")
        print("=" * 70)
        print()
        print("Model Status:")
        print(f"  - Anomaly Detector Trained: {ml_system.anomaly_detector.is_trained}")
        print(f"  - Events Used: {len(events)}")
        print(f"  - Patterns Loaded: {len(ml_system.classifier.patterns)}")
        print()
        print("The ML system is now ready for real-time detection!")
        print()

    except Exception as e:
        print(f"❌ Error training models: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    train_ml_models()
