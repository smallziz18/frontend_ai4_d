import json
import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.config import Config
import redis.asyncio as redis

logger = logging.getLogger("redis_profile")
logger.setLevel(logging.INFO)

# Redis client (même configuration que votre redis principal)
r = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB, decode_responses=True)


def serialize(obj):
    """Transforme UUID et datetime en string pour JSON."""
    if isinstance(obj, (UUID, datetime)):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


# TTL par défaut (en secondes)
DEFAULT_PROFILE_TTL = 3600  # 1 heure
DEFAULT_LEADERBOARD_TTL = 300  # 5 minutes
DEFAULT_STATS_TTL = 1800  # 30 minutes


# --- Single profile ---
async def get_profile_cache(user_id: UUID) -> Optional[dict]:
    """Récupère un profil depuis le cache Redis"""
    try:
        data = await r.get(f"profile:{user_id}")
        if data:
            logger.debug(f"Profile cache hit for user {user_id}")
            return json.loads(data)
        logger.debug(f"Profile cache miss for user {user_id}")
    except Exception as e:
        logger.warning(f"Redis get_profile_cache failed for user {user_id}: {e}")
    return None


async def set_profile_cache(user_id: UUID, profile_data: dict, expire: int = DEFAULT_PROFILE_TTL):
    """Met en cache un profil individuel"""
    try:
        await r.set(
            f"profile:{user_id}",
            json.dumps(profile_data, default=serialize),
            ex=expire
        )
        logger.debug(f"Profile cached for user {user_id}")
    except Exception as e:
        logger.warning(f"Redis set_profile_cache failed for user {user_id}: {e}")


async def invalidate_profile_cache(user_id: UUID):
    """Supprime le cache d'un profil spécifique"""
    try:
        await r.delete(f"profile:{user_id}")
        logger.debug(f"Profile cache invalidated for user {user_id}")
    except Exception as e:
        logger.warning(f"Redis invalidate_profile_cache failed for user {user_id}: {e}")


# --- Profile stats ---
async def get_profile_stats_cache(user_id: UUID) -> Optional[dict]:
    """Récupère les stats d'un profil depuis le cache"""
    try:
        data = await r.get(f"profile:stats:{user_id}")
        if data:
            logger.debug(f"Profile stats cache hit for user {user_id}")
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Redis get_profile_stats_cache failed for user {user_id}: {e}")
    return None


async def set_profile_stats_cache(user_id: UUID, stats_data: dict, expire: int = DEFAULT_STATS_TTL):
    """Met en cache les stats d'un profil"""
    try:
        await r.set(
            f"profile:stats:{user_id}",
            json.dumps(stats_data, default=serialize),
            ex=expire
        )
        logger.debug(f"Profile stats cached for user {user_id}")
    except Exception as e:
        logger.warning(f"Redis set_profile_stats_cache failed for user {user_id}: {e}")


async def invalidate_profile_stats_cache(user_id: UUID):
    """Supprime le cache des stats d'un profil"""
    try:
        await r.delete(f"profile:stats:{user_id}")
        logger.debug(f"Profile stats cache invalidated for user {user_id}")
    except Exception as e:
        logger.warning(f"Redis invalidate_profile_stats_cache failed for user {user_id}: {e}")


# --- Leaderboard ---
async def get_leaderboard_cache() -> Optional[List[dict]]:
    """Récupère le leaderboard depuis le cache"""
    try:
        data = await r.get("leaderboard:xp")
        if data:
            logger.debug("Leaderboard cache hit")
            return json.loads(data)
        logger.debug("Leaderboard cache miss")
    except Exception as e:
        logger.warning(f"Redis get_leaderboard_cache failed: {e}")
    return None


async def set_leaderboard_cache(leaderboard_data: List[dict], expire: int = DEFAULT_LEADERBOARD_TTL):
    """Met en cache le leaderboard"""
    try:
        await r.set(
            "leaderboard:xp",
            json.dumps(leaderboard_data, default=serialize),
            ex=expire
        )
        logger.debug("Leaderboard cached")
    except Exception as e:
        logger.warning(f"Redis set_leaderboard_cache failed: {e}")


async def invalidate_leaderboard_cache():
    """Supprime le cache du leaderboard"""
    try:
        await r.delete("leaderboard:xp")
        logger.debug("Leaderboard cache invalidated")
    except Exception as e:
        logger.warning(f"Redis invalidate_leaderboard_cache failed: {e}")


# --- Activity history ---
async def get_activities_cache(user_id: UUID) -> Optional[List[dict]]:
    """Récupère l'historique des activités depuis le cache"""
    try:
        data = await r.get(f"activities:{user_id}")
        if data:
            logger.debug(f"Activities cache hit for user {user_id}")
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Redis get_activities_cache failed for user {user_id}: {e}")
    return None


async def set_activities_cache(user_id: UUID, activities_data: List[dict], expire: int = 7200):  # 2h
    """Met en cache l'historique des activités"""
    try:
        await r.set(
            f"activities:{user_id}",
            json.dumps(activities_data, default=serialize),
            ex=expire
        )
        logger.debug(f"Activities cached for user {user_id}")
    except Exception as e:
        logger.warning(f"Redis set_activities_cache failed for user {user_id}: {e}")


async def invalidate_activities_cache(user_id: UUID):
    """Supprime le cache des activités d'un utilisateur"""
    try:
        await r.delete(f"activities:{user_id}")
        logger.debug(f"Activities cache invalidated for user {user_id}")
    except Exception as e:
        logger.warning(f"Redis invalidate_activities_cache failed for user {user_id}: {e}")


# --- Bulk invalidation ---
async def invalidate_all_profile_caches():
    """Supprime tous les caches liés aux profils (utile pour maintenance)"""
    try:
        # Pattern matching pour supprimer tous les profils
        keys_to_delete = []

        # Récupérer toutes les clés de profils
        profile_keys = await r.keys("profile:*")
        stats_keys = await r.keys("profile:stats:*")
        activities_keys = await r.keys("activities:*")
        leaderboard_keys = await r.keys("leaderboard:*")

        keys_to_delete.extend(profile_keys)
        keys_to_delete.extend(stats_keys)
        keys_to_delete.extend(activities_keys)
        keys_to_delete.extend(leaderboard_keys)

        if keys_to_delete:
            await r.delete(*keys_to_delete)
            logger.info(f"Invalidated {len(keys_to_delete)} profile-related cache keys")

    except Exception as e:
        logger.warning(f"Redis invalidate_all_profile_caches failed: {e}")


# --- Helper functions ---
async def invalidate_user_related_caches(user_id: UUID):
    """Invalide tous les caches liés à un utilisateur spécifique"""
    try:
        await invalidate_profile_cache(user_id)
        await invalidate_profile_stats_cache(user_id)
        await invalidate_activities_cache(user_id)
        # Le leaderboard doit aussi être invalidé car l'utilisateur peut avoir changé de position
        await invalidate_leaderboard_cache()

        logger.debug(f"All caches invalidated for user {user_id}")

    except Exception as e:
        logger.warning(f"Error invalidating user related caches for {user_id}: {e}")


async def get_cache_info() -> dict[str, int] | dict[str, str]:
    """Récupère des informations sur l'état du cache (pour monitoring)"""
    try:
        info = {
            "profiles": len(await r.keys("profile:*")),
            "stats": len(await r.keys("profile:stats:*")),
            "activities": len(await r.keys("activities:*")),
            "leaderboard": len(await r.keys("leaderboard:*")),
        }
        return info
    except Exception as e:
        logger.warning(f"Error getting cache info: {e}")
        return {"error": str(e)}