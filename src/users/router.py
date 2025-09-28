from datetime import timedelta, datetime, timezone
from typing import Union, List
from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import JSONResponse
import logging

from src.db.main import get_session
from src.db.redis import (
    get_all_users_cache,
    set_all_users_cache,
    set_user_cache,
    invalidate_all_users_cache,
    add_jti_to_redis_block_list
)
from .models import StatutUtilisateur
from .utils import create_access_token
from src.users.schema import UtilisateurRead, ProfesseurCreate, EtudiantCreate, UserLogin
from src.users.services import UserService
from src.users.utils import verify_password_hash
from src.users.dependencies import AccessTokenBearer
from .dependencies import RefreshTokenBearer
from .dependencies import get_current_use,RoleChecker

# Logger
logger = logging.getLogger("user_router")
logger.setLevel(logging.INFO)
roles = [role.value for role in StatutUtilisateur]
role =["admin","user"]
role_checker = RoleChecker(role)

access_token = AccessTokenBearer()
refresh_token = RefreshTokenBearer()

user_router = APIRouter()
user_service = UserService()
REFRESH_TOKEN_EXPIRATION = 2  # en jours

# --- GET all users ---
@user_router.get("/", response_model=List[UtilisateurRead])
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token)
):
    try:
        cached = await get_all_users_cache()
        if cached:
            logger.info("Cache hit for all users")
            return [UtilisateurRead.model_validate(u) for u in cached]
    except Exception as e:
        logger.warning(f"Redis unavailable for all users cache: {e}")

    users_result = await user_service.get_all_users(session)
    users_data = [UtilisateurRead.model_validate(u, from_attributes=True) for u in users_result]

    try:
        await set_all_users_cache(users_data)
    except Exception as e:
        logger.warning(f"Redis unavailable, cannot cache all users: {e}")

    return users_data

# --- CREATE user ---
@user_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UtilisateurRead)
async def create_user(
    data: Union[ProfesseurCreate, EtudiantCreate],
    session: AsyncSession = Depends(get_session)
):
    user = await user_service.create_user(session, data)
    user_data = UtilisateurRead.model_validate(user, from_attributes=True)

    # Mettre à jour cache individuel
    try:
        await set_user_cache(user_data)
        await invalidate_all_users_cache()
    except Exception as e:
        logger.warning(f"Redis unavailable during user cache update: {e}")

    logger.info(f"User created: {user_data.id}")
    return user_data

# --- LOGIN user ---
@user_router.post("/login", response_model=UserLogin)
async def login_user(login: UserLogin, session: AsyncSession = Depends(get_session)):
    email = str(login.email)
    password = login.password
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="Invalid email")
    if not verify_password_hash(password, user.motDePasseHash):
        raise HTTPException(status_code=400, detail="Invalid password")

    payload = {
        'email': str(user.email),
        'id': str(user.id),
        'username': str(user.username),
        'status': str(user.status),
    }

    access_token_value = create_access_token(data=payload)
    refresh_token_value = create_access_token(
        data=payload,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRATION),
        refresh=True
    )

    logger.info(f"User logged in: {user.id}")
    return JSONResponse(
        content={
            "message": "Successfully logged in",
            "access_token": access_token_value,
            "refresh_token": refresh_token_value,
            "user": {
                "id": str(user.id),
                "username": str(user.username),
                "email": str(user.email),
            }
        }
    )

# --- REFRESH token ---
@user_router.get("/refresh_token")
async def get_new_access_token(token_detail: dict = Depends(RefreshTokenBearer())):
    if token_detail:
        expire_timestamp = token_detail['exp']
        now = datetime.now(timezone.utc).timestamp()
        if expire_timestamp > now:
            new_access_token = create_access_token(
                data={"user": token_detail["user"]}
            )
            logger.info(f"Access token refreshed for user: {token_detail['user']['id']}")
            return JSONResponse(content={"token": new_access_token})
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired refresh token")

@user_router.get("/me")
async def get_current_user(user_details: dict = Depends(get_current_use)):
    return user_details
@user_router.get("/logout")
async def logout(token_detail: dict = Depends(AccessTokenBearer())):
    jti = token_detail['jti']
    await add_jti_to_redis_block_list(jti)
    return JSONResponse(content={"message": "Successfully logged out"},
                        status_code=status.HTTP_200_OK
                        )

