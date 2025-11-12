"""Create .env file with generated secret keys."""

import secrets

# Generate secret keys
secret_key = secrets.token_urlsafe(32)
jwt_secret_key = secrets.token_urlsafe(32)

# .env file content
env_content = f"""# Application Configuration
APP_NAME=CSIRT Platform
DEBUG=true
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Security Keys (Generated)
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret_key}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database Configuration
# For Docker Compose (default)
DATABASE_URL=postgresql://csirt_user:csirt_password@localhost:5432/csirt_db
# For local PostgreSQL, uncomment and modify:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/csirt_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# SIEM - Splunk (Optional - configure if you have Splunk)
SPLUNK_HOST=localhost
SPLUNK_PORT=8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=changeme
SPLUNK_VERIFY_SSL=false

# SIEM - Elastic Security (Optional - configure if you have Elastic)
ELASTIC_HOST=localhost
ELASTIC_PORT=9200
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=changeme
ELASTIC_VERIFY_SSL=false

# SOAR - TheHive (Optional - configure if you have TheHive)
THEHIVE_URL=http://localhost:9000
THEHIVE_API_KEY=changeme

# SOAR - Cortex (Optional - configure if you have Cortex)
CORTEX_URL=http://localhost:9001
CORTEX_API_KEY=changeme

# SOAR - Phantom (Optional - configure if you have Phantom)
PHANTOM_URL=http://localhost:8080
PHANTOM_USERNAME=admin
PHANTOM_PASSWORD=changeme
PHANTOM_VERIFY_SSL=false

# ML Model Configuration
ML_MODEL_PATH=./models/alert_prioritizer.pkl
ML_RETRAIN_INTERVAL_HOURS=24
"""

# Write .env file
with open(".env", "w") as f:
    f.write(env_content)

print("SUCCESS: .env file created with generated secret keys!")
print(f"SECRET_KEY: {secret_key[:20]}...")
print(f"JWT_SECRET_KEY: {jwt_secret_key[:20]}...")
print("\nNext steps:")
print("1. Review .env file and update database/redis URLs if needed")
print("2. Choose your setup method:")
print("   - Docker Compose: docker-compose up -d")
print("   - Local: Follow START_HERE.md")
print("3. Access API at: http://localhost:8000/docs")
