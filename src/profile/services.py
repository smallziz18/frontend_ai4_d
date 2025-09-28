from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from collections.abc import MutableMapping  # Import correct depuis Python 3.10+
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from src.db.mongo_db import mongo_db
from src.profile.mongo_models import ProfilMongoDB
from src.profile.schema import ProfilCreate, ProfilUpdate


# Reste du code...



class ProfileService:
    """Service pour gérer les profils utilisateurs dans MongoDB"""

    def __init__(self):
        self.collection: Collection = mongo_db.profils
        # Créer un index unique sur utilisateur_id
        self.collection.create_index("utilisateur_id", unique=True)

    async def create_profile(self, profile_data: ProfilCreate) -> ProfilMongoDB:
        """Créer un nouveau profil utilisateur"""

        # Vérifier si le profil existe déjà
        existing = await self.get_profile_by_user_id(profile_data.utilisateur_id)
        if existing:
            raise ValueError(f"Profile already exists for user {profile_data.utilisateur_id}")

        profil_dict = profile_data.model_dump()
        profil_dict["created_at"] = datetime.now()
        profil_dict["updated_at"] = datetime.now()
        profil_dict["utilisateur_id"] = str(profil_dict["utilisateur_id"])

        try:
            result = self.collection.insert_one(profil_dict)
            created_profil = self.collection.find_one({"_id": result.inserted_id})
            return ProfilMongoDB(**created_profil)
        except DuplicateKeyError:
            raise ValueError(f"Profile already exists for user {profile_data.utilisateur_id}")

    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[ProfilMongoDB]:
        """Récupérer le profil d'un utilisateur par son ID"""
        profil_data = self.collection.find_one({"utilisateur_id": str(user_id)})
        if profil_data:
            return ProfilMongoDB(**profil_data)
        return None

    async def get_profile_by_id(self, profile_id: str) -> Optional[ProfilMongoDB]:
        """Récupérer un profil par son ID MongoDB"""
        if not ObjectId.is_valid(profile_id):
            return None

        profil_data = self.collection.find_one({"_id": ObjectId(profile_id)})
        if profil_data:
            return ProfilMongoDB(**profil_data)
        return None

    async def update_profile(self, user_id: UUID, update_data: ProfilUpdate) -> Optional[ProfilMongoDB]:
        """Mettre à jour le profil d'un utilisateur"""
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        update_dict["updated_at"] = datetime.now()

        result = self.collection.find_one_and_update(
            {"utilisateur_id": str(user_id)},
            {"$set": update_dict},
            return_document=True
        )

        if result:
            return ProfilMongoDB(**result)
        return None

    async def delete_profile(self, user_id: UUID) -> bool:
        """Supprimer le profil d'un utilisateur"""
        result = self.collection.delete_one({"utilisateur_id": str(user_id)})
        return result.deleted_count > 0

    async def add_xp(self, user_id: UUID, xp_points: int) -> Optional[ProfilMongoDB]:
        """Ajouter des points d'expérience et gérer les montées de niveau"""
        result = self.collection.find_one_and_update(
            {"utilisateur_id": str(user_id)},
            {
                "$inc": {"xp": xp_points},
                "$set": {"updated_at": datetime.now()}
            },
            return_document=True
        )

        if result:
            profil = ProfilMongoDB(**result)
            await self._check_level_up(profil)
            # Récupérer le profil mis à jour
            updated_profil = self.collection.find_one({"_id": profil.id})
            return ProfilMongoDB(**updated_profil) if updated_profil else profil
        return None

    async def add_badge(self, user_id: UUID, badge: str) -> Optional[ProfilMongoDB]:
        """Ajouter un badge au profil"""
        result = self.collection.find_one_and_update(
            {"utilisateur_id": str(user_id)},
            {
                "$addToSet": {"badges": badge},
                "$set": {"updated_at": datetime.now()}
            },
            return_document=True
        )

        if result:
            return ProfilMongoDB(**result)
        return None

    async def add_competence(self, user_id: UUID, competence: str) -> Optional[ProfilMongoDB]:
        """Ajouter une compétence au profil"""
        result = self.collection.find_one_and_update(
            {"utilisateur_id": str(user_id)},
            {
                "$addToSet": {"competences": competence},
                "$set": {"updated_at": datetime.now()}
            },
            return_document=True
        )

        if result:
            return ProfilMongoDB(**result)
        return None

    async def log_activity(self, user_id: UUID, activity_type: str, details: Dict[str, Any]) -> Optional[ProfilMongoDB]:
        """Enregistrer une activité dans l'historique"""
        activity = {
            "type": activity_type,
            "details": details,
            "timestamp": datetime.now()
        }

        result = self.collection.find_one_and_update(
            {"utilisateur_id": str(user_id)},
            {
                "$push": {"historique_activites": activity},
                "$set": {"updated_at": datetime.now()}
            },
            return_document=True
        )

        if result:
            return ProfilMongoDB(**result)
        return None

    async def update_preferences(self, user_id: UUID, preferences: Dict[str, Any]) -> Optional[ProfilMongoDB]:
        """Mettre à jour les préférences utilisateur"""
        result = self.collection.find_one_and_update(
            {"utilisateur_id": str(user_id)},
            {
                "$set": {
                    "preferences": preferences,
                    "updated_at": datetime.now()
                }
            },
            return_document=True
        )

        if result:
            return ProfilMongoDB(**result)
        return None

    async def get_profile_stats(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Obtenir les statistiques du profil"""
        profil = await self.get_profile_by_user_id(user_id)
        if not profil:
            return None

        return {
            "niveau": profil.niveau,
            "xp": profil.xp,
            "xp_pour_niveau_suivant": (profil.niveau * 1000) - profil.xp,
            "nombre_badges": len(profil.badges),
            "nombre_competences": len(profil.competences),
            "nombre_activites": len(profil.historique_activites),
            "energie": profil.energie
        }

    async def complete_activity(self, user_id: UUID, activity_type: str, xp_reward: int = 0) -> Optional[ProfilMongoDB]:
        """Enregistrer une activité et donner de l'XP"""
        activity_details = {
            "xp_earned": xp_reward,
            "completed_at": datetime.now()
        }

        profile = await self.log_activity(user_id, activity_type, activity_details)

        if xp_reward > 0 and profile:
            profile = await self.add_xp(user_id, xp_reward)

        return profile

    async def unlock_achievement(self, user_id: UUID, achievement: str, badge: str = None) -> Optional[ProfilMongoDB]:
        """Débloquer un succès et optionnellement un badge"""
        await self.log_activity(user_id, "achievement_unlocked", {"achievement": achievement})

        if badge:
            return await self.add_badge(user_id, badge)

        return await self.get_profile_by_user_id(user_id)

    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtenir le classement des utilisateurs par XP"""
        cursor = self.collection.find({}).sort("xp", -1).limit(limit)

        leaderboard = []
        for i, profil_data in enumerate(cursor, 1):
            profil = ProfilMongoDB(**profil_data)
            leaderboard.append({
                "rank": i,
                "utilisateur_id": profil.utilisateur_id,
                "niveau": profil.niveau,
                "xp": profil.xp,
                "badges_count": len(profil.badges)
            })

        return leaderboard

    async def _check_level_up(self, profil: ProfilMongoDB) -> None:
        """Vérifier et mettre à jour le niveau basé sur l'XP"""
        nouveau_niveau = profil.xp // 1000 + 1

        if nouveau_niveau > profil.niveau:
            self.collection.update_one(
                {"_id": profil.id},
                {
                    "$set": {
                        "niveau": nouveau_niveau,
                        "updated_at": datetime.now()
                    }
                }
            )


# Instance globale du service
profile_service = ProfileService()