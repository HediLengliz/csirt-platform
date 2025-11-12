"""Initialize database with tables."""

from config.database import Base, engine
from models import *  # Import all models
from utils.logger import logger


def init_database():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    init_database()
