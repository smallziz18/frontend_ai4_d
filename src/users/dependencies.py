from operator import truediv
from typing import List, Any

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.sql.functions import user
from .models import Utilisateur

from src.users.utils import decode_token
from src.db.redis import is_token_in_block_list
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .services import UserService

users_service = UserService()

class AccessToken(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        # Récupérer le token
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials

        # Décoder le token (decode_token lève HTTPException si invalide ou expiré)
        token_data = decode_token(token)

        # Vérifier si le token est dans la blacklist Redis
        if await is_token_in_block_list(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "token invalid or revoked",
                    "hint": "get new token",
                }
            )

        # Vérifier le type de token (accès ou refresh)
        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        """À surcharger dans les sous-classes."""
        raise NotImplementedError("Please implement this method.")


class AccessTokenBearer(AccessToken):
    def verify_token_data(self, token_data: dict) -> None:
        # Si c'est un refresh token, on bloque
        if token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token"
            )


class RefreshTokenBearer(AccessToken):
    def verify_token_data(self, token_data: dict) -> None:
        # Si ce n'est pas un refresh token, on bloque
        if not token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token"
            )

async def get_current_use(session: AsyncSession = Depends(get_session),token_details: dict = Depends(AccessTokenBearer(),)):
    user_email = token_details["user"]["email"]
    user = await users_service.get_user_by_email(user_email, session=session)
    return user


class RoleChecker:
    def __init__(self,allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self,current_user: Utilisateur = Depends(get_current_use)) -> Any:
        if current_user.status in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this resource"
        )



