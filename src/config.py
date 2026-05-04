from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Application settings loaded from the environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    ) 

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # API Keys
    openai_api_key: str | None = Field(
        default=None,
        alias="OPENAI_API_KEY",
        description="API key for OpenAI integration",
    )

    redis_server: str = Field(default="localhost", description="Redis server address")
    
    redis_port: int = Field(default=6379, description="Redis server port")


settings = Settings()