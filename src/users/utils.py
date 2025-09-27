import uuid
from typing import Any

from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from src.config import Config
import logging
ACCESS_TOKEN_EXPIRE= 3600
password_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def generate_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password_hash(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(data: dict, expires_delta: timedelta = None,refresh:bool =False) -> str:
    payload = {}
    payload["user"] = data
    payload["exp"] = datetime.now() + (expires_delta if  expires_delta is not None  else timedelta(ACCESS_TOKEN_EXPIRE))
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        raise e





