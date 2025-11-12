"""Main application entry point."""
import uvicorn
from config.settings import settings
from config.database import engine
from models.base import Base
from models import *  # Import all models to register them
from utils.logger import logger

# Create database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

