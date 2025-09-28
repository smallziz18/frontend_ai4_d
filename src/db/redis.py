import redis.asyncio as redis
import json
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.users.schema import UtilisateurRead
import logging
from src.config import Config

logger = logging.getLogger("redis_cache")
logger.setLevel(logging.INFO)

JTI_EXPIRY = 3600

# Redis client
r = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB, decode_responses=True)

def serialize(obj):
    """Transforme UUID et datetime en string pour JSON."""
    if isinstance(obj, (UUID, datetime)):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# --- Single user ---
async def get_user_cache(user_id: UUID) -> Optional[dict]:
    try:
        data = await r.get(f"user:{user_id}")
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Redis get_user_cache failed: {e}")
    return None

async def set_user_cache(user: UtilisateurRead, expire: int = 300):
    """Met en cache un utilisateur individuel (expire en secondes)."""
    try:
        await r.set(
            f"user:{user.id}",
            json.dumps(user.model_dump(), default=serialize),
            ex=expire
        )
    except Exception as e:
        logger.warning(f"Redis set_user_cache failed: {e}")

# --- All users ---
async def get_all_users_cache() -> Optional[List[dict]]:
    try:
        data = await r.get("users:all")
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Redis get_all_users_cache failed: {e}")
    return None

async def set_all_users_cache(users: List[UtilisateurRead], expire: int = 300):
    """Met en cache la liste de tous les utilisateurs."""
    try:
        users_dict = [u.model_dump() for u in users]
        await r.set(
            "users:all",
            json.dumps(users_dict, default=serialize),
            ex=expire
        )
    except Exception as e:
        logger.warning(f"Redis set_all_users_cache failed: {e}")

# --- Invalidate cache ---
async def invalidate_user_cache(user_id: Optional[UUID] = None):
    """Supprime le cache d’un utilisateur ou de tous les utilisateurs."""
    try:
        if user_id:
            await r.delete(f"user:{user_id}")
        else:
            await r.delete("users:all")
    except Exception as e:
        logger.warning(f"Redis invalidate_user_cache failed: {e}")
async def invalidate_all_users_cache():
    """Supprime le cache de tous les utilisateurs."""
    try:
        await r.delete("users:all")
    except Exception as e:
        logger.warning(f"Redis invalidate_all_users_cache failed: {e}")


async def add_jti_to_redis_block_list(jti:str)->None:
    await r.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY
    )

async def is_token_in_block_list(jti: str) -> bool:
    value = await r.get(jti)
    return value is not None
