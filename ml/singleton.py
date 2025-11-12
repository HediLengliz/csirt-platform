"""Singleton instance for RealTimeMLSystem to share state across the application."""
from ml.detector import RealTimeMLSystem

# Global singleton instance
_ml_system_instance = None

def get_ml_system() -> RealTimeMLSystem:
    """Get or create the singleton ML system instance."""
    global _ml_system_instance
    if _ml_system_instance is None:
        _ml_system_instance = RealTimeMLSystem()
    return _ml_system_instance

def reset_ml_system():
    """Reset the ML system instance (for testing)."""
    global _ml_system_instance
    _ml_system_instance = None

