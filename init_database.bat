@echo off
REM Initialize database tables in Docker container

echo Initializing database tables...
docker-compose exec -T api python -c "from config.database import engine; from models.base import Base; from models.event import Event; from models.alert import Alert; from models.incident import Incident; from models.integration import Integration; Base.metadata.create_all(bind=engine); print('Database tables created successfully!')"

