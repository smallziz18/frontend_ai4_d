import os

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
    REDIS_URL: str = 'redis://localhost:6379/0'


    # MongoDB
    MONGO_ROOT_USERNAME: str
    MONGO_ROOT_PASSWORD: str
    MONGO_APP_USERNAME: str
    MONGO_APP_PASSWORD: str
    MONGO_DATABASE: str
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    DOMAIN: str

    # Mail config - CORRIGÉ
    MAIL_USERNAME: str = "abdoulazizdiouf221@gmail.com"
    MAIL_PASSWORD: str = "sflb oazi vmwv wojr"
    MAIL_FROM: str = "abdoulazizdiouf221@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "AI4DB Support"  # Pas None
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    OPENAI_API_KEY: str



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
    def model_post_init(self, __context):
        """Injecte OPENAI_API_KEY dans l'environnement après initialisation"""
        os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY


Config = Settings()

broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
