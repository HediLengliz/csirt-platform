"""Real-time incident processing pipeline."""

from pipeline.correlator import EventCorrelator
from pipeline.processor import EventProcessor

__all__ = [
    "EventProcessor",
    "EventCorrelator",
]
