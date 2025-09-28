from pydantic_settings import BaseSettings,SettingsConfigDict
from pathlib import Path
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_HOST : str = 'localhost'
    REDIS_PORT : int = 6379
    REDIS_DB : str = 0

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        extra="ignore"
    )

Config = Settings()