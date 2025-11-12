"""Configuration settings for CSIRT Platform."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "CSIRT Platform"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # SIEM - Splunk
    SPLUNK_HOST: Optional[str] = None
    SPLUNK_PORT: int = 8089
    SPLUNK_USERNAME: Optional[str] = None
    SPLUNK_PASSWORD: Optional[str] = None
    SPLUNK_VERIFY_SSL: bool = False

    # SIEM - Elastic
    ELASTIC_HOST: Optional[str] = None
    ELASTIC_PORT: int = 9200
    ELASTIC_USERNAME: Optional[str] = None
    ELASTIC_PASSWORD: Optional[str] = None
    ELASTIC_VERIFY_SSL: bool = False

    # SOAR - TheHive
    THEHIVE_URL: Optional[str] = None
    THEHIVE_API_KEY: Optional[str] = None

    # SOAR - Cortex
    CORTEX_URL: Optional[str] = None
    CORTEX_API_KEY: Optional[str] = None

    # SOAR - Phantom
    PHANTOM_URL: Optional[str] = None
    PHANTOM_USERNAME: Optional[str] = None
    PHANTOM_PASSWORD: Optional[str] = None
    PHANTOM_VERIFY_SSL: bool = False

    # ML
    ML_MODEL_PATH: str = "./models/alert_prioritizer.pkl"
    ML_RETRAIN_INTERVAL_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
