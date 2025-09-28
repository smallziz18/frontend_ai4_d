import uuid

from fastapi import HTTPException,status
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import jwt
from src.config import Config
ACCESS_TOKEN_EXPIRE= 3600
password_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def generate_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password_hash(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(data: dict, expires_delta: timedelta = None, refresh: bool = False) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(ACCESS_TOKEN_EXPIRE))
    payload = {
        "user": data,
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "refresh": refresh
    }
    token = jwt.encode(payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                                    "error": "token invalid or revoked",
                                    "hint":"get new token",
                                })
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")






