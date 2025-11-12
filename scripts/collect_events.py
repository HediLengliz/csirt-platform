"""Script to manually trigger event collection."""

from pipeline.tasks import collect_events_from_sources

if __name__ == "__main__":
    result = collect_events_from_sources()
    print(f"Event collection result: {result}")
