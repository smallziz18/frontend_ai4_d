import redis.asyncio as redis
import json
from typing import List
from uuid import UUID
from datetime import datetime
from src.users.schema import UtilisateurRead

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def serialize(obj):
    """Transforme UUID et datetime en string pour JSON."""
    if isinstance(obj, (UUID, datetime)):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# --- Single user ---
async def get_user_cache(user_id: UUID) -> dict | None:
    data = await r.get(f"user:{user_id}")
    if data:
        return json.loads(data)
    return None

async def set_user_cache(user: UtilisateurRead):
    await r.set(
        f"user:{user.id}",
        json.dumps(user.model_dump(), default=serialize),
        ex=300  # expire en 5 min
    )

# --- All users ---
async def get_all_users_cache() -> List[dict] | None:
    data = await r.get("users:all")
    if data:
        return json.loads(data)
    return None

async def set_all_users_cache(users: List[UtilisateurRead]):
    users_dict = [u.model_dump() for u in users]
    await r.set(
        "users:all",
        json.dumps(users_dict, default=serialize),
        ex=300
    )

async def invalidate_all_users_cache():
    """Supprime le cache de tous les utilisateurs."""
    await r.delete("users:all")
