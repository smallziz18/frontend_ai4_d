from pathlib import Path
import os
from fastapi_mail import FastMail, ConnectionConfig,MessageSchema,MessageType
from pydantic import EmailStr

from src.config import Config

# Chemin du dossier courant
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"


os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Configuration FastMail
mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_SSL_TLS=Config.MAIL_SSL_TLS,
    MAIL_STARTTLS=Config.MAIL_STARTTLS,
    USE_CREDENTIALS=Config.USE_CREDENTIALS,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    VALIDATE_CERTS=Config.VALIDATE_CERTS,
    TEMPLATE_FOLDER=TEMPLATE_DIR,
)

# Initialisation FastMail
mail = FastMail(config=mail_config)


def create_message(recipients, subject:str, body:str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=MessageType.html,
    )
    return message

