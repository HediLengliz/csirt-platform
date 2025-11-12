"""Script to help setup .env file."""

import os
import secrets
from pathlib import Path


def generate_secret_key():
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(32)


def setup_env_file():
    """Create or update .env file."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_example.exists():
        print("Error: .env.example file not found!")
        return False

    # Read example
    with open(env_example, "r") as f:
        content = f.read()

    # Generate secret keys if not set
    if "your-secret-key-here" in content:
        secret_key = generate_secret_key()
        jwt_secret_key = generate_secret_key()
        content = content.replace(
            "your-secret-key-here-change-in-production-use-secrets-token-urlsafe-32",
            secret_key,
        )
        content = content.replace(
            "your-jwt-secret-key-here-change-in-production-use-secrets-token-urlsafe-32",
            jwt_secret_key,
        )
        print("Generated new secret keys")

    # Write .env file
    with open(env_file, "w") as f:
        f.write(content)

    print(f"✓ Created/updated .env file")
    return True


if __name__ == "__main__":
    setup_env_file()
