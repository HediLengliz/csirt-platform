"""Setup script for CSIRT Platform."""
import os
import secrets
import subprocess
import sys
from pathlib import Path


def generate_secret_key():
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(32)


def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return
    
    if not env_example.exists():
        print("✗ .env.example file not found!")
        return
    
    # Read example file
    with open(env_example, "r") as f:
        content = f.read()
    
    # Replace placeholder secret keys
    secret_key = generate_secret_key()
    jwt_secret_key = generate_secret_key()
    
    content = content.replace("your-secret-key-here-change-in-production-use-secrets-token-urlsafe-32", secret_key)
    content = content.replace("your-jwt-secret-key-here-change-in-production-use-secrets-token-urlsafe-32", jwt_secret_key)
    
    # Write .env file
    with open(env_file, "w") as f:
        f.write(content)
    
    print("✓ Created .env file with generated secret keys")
    print(f"  SECRET_KEY: {secret_key[:20]}...")
    print(f"  JWT_SECRET_KEY: {jwt_secret_key[:20]}...")


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\nChecking dependencies...")
    
    try:
        import fastapi
        import sqlalchemy
        import celery
        import redis
        print("✓ Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Run: pip install -r requirements.txt")
        return False


def check_database_connection():
    """Check if database is accessible."""
    print("\nChecking database connection...")
    
    try:
        from config.settings import settings
        from sqlalchemy import create_engine, text
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("  Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False


def check_redis_connection():
    """Check if Redis is accessible."""
    print("\nChecking Redis connection...")
    
    try:
        import redis
        from config.settings import settings
        
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("✓ Redis connection successful")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        print("  Make sure Redis is running and REDIS_URL is correct")
        return False


def init_database():
    """Initialize database tables."""
    print("\nInitializing database...")
    
    try:
        from config.database import engine
        from models.base import Base
        # Import all models to register them
        from models.event import Event
        from models.alert import Alert
        from models.incident import Incident
        from models.integration import Integration
        
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("CSIRT Platform Setup")
    print("=" * 60)
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database
    db_ok = check_database_connection()
    
    # Check Redis
    redis_ok = check_redis_connection()
    
    # Initialize database if connection is ok
    if db_ok:
        init_database()
    
    print("\n" + "=" * 60)
    print("Setup Summary")
    print("=" * 60)
    print(f"Database: {'✓ OK' if db_ok else '✗ FAILED'}")
    print(f"Redis: {'✓ OK' if redis_ok else '✗ FAILED'}")
    print("\nNext steps:")
    print("1. Review and update .env file with your configurations")
    print("2. Start the application:")
    print("   - With Docker: docker-compose up -d")
    print("   - Manually: python main.py")
    print("3. Access the API at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()

