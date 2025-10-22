import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


@dataclass
class Config:
    """Configuration settings loaded from environment variables with sensible defaults."""
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "network_devices")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION", "devices")

    # Ping settings
    PING_ENABLED: bool = os.getenv("PING_ENABLED", "true").lower() in ("1", "true", "yes", "y")
    PING_INTERVAL_SECONDS: int = int(os.getenv("PING_INTERVAL_SECONDS", "300"))
    PING_TIMEOUT_MS: int = int(os.getenv("PING_TIMEOUT_MS", "1000"))

    # App/server settings
    APP_PORT: int = int(os.getenv("APP_PORT", "5000"))

    # Flask settings
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes", "y")
    ENV: str = os.getenv("FLASK_ENV", "production")


# PUBLIC_INTERFACE
def get_config() -> Config:
    """Return a Config instance populated from environment variables."""
    return Config()
