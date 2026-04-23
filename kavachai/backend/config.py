"""KavachAI configuration — environment-specific settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "local"  # local | docker | cloud
    DATABASE_BACKEND: str = "sqlite"  # sqlite | mongodb
    DATABASE_URL: str = "sqlite:///data/kavachai.db"
    MONGODB_URI: str = ""  # mongodb+srv://user:pass@cluster.mongodb.net/kavachai
    MONGODB_DATABASE: str = "kavachai"
    REDIS_URL: str = "redis://localhost:6379"

    # LLM provider keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # KavachAI crypto keys
    KAVACHAI_PRIVATE_KEY_PATH: str = ""
    KAVACHAI_PUBLIC_KEY_PATH: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Defaults
    DEFAULT_TRUST_SCORE: float = 0.5
    ESCALATION_TIMEOUT_SECONDS: int = 60
    MIN_MODEL_SAFETY_SCORE: int = 70
    GROUNDING_THRESHOLD: float = 0.7
    MAX_ACTION_WINDOW: int = 50
    TRUST_DECAY_RATE: float = 0.01  # per hour of inactivity

    class Config:
        env_file = ".env"


settings = Settings()
