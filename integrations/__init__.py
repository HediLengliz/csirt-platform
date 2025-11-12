"""SIEM and SOAR integration adapters."""
from integrations.siem_splunk import SplunkIntegration
from integrations.siem_elastic import ElasticIntegration
from integrations.soar_thehive import TheHiveIntegration
from integrations.soar_cortex import CortexIntegration
from integrations.soar_phantom import PhantomIntegration

__all__ = [
    "SplunkIntegration",
    "ElasticIntegration",
    "TheHiveIntegration",
    "CortexIntegration",
    "PhantomIntegration",
]

