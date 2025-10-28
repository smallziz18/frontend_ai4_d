"""
Utilitaires de sécurité pour protéger les données utilisateur
"""
from uuid import UUID
from fastapi import HTTPException, status
from src.users.models import Utilisateur


def verify_user_access(
    current_user: Utilisateur,
    resource_user_id: UUID,
    resource_name: str = "ressource"
) -> None:
    """
    Vérifie qu'un utilisateur a le droit d'accéder à une ressource.

    Args:
        current_user: L'utilisateur connecté
        resource_user_id: L'UUID du propriétaire de la ressource
        resource_name: Nom de la ressource (pour le message d'erreur)

    Raises:
        HTTPException: 403 si l'utilisateur n'a pas accès
    """
    if current_user.id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Accès interdit : vous ne pouvez accéder qu'à votre propre {resource_name}"
        )


def verify_admin_access(current_user: Utilisateur) -> None:
    """
    Vérifie qu'un utilisateur est administrateur.

    Args:
        current_user: L'utilisateur connecté

    Raises:
        HTTPException: 403 si l'utilisateur n'est pas admin
    """
    if current_user.status != "Administrateur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit : droits administrateur requis"
        )


def sanitize_user_data(user_data: dict, is_owner: bool = False) -> dict:
    """
    Nettoie les données utilisateur pour éviter l'exposition d'informations sensibles.

    Args:
        user_data: Les données brutes de l'utilisateur
        is_owner: True si c'est l'utilisateur lui-même qui consulte

    Returns:
        dict: Données nettoyées
    """
    # Toujours retirer ces champs
    sensitive_fields = [
        "motDePasseHash",
        "password",
        "motdepasse",
        "hash",
    ]

    # Retirer aussi ces champs si ce n'est pas le propriétaire
    private_fields = [
        "email",
        "is_verified",
        "created_at",
        "updated_at",
    ] if not is_owner else []

    # Toujours masquer l'UUID complet (utiliser username à la place)
    uuid_fields = [
        "id",
        "utilisateur_id",
        "user_id",
    ] if not is_owner else []

    fields_to_remove = sensitive_fields + private_fields + uuid_fields

    cleaned = {
        k: v for k, v in user_data.items()
        if k not in fields_to_remove
    }

    return cleaned


def sanitize_profile_data(profile_data: dict, current_user_id: UUID, profile_user_id: UUID) -> dict:
    """
    Nettoie les données de profil selon qui y accède.

    Args:
        profile_data: Les données du profil
        current_user_id: UUID de l'utilisateur connecté
        profile_user_id: UUID du propriétaire du profil

    Returns:
        dict: Données de profil nettoyées
    """
    is_owner = (current_user_id == profile_user_id)

    # Champs toujours publics
    public_fields = [
        "niveau",
        "xp",
        "badges",
        "competences",
        "current_streak",
        "best_streak",
        "quiz_completed",
        "perfect_quiz_count",
    ]

    # Champs privés (seulement pour le propriétaire)
    private_fields = [
        "recommandations",
        "analyse_detaillee",
        "historique_activites",
        "preferences",
        "objectifs",
        "motivation",
        "energie",
        "statistiques",
    ]

    if is_owner:
        # Le propriétaire voit tout (sauf UUID exposé)
        cleaned = {k: v for k, v in profile_data.items() if k not in ["id", "_id"]}
        # Remplacer l'UUID par un flag
        cleaned["is_me"] = True
    else:
        # Les autres voient seulement les champs publics
        cleaned = {
            k: v for k, v in profile_data.items()
            if k in public_fields
        }
        cleaned["is_me"] = False

    # Toujours masquer l'UUID utilisateur (utiliser username à la place)
    cleaned.pop("utilisateur_id", None)

    return cleaned


def anonymize_leaderboard_entry(entry: dict, current_username: str) -> dict:
    """
    Anonymise une entrée de leaderboard.

    Args:
        entry: L'entrée du leaderboard
        current_username: Username de l'utilisateur connecté

    Returns:
        dict: Entrée anonymisée
    """
    # Retirer l'UUID si présent
    anonymized = {k: v for k, v in entry.items() if k not in ["id", "utilisateur_id", "user_id"]}

    # Ajouter un flag pour identifier l'utilisateur connecté
    anonymized["is_me"] = (entry.get("username") == current_username)

    return anonymized

