from datetime import timedelta
from uuid import UUID
from typing import Union, List
from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.db.redis import (
    get_all_users_cache,
    set_all_users_cache,
    get_user_cache,
    set_user_cache,
    invalidate_all_users_cache
)
from .utils import create_access_token,decode_token
from src.users.schema import UtilisateurRead, ProfesseurCreate, EtudiantCreate, UserLogin
from src.users.services import UserService
from src.users.utils import verify_password_hash
from fastapi.responses import JSONResponse
from src.users.dependencies import  AccessToken
access_token = AccessToken()

user_router = APIRouter()
user_service = UserService()
REFRESH_TOKEN_EXPIRATION = 2

# --- GET all users ---
@user_router.get("/", response_model=List[UtilisateurRead])
async def get_all_users(session: AsyncSession = Depends(get_session),user_details=Depends(access_token)):
    cached = await get_all_users_cache()
    if cached:
        return [UtilisateurRead.model_validate(u) for u in cached]

    users_result = await user_service.get_all_users(session)
    users_data = [UtilisateurRead.model_validate(u, from_attributes=True) for u in users_result]

    await set_all_users_cache(users_data)
    return users_data

# --- GET single user ---


# --- CREATE user ---
@user_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UtilisateurRead)
async def create_user(
    data: Union[ProfesseurCreate, EtudiantCreate],
    session: AsyncSession = Depends(get_session)
):

    user = await user_service.create_user(session, data)
    user_data = UtilisateurRead.model_validate(user, from_attributes=True)

    # Mettre à jour cache individuel
    await set_user_cache(user_data)
    # Invalider le cache "all users"
    await invalidate_all_users_cache()

    return user_data


@user_router.post("/login", response_model=UserLogin)
async def login_user(login: UserLogin, session: AsyncSession = Depends(get_session)):
    email = str(login.email)
    password = login.password
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    password_valid = verify_password_hash(password, user.motDePasseHash)
    if not password_valid:
        raise HTTPException(status_code=400, detail="Incorrect password")
    access_token = create_access_token(
        data={
            'email': str(user.email),
            'id': str(user.id),
            'username': str(user.username),
            'status': str(user.statut),
        }

    )

    refresh_token = create_access_token(
        data={
            'email': str(user.email),
            'id': str(user.id),
            'username': str(user.username),
            'status': str(user.statut),
        },
        expires_delta=timedelta(days= REFRESH_TOKEN_EXPIRATION),
        refresh=True

    )
    return JSONResponse(
        content={
            "message": "Successfully logged in",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user":{
                "id": str(user.id),
                "username": str(user.username),
                "email": str(user.email),
            }
        }
    )

@user_router.get("/{user_id}", response_model=UtilisateurRead)
async def get_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    cached = await get_user_cache(user_id)
    if cached:
        return UtilisateurRead.model_validate(cached)

    user_result = await user_service.get_user(user_id, session)
    if not user_result:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = UtilisateurRead.model_validate(user_result, from_attributes=True)
    await set_user_cache(user_data)
    return user_data


