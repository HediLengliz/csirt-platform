"""Populate ML event window with recent events."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alerts.tasks import _get_event_context
from config.database import SessionLocal
from ml.singleton import get_ml_system
from models.event import Event


def populate_ml_window():
    """Populate ML event window with recent events."""
    db = SessionLocal()
    ml_system = get_ml_system()

    try:
        print("Populating ML event window...")

        # Get recent events
        events = db.query(Event).order_by(Event.created_at.desc()).limit(100).all()
        print(f"Found {len(events)} events")

        # Process each event to add to window
        processed = 0
        for event in events:
            context = _get_event_context(db, event)
            ml_system.process_event(event, context)
            processed += 1
            if processed % 20 == 0:
                print(f"  Processed {processed}/{len(events)} events...")

        print(f"✅ Processed {processed} events")
        print(f"✅ Events in window: {len(ml_system.event_window)}")
        print()
        print("ML window is now populated!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    populate_ml_window()
