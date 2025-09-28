from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # Redis
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # MongoDB
    MONGO_ROOT_USERNAME: str
    MONGO_ROOT_PASSWORD: str
    MONGO_APP_USERNAME: str
    MONGO_APP_PASSWORD: str
    MONGO_DATABASE: str
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017

    @property
    def MONGODB_URL(self) -> str:
        return f"mongodb://{self.MONGO_APP_USERNAME}:{self.MONGO_APP_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DATABASE}"

    @property
    def MONGODB_ADMIN_URL(self) -> str:
        return f"mongodb://{self.MONGO_ROOT_USERNAME}:{self.MONGO_ROOT_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DATABASE}"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        extra="ignore"
    )


Config = Settings()
