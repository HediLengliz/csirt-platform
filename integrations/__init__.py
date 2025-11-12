"""SIEM and SOAR integration adapters."""

from integrations.siem_elastic import ElasticIntegration
from integrations.siem_splunk import SplunkIntegration
from integrations.soar_cortex import CortexIntegration
from integrations.soar_phantom import PhantomIntegration
from integrations.soar_thehive import TheHiveIntegration

__all__ = [
    "SplunkIntegration",
    "ElasticIntegration",
    "TheHiveIntegration",
    "CortexIntegration",
    "PhantomIntegration",
]
