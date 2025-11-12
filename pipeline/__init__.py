"""Real-time incident processing pipeline."""
from pipeline.processor import EventProcessor
from pipeline.correlator import EventCorrelator

__all__ = [
    "EventProcessor",
    "EventCorrelator",
]

