"""Detection modules for multi-source event collection."""
from detection.base import BaseDetector
from detection.splunk_detector import SplunkDetector
from detection.elastic_detector import ElasticDetector
from detection.endpoint_detector import EndpointDetector
from detection.network_detector import NetworkDetector

__all__ = [
    "BaseDetector",
    "SplunkDetector",
    "ElasticDetector",
    "EndpointDetector",
    "NetworkDetector",
]

